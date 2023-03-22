# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Main dispatching of scheduler """

import random
from base64 import b64decode

from twisted.internet.defer import Deferred, maybeDeferred, DeferredList
from twisted.internet.defer import succeed
from twisted.internet.threads import deferToThread
from twisted.internet import reactor

from pulse2.scheduler.types import MscContainer, Circuit, CC_STATUS
from pulse2.scheduler.analyses import MscQueryManager
from pulse2.scheduler.launchers_driving import RemoteCallProxy
from pulse2.scheduler.queries import get_cohs, is_command_in_valid_time
from pulse2.scheduler.queries import switch_commands_to_start
from pulse2.scheduler.queries import get_ids_to_start, get_commands
from pulse2.scheduler.dlp import get_dlp_method


class MethodProxy(MscContainer):
    """ Interface to dispatch the circuit operations from exterior. """


    def start_commands(self, cmds):
        self.logger.info("Prepare %d commands to START..." % len(cmds))

        scheduler = self.config.name

        if len(cmds) > 0 :
            for cmd_id in cmds :
                if is_command_in_valid_time(cmd_id):
                    cohs = get_cohs(cmd_id, scheduler)
                    self.start_commands_on_host(cohs)
        return True


    def start_commands_on_host(self, cohs):
        """
        Starts selected commands on host.

        @param cmd_ids: list of commands ids
        @type cmd_ids: list
        """
        cmd_ids = get_commands(cohs)
        for cmd_id in cmd_ids :
            self.statistics.watchdog_schedule(cmd_id)
        switch_commands_to_start(cohs)

        self.logger.debug("Cohs %s starting" % cohs)

        active_circuits = [c for c in self._circuits if c.id in cohs]

        active_cohs = [c.id for c in active_circuits]
        new_cohs = [id for id in cohs if id not in active_cohs and not id in self.stopped_track]
        self.logger.info("Starting %s circuits" % len(new_cohs))

        for circuit in active_circuits :
            self.logger.info("Circuit #%s: start" % circuit.id)
            # set the next_launch_date for now
            circuit.cohq.coh.reSchedule(0, False)
            circuit.cohq.cmd.refresh()
        return True


    def stop_commands(self, cohs=[]):
        """
        Stops all or selected circuits.

        @param cohs: list of commands_on_host
        @type cohs: list
        """
        # Mutable list cohs used as default argument to a method or function
        cmd_ids = get_commands(cohs)
        active_circuits = [c for c in self._circuits if c.id in cohs]

        active_cohs = [c.id for c in active_circuits]

        self.logger.info("Prepare %d circuits to STOP ..." % len(active_cohs))
        for cmd_id in cmd_ids:
            # final statistics calculate
            self.statistics.watchdog_schedule(cmd_id)

        self.stopped_track.add(active_cohs)

        for circuit in active_circuits :
            circuit.cohq.coh.refresh()
            circuit.cohq.cmd.refresh()
            circuit.release()


        return True


    def run_proxymethod(self, launcher, id, name, args, from_dlp):
        """
        Calls the proxy method.

        This call is invoked by proxy processing the parsing results
        from the launcher or download provider.
        Invoked method tagged as @launcher_proxymethod

        @param launcher: launcher which calls this method
        @type launcher: str

        @param id: commands_on_host id
        @type id: int

        @param args: argumets of called method
        @type args: list

        @param from_dlp: if True, response is coming from DLP
        @type from_dlp: bool
        """
        circuit = self.get(id)
        if circuit :
            return self._run_proxymethod(launcher, id, name, args, circuit)
        else :
            self.logger.info("probably recurrent phase or stopped circuit #%s" % (id))
            # Recurrent phase parsing which does not exists in the container
            # The circuit is created out of container
            circuit = Circuit(id, self.installed_phases, self.config, from_dlp)
            if not circuit :
                self.logger.warn("Circuit #%s: not found" % id)
                return False
            circuit.install_dispatcher(self)
            d = circuit.setup(True)
            @d.addCallback
            def _setup(result):
                dth = deferToThread(circuit.run)
                return dth
            @d.addCallback
            def _post_setup(result):
                if not circuit.running_phase :
                    self.logger.warn("Method <%s> call for current phase is not valid" % name)
                    return False
                if from_dlp :
                    valid_method_name = get_dlp_method(circuit.running_phase.name)

                    if valid_method_name != name :
                        self.logger.warn("Recurrent phase %s ignored" % name)
                        return False
                dps = maybeDeferred(self._run_proxymethod,
                                    launcher,
                                    id,
                                    name,
                                    args,
                                    circuit)
                @dps.addCallback
                def result_proxy(res):
                    return True

                @dps.addErrback
                def failed_proxy(failure):
                    self.logger.warn("Proxymethod execution failed: %s" % failure)
                    return False
                return dps


            @d.addErrback
            def _eb(result):
                self.logger.warn("Recurrent phase result parsing failed: %s" % result)
                return False
            return d


    def _run_proxymethod(self, launcher, id, name, args, circuit=None):
        """
        Calls the proxy method.

        @param launcher: launcher which calls this method
        @type launcher: str

        @param id: commands_on_host id
        @type id: int

        @param args: argumets of called method
        @type args: list

        @param circuit: Recurrent circuit
        @type circuit: Circuit
        """

        if hasattr(circuit.running_phase, "proxy_methods"):
            px_dict = getattr(circuit.running_phase, "proxy_methods")
            if name in px_dict :
                method_name = px_dict[name].__name__
                method = px_dict[name]
                if not hasattr(circuit.running_phase, method_name):
                    self.logger.debug("Proxymethod %s not found, call aborted" % name)
                    return False

                self.logger.debug("Incoming result from launcher <%s>,executing method <%s> from phase <%s>" %
                            (launcher, method_name, circuit.running_phase.name))
                if len(args) == 3:
                    exitcode, _stdout, _stderr = args
                    stdout = unicode(b64decode(_stdout),'utf-8', 'strict')
                    stderr = unicode(b64decode(_stderr),'utf-8', 'strict')
                    result = method(circuit.running_phase, (exitcode, stdout, stderr))
                else:
                    result = method(circuit.running_phase, args)

                circuit.phase_process(result)
                return True
        return False


    def extend_command(self, cmd_id, start_date, end_date):
        """
        Custom command re-scheduling.

        @param cmd_id: Commands id
        @type cmd_id: int

        @param start_date: new start date of command
        @type start_date: str

        @param end_date: new end date of command
        @type end_date: str
        """
        self.logger.info("re-scheduling command id = <%s> from %s to %s" %
                (cmd_id, start_date, end_date))
        circuits = self.get_circuits_by_command(cmd_id)

        for circuit in circuits :
            circuit.cohq.coh.refresh()
            circuit.cohq.cmd.refresh()

        return True




class MscDispatcher (MscQueryManager, MethodProxy):
    """Core of scheduler """

    def start_all(self, ids, truncate=False):
        """
        A starting point of the workflow.

        @param ids: list of ids (commands_on_host) to start.
        @type ids: list

        """
        d1 = Deferred()

        banned = self.bundles.get_banned_cohs()
        ids = [id for id in ids if id not in banned]

        already_initialized_circuits = [c for c in self._circuits
                                          if c.id in ids
                                       ]
	# already initialized circuits will be started
        aicd = maybeDeferred(self._circuits_activate,
			     already_initialized_circuits)
	aicd.addCallback(self._run_all)
        aicd.addErrback(self._start_failed)

        already_initialized_ids = [c.id for c in already_initialized_circuits]

        new_ids = [id for id in ids if not id in already_initialized_ids]

        if truncate and len(new_ids) > self.free_slots :

            self.logger.info("Number of new circuits was truncated from %d to %d" %
                    (len(new_ids), self.free_slots))
            new_ids = new_ids[:self.free_slots]
            self.logger.info("Remaining circuits will be requested soon")

        if len(new_ids) > 0 :
            d1 = self._setup_all(new_ids)

            d1.addCallback(self._assign_launcher)
            d1.addCallback(self._class_bundles)
            d1.addCallback(self._class_all)
            d1.addCallback(self._revolve_all)
            d1.addCallback(self._run_all)
            d1.addErrback(self._start_failed)
            return d1
        else:
            succeed(True)


    def _circuits_activate(self, circuits):
        """
        Activates already initialized circuits.

        @param circuits: list of circuits to activate
        @type circuits: list
        """
        for circuit in circuits :
            circuit.status = CC_STATUS.ACTIVE
            circuit.cohq.coh.refresh()
            self.logger.info("Circuit #%s: reactivate" % (circuit.id))

        return circuits


    def _consolidate(self, already_initialized_ids):
        """
        Gets all circuits (active+waiting) to restart.

        @param already_initialized_ids: ids of circuits
        @type already_initialized_ids: int

        @return: circuits to restart
        @rtype: list
        """
        waiting_circuits = self.get_waiting_circuits(already_initialized_ids)
        circuits = self.get_circuits(already_initialized_ids)
        circuits.extend(waiting_circuits)
        return circuits

    def _start_failed(self, failure):
        """
        Errorback to starting of lot of circuits.

        @param failure: reason of failure
        @type failure: twisted failure
        """
        self.logger.error("Circuit start failed: %s" % failure)


    def _setup_all(self, ids):
        """
        Initializing of all the circuits.

        @param ids: circuits ids
        @type ids: int

        @return: list of setup results
        @rtype: DeferredList
        """
        dl = []
        for id in ids :
            if self.kill_all:
                self.logger.debug("Dispatcher killed")
                return DeferredList(dl)

            if any([True for c in self._circuits if c.id == id]):
                circuit = self.get(id)
                if circuit.initialized :
                    deferToThread(circuit.run)
                else :
                    circuit.install_dispatcher(self)
                    d = circuit.setup()
                    dl.append(d)
            else :
                d = maybeDeferred(self._circuit_pre_setup, id)
                d.addCallback(self._circuit_setup)
                @d.addErrback
                def _err(failure):
                    self.logger.error("Circuit pre-setup failed: %s" % failure)
                dl.append(d)
        return DeferredList(dl)


    def _circuit_pre_setup(self, id):
	"""
	Circuit pre-setup step.

	This method encapsuled as deferred avoids to go directly on the setup
	without terminating all the operations in the Circuit's constructor,
	especialy the creation oh CohQuery object needed for setup.

	@param id: circuit id
        @type id: int

        @return: initialized Circuit object
        @rtype: Circuit
        """
        circuit = Circuit(id, self.installed_phases, self.config)
        circuit.install_dispatcher(self)
        return circuit


    def _circuit_setup(self, circuit):
	"""
	Final circuit's setup step.

        @param circuit: initialized Circuit object
        @type circuit: Circuit

        @return: deferred containing circuit's instance ready to run
        @rtype: Deferred
	"""
        return circuit.setup()


    def _run_all(self, circuits):
        """
        Executes all the circuits.

        @param circuits: circuits to run
        @type circuits: list

        @return: list of start results
        @rtype: list
        """
	return self.loop_starter.run(circuits)



    def get_launchers_by_network(self, network):
        """
        Pre-detect the nearest launcher for the machine.

        @param network: network address of machine assigned on this circuit
        @type network: str

        @return: list of the best launchers
        @rtype: list
        """
        return [launcher for (launcher, networks) in self.launchers_networks.items()
                         if network in networks]


    def _setup_check(self, circuits):
        """
        Checks the setup result and transforms its to simple list (generator).

        @param circuits: circuits to check
        @type circuits: DeferredList results

        @return: checked circuits:
        @rtype: generator
        """
        for success, circuit in circuits :
            if not success :
                self.logger.warn("Circuit setup failed")
            if not isinstance(circuit, Circuit):
                self.logger.warn("Circuit setup failed - not Circuit instance")
		continue
            yield circuit


    def _assign_launcher(self, incoming_circuits):
        """
        Assigning the launcher provider favorizing the best launcher.

        @param incoming_circuits: circuits to start
        @type incoming_circuits: DeferredList results

        @return: circuits to start with assigned launcher provider
        @rtype: list
        """
        circuits = []

        for circuit in self._setup_check(incoming_circuits):
            if self.launchers_provider.single_mode :
                launcher = self.config.launchers.keys()[0]
                circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri,
                                                             self.slots,
                                                             launcher)
            else :
                launchers = self.get_launchers_by_network(circuit.network_address)
                if len(launchers) > 0 :
                    circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri,
                                                                 self.slots,
                                                                 launchers[0])
                    self.logger.debug("Circuit #%s: assigned launcher <%s>" %
                            (circuit.id, launchers[0]))
                else:
                    launcher = self.config.launchers.keys()[0]
                    circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri,
                                                                 self.slots,
                                                                 launcher)
                    self.logger.debug("Launcher pre-detect failed, assigning the first launcher '%s' to circuit #%s" %
                                  (launcher, circuit.id))
            circuits.append(circuit)
        return circuits

    def _class_bundles(self, incoming_circuits):
        """
        Adds the bundled circuits into the bundle tracking.

        @param incoming_circuits: circuits to start
        @type incoming_circuits: list
        """
        for circuit in incoming_circuits :
            self.bundles.update(circuit)

        return incoming_circuits


    def _class_all(self, incoming_circuits):
        """
        Classing of all incoming circuits.

        Based on statistics of running circuits (see _select_balanced),
        this treatement ensures the balanced execution of favorized circuits
        and remaining circuits temporarily saves into a queue.

        @param incoming_circuits: circuits to class
        @type incoming_circuits: deferred list
        """
        new_circuits = []
        banned = self.bundles.get_banned_cohs()
        circuits_to_start = []
        for circuit in incoming_circuits :
            circuit.status = CC_STATUS.WAITING
            new_circuits.append(circuit)

        grouped = self._select_balanced(new_circuits)

        for group, total in grouped.items() :
            circuits_to_run = []

            count = 0
            for circuit in [c for c in new_circuits if c.network_address==group] :

                # bundle banned excluding
                if circuit.id in banned:
                    self.logger.info("Circuit #%s is part of bundle, still waiting" % circuit.id)
                    continue
                if not circuit.cohq.cmd.inDeploymentInterval():
                    circuit.release()
                    continue
                if self.contains_running_target(circuit):
                    # if another deployment running on the same machine
                    continue
                if circuit.network_address == group :
                    if count == total :
                        break
                    # include a new circuit to running container
                    circuit.status = CC_STATUS.ACTIVE
                    self.started_track.add([circuit.id])
                    circuits_to_run.append(circuit)
                    new_circuits.remove(circuit)
                    count += 1


            circuits_to_start.extend(circuits_to_run)


        # rest of new circuits in queue
        new_circuits = [c for c in new_circuits if c not in self.waiting_circuits]

        self._circuits.extend(new_circuits)
        self.logger.info("Circuits stats: running: %d waiting: %d" %
                (len(self.circuits), len(self.waiting_circuits)))

        return circuits_to_start

    def _revolve_all(self, circuits_to_start):
        """ Randomizing the deployment orders by group """

        final_length = len(circuits_to_start)
        circuits_by_groups = {}
        for group in self.groups :
            content = [c for c in circuits_to_start if c.network_address==group]
            random.shuffle(content)

            circuits_by_groups[group] = content

        circuits = []
        while True :
            if len(circuits) == final_length:
                break
            for group in self.groups :
                try :
                    c = circuits_by_groups[group].pop(0)
                    circuits.append(c)
                except IndexError:
                    continue

        return circuits


    def _select_balanced(self, new_circuits):
        """
        Equalizing the circuits by groups.

        Based on statistics of running circuits, this routine calculates
        the number of new circuits to execute on slihghtests groups.
        Goal is the equalized load balancing to avoid saturate some networks
        more than others.
        Final number of new_circuits, together with running circuits,
        covers the maximum of running circuits (max_slots).

        @param new_circuits: new circuits to equalize
        @type new_circuits: list

        @return: number of circuits per existing groups.
        @rtype: dict
        """

        # sorted statistics from circuits to add
        new_grps_stat = self._analyze_groups(new_circuits)
        # sorted statistics from running circuits
        running_grps_stat = self._analyze_groups(self.circuits)

        to_add = None

        if len(self.circuits) < self.max_slots :
            # number of new circuits to add
            free_slots = self.max_slots - len(self.circuits)

            if  len(self.circuits) + len(new_circuits) <= self.max_slots :
                return new_grps_stat
            else :

                to_add = dict((group, 0) for group in self.groups)

                zero_blacklist = []
                while True :

                    masked = dict((group, value + to_add[group])
                                    for (group, value) in running_grps_stat.items()
                                    if group not in zero_blacklist)
                    # group having minimum circuits
                    min_key = min(masked, key=masked.get)
                    if new_grps_stat[min_key] > 0 :
                        to_add[min_key] += 1
                        new_grps_stat[min_key] -= 1
                    else :
                        zero_blacklist.append(min_key)

                    if sum(to_add.values()) == free_slots :
                        break
        else :
            return dict((g, 0) for g in self.groups)

        return to_add



    def release(self, id, suspend_to_waitings=False):
        """
        Circuit releasing from container.

        Called typicaly when last phase ends or overtimed.

        @param id: commands_on_host id
        @type id: int
        """
        reactor.callFromThread(self._release_and_launch_next,
                               id,
                               suspend_to_waitings)


    def _release_and_launch_next(self, id, suspend_to_waitings=False):
        self._release(id, suspend_to_waitings)
        try:
            self.launch_next_waiting()
        except Exception, e:
            self.logger.error("Next circuit launching failed: %s" % str(e))

    def _get_next_waiting(self, circuits, slightest_network):
        """
        Selects a next candidate to launch.

        @param circuits: proposed circuits
        @type circuits: list

        @param slightest_network: group with the minimum running circuits
        @type slightest_network: str

        @return: next circuit to start
        @rtype: Circuit

        """
        if len(circuits) > 0 :
            ids = [c.id for c in circuits if c.network_address==slightest_network]

            # queued bundled circuits to exclude
            banned = self.bundles.get_banned_cohs()
            for id in ids :
                if id in banned :
                    continue

                # do not start a stopped circuit
	        if id in self.stopped_track:
	            circuit = self.get(id)
                    if circuit :
	                circuit.release()
 	            continue

                circuit = self.get(id)
                if circuit :
                    if self.contains_running_target(circuit):
                        # if another deployment running on the same machine
                        continue

                    self.logger.info("Circuit #%s: (group %s) is going to start" %
                            (circuit.id, slightest_network))
                    circuit.status = CC_STATUS.ACTIVE
                    return circuit
        return None

    def launch_next_waiting(self):
        """
        Launch the next candidate to start.

        The choice of next circuit is based on statistics of running circuits.
        Like on start, goal is selecting a circuit destinated to a computer
        which is located at least saturated network.
        """
        try:
            running = self._analyze_groups(self.circuits)
            remaining = self._analyze_groups(self.get_valid_waitings())

            for _ in xrange(self.nbr_groups):
                # the least saturated network
                 slightest_group = min(running, key=running.get)
                 if remaining[slightest_group] > 0 :
                     # waiting circuits not processed yet
                     unprocessed_circuits = self.get_unprocessed_waitings()
                     # waiting circuits already processed (recycling of failed attempts)
                     already_treated_circuits = self.get_valid_waitings()

                     for circuits in [unprocessed_circuits, already_treated_circuits]:
                         if self.has_free_slots():
                             circuit = self._get_next_waiting(circuits, slightest_group)
                             if circuit :
                                 circuit.run()
                                 return True
                         else:
                             return False

                 else :
                     if slightest_group in running :
                         del running[slightest_group]
                     # if not a candidate in waiting circuits, skip on next group
                     continue
            if len(self.get_valid_waitings()) > 0 :
                circuit = self.get_valid_waitings()[0]
                if circuit :
                    self.logger.debug("Remaining waiting circuit #%s: start" % circuit.id)
                    circuit.status = CC_STATUS.ACTIVE
                    circuit.run()
                    self.started_track.add([circuit.id])
                    return True
            return False
        except Exception, e:
            self.logger.error("\033[31mnext circuit exec failed: %s\033[0m" % str(e))


    def launch_remaining_waitings(self, reason):
        """ Calls the next waiting circuit. """
        while True:
            #self.logger.debug("Looking for remaining circuits...")
            self.logger.info("Looking for remaining circuits...")
            if not self.has_free_slots():
                break
            started_next = self.launch_next_waiting()
            if not started_next :
                break
            else :
                self.logger.debug("Next circuit started")

    def update_stats(self, result):
        """ Update of global statistics of all valid running commands """
        self.statistics.update()

        self.logger.debug("Command stats - %s" % self.statistics.stats)

        b_ids = self.get_all_running_bundles()
        self.logger.debug("Bundles to hold: %s" % str(b_ids))
        self.bundles.clean_up_remaining(b_ids)


    def remove_expired(self, reason):
	"""Freezed circuits clean up"""
	exp_ids = self.started_track.get_expired()
	for id in exp_ids:
	    circuit = self.get(id)
	    if circuit:
	        if circuit.status == CC_STATUS.ACTIVE:
                    self.logger.warn("Circuit #%s: EXIPRED -> REMOVED!" % id)
                    circuit.release()
                    self.started_track.remove(id)


    def unlock_when_empty(self, reason):
        """Unlocks empty startloops """
        if self.lock_start.locked and len(self.circuits)==0:
            self.lock_start.release()
            self.logger.info("Previous batch unlocked")


    def mainloop(self):
        """ The main loop of scheduler """
        d = maybeDeferred(self._mainloop)
        #d.addCallback(self.launch_remaining_waitings)
        d.addCallback(self.update_stats)
        d.addCallback(self.remove_expired)
        #d.addCallback(self.unlock_when_empty)
        d.addErrback(self.eb_mainloop)

        return d

    def eb_mainloop(self, failure):
        self.logger.error("Mainloop failed: %s" % str(failure))


    def _mainloop(self):
        """ The main loop of scheduler """

        self.logger.debug("Looking for new commands")
        try :
            self.rn_stats()
            self.wt_stats()

            self.logger.debug("Number of tracked/stopped circuits: %d" % len(self.stopped_track))

            if self.lock_start.locked:
                self.logger.info("Previous batch not finished, skiping")
                return True

            if self.has_free_slots():
                top = self.free_slots
                if top > 0 :

                    starting_ids = [c.id for c in self.circuits if not c.is_running]
                    running_ids = [c.id for c in self.circuits if c.initialized]
                    waiting_ids = [c.id for c in self.get_valid_waitings()]

                    ids_to_exclude = running_ids + waiting_ids + starting_ids

                    # Looking for new commands
                    ids = get_ids_to_start(self.config.name,
                                           ids_to_exclude,
                                           top)

                    if len(ids) > 0 :
                        self.logger.info("Prepare %d new commands to initialize" % len(ids))
                    else :
                        self.logger.debug("Nothing to initialize")
                        return True

                    # starting of all ids will be locked until the start
                    # of last circuit launching
                    dstart = self.lock_start.run(self.start_all, ids)

                    @dstart.addCallback
                    def _cb(reason):
                        self.logger.info("Batch completed, ready for next.")
                    @dstart.addErrback
                    def _eb(reason):
                        self.logger.info("Start batch failed! : %s" % reason)


                else :
                    self.logger.info("Slots will be filled with by waiting circuits")
            else :
                self.logger.info("Slots full: continue and waiting on next awake")
            return True

        except Exception, e:
            self.logger.error("Mainloop execution failed: %s" % str(e))
            return True
