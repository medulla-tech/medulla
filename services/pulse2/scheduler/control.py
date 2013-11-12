# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

""" Main dispatching of scheduler """

import random

from twisted.internet.defer import Deferred, maybeDeferred, DeferredList
from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.types import MscContainer, Circuit, CC_STATUS 
from pulse2.scheduler.analyses import MscQueryManager
from pulse2.scheduler.launchers_driving import RemoteCallProxy
from pulse2.scheduler.queries import get_cohs, is_command_in_valid_time
from pulse2.scheduler.queries import process_non_valid, get_ids_to_start
from pulse2.scheduler.queries import is_command_finished, get_cohs_with_failed_phase
from pulse2.scheduler.cleanup import CleanUpSchedule, Defaults

Defaults().setup()

class MethodProxy(MscContainer):
    """ Interface to dispatch the circuit operations from exterior. """

    def start_commands(self, cmds=[]):
        """
        Starts all or selected commands.

        @param cmd_ids: list of commands ids
        @type cmd_ids: list
        """
        self.logger.info("start_commands: %s" % str(cmds))

        scheduler = self.config.name

        if len(cmds) > 0 : 
            for cmd_id in cmds :
                if is_command_in_valid_time(cmd_id):
                    cohs = get_cohs(cmd_id, scheduler)
                    
                    active_circuits = self.get_active_circuits(cohs)
                    
                    active_cohs = [c.id for c in active_circuits]
                    new_cohs = [id for id in cohs if id not in active_cohs]

                    self.start_all(new_cohs, True)

                    for circuit in active_circuits :
                        self.logger.info("Circuit #%s: start" % circuit.id)
                        # set the next_launch_date for now
                        circuit.qm.coh.reSchedule(0, False)
                        circuit.qm.coh.setStateScheduled()
 
        
    def stop_commands(self, cohs=[]):
        """
        Stops all or selected circuits.

        @param cohs: list of commands_on_host
        @type cohs: list
        """
 
        cohs = [int(c) for c in cohs]
        circuits = self.get_active_circuits(cohs)
        for circuit in circuits :
            self.logger.info("Circuit #%s: stopping" % circuit.id)
            circuit.qm.coh.setStateStopped()
            circuit.release()
            # TODO - give up ?

 
    def run_proxymethod(self, launcher, id, name, args):
        """
        Calls the proxy method.
        
        This call is invoked by proxy processing the parsing results 
        from the launcher. 
        Invoked method tagged as @launcher_proxymethod 
        
        @param launcher: launcher which calls this method
        @type launcher: str

        @param id: commands_on_host id
        @type id: int

        @param args: argumets of called method
        @type args: list

        """
        circuit = self.get(id)
        if not circuit :
            if id in [c.id for c in self.get_valid_waitings()]:
                 circuit = [c for c in self.get_valid_waitings() if c.id == id]
            else :
                 self.logger.debug("Aborted execution of method <%s> (Circuit #%d)" % (name, id))
            return None

        if hasattr(circuit.running_phase, "proxy_methods"):
            px_dict = getattr(circuit.running_phase, "proxy_methods")
            if name in px_dict :
                method_name = px_dict[name].__name__
                method = px_dict[name]
                self.logger.debug("Incoming result from launcher <%s>,executing method <%s> from phase <%s>" %
                            (launcher, method_name, circuit.running_phase.name))
                result = method(circuit.running_phase, args)
                circuit.phase_process(result)
                return "OK"


class MscDispatcher (MscQueryManager, MethodProxy):
    """Core of scheduler """
            
    def start_all(self, ids, truncate=False):
        """
        A starting point of the workflow.

        @param ids: list of ids (commands_on_host) to start.
        @type ids: list

        """
        d1 = d2 = Deferred()

        already_initialized_ids = [c.id for c in self.waiting_circuits 
                                        if c.id in ids and c.initialized
                                  ]
        
        new_ids = [id for id in ids if not id in already_initialized_ids]

        if truncate and len(new_ids) > 2 * self.free_slots :
            
            self.logger.info("Number of new circuits was truncated from %d to %d" %
                    (len(new_ids), 2 * self.free_slots))
            new_ids = new_ids[:2*self.free_slots]
            self.logger.info("Remaining circuits will be requested soon")

        if len(new_ids) > 0 :
            d1 = self._setup_all(new_ids)
            d1.addCallback(self._assign_launcher)
            d1.addCallback(self._class_all)
            d1.addCallback(self._revolve_all)
            d1.addCallback(self._run_all)
            d1.addErrback(self._start_failed)
        if len(already_initialized_ids) > 0 :
            d2 = maybeDeferred(self._consolidate, already_initialized_ids)
            d2.addCallback(self._class_all)
            d2.addCallback(self._revolve_all)
            d2.addCallback(self._run_all)
            d2.addErrback(self._start_failed)

        return DeferredList([d1, d2])


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
            if id in self :
                circuit = self.get(id)
                self._run_one(circuit)
            else :
                wf = Circuit(id, self.installed_phases, self.config)
                wf.install_dispatcher(self)
                d = wf.setup()
                dl.append(d)

        return DeferredList(dl)

    def _run_one(self, circuit):
        """
        Executes the circuit in the thread.

        @param circuit: circuit to run
        @type circuit: Circuit

        @return: start result
        @rtype: Deferred
        """
 
        d = deferToThread(circuit.run)
        @d.addErrback
        def eb(reason):
            self.logger.error("Circuit #%s: start failed: %s" % (circuit.id, reason))
        return d

    # looping call reference
    loop = None

    def _run_later(self, circuits):
        """
        Starts the each circuit with a predefined delay.

        This periodic call avoids a saturation on the server (i.e. launcher).
        @param circuits: circuits to start
        @type circuits: iterator
        """
        try :
            circuit = next(circuits)
            self._run_one(circuit)
        except StopIteration :
            self.loop.stop()

    def _run_all(self, circuits):
        """
        Executes all the circuits.

        @param circuits: circuits to run
        @type circuits: list

        @return: list of start results
        @rtype: list
        """
        try :
            self._circuits.extend(circuits)
            self.loop = LoopingCall(self._run_later, iter(circuits))
            self.loop.start(self.config.emitting_period)
            return True

        except Exception, e :
            self.logger.error("Circuits start failed: %s" % str(e))
            return False

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
                self.logger.warn("Circuit #%s: setup failed" % circuit.id)

            yield circuit

 
    def _assign_launcher(self, incoming_circuits):
        """
        Assigning the launcher provider favorizing the best launcher.

        @param incoming_circuits: circuits to start 
        @type incoming_circuits: DeferredList results

        @return: circuits to start with assigned launcher provider
        @rtype: list
        """
        for circuit in self._setup_check(incoming_circuits):
            if self.launchers_provider.single_mode :
                launcher = self.config.launchers.keys()[0]
                circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri, 
                                                             launcher)
            else :
                launchers = self.get_launchers_by_network(circuit.network_address)
                if len(launchers) > 0 :
                    circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri, 
                                                                 launchers[0])
                    self.logger.debug("Circuit #%s: assigned launcher <%s>" % 
                            (circuit.id, launchers[0]))
                else:
                    launcher = self.config.launchers.keys()[0]
                    circuit.launchers_provider = RemoteCallProxy(self.config.launchers_uri, 
                                                                 launcher)
                    self.logger.debug("Launcher pre-detect failed, assigning the first launcher '%s' to circuit #%s" % 
                                  (launcher, circuit.id))
            yield circuit

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
        circuits_to_start = []
        for circuit in incoming_circuits :
            circuit.status = CC_STATUS.WAITING
            new_circuits.append(circuit)

        grouped = self._select_balanced(new_circuits)

        for group, total in grouped.items() :
            circuits_to_run = []

            count = 0 # FIXME - need really ?
            for circuit in [c for c in new_circuits if c.network_address==group] :
                if circuit.network_address == group :
                    if count == total :
                        break
                    # include a new circuit to running container
                    circuit.status = CC_STATUS.ACTIVE
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

                to_add = dict((group, 0) for group in self.groups)# if group in new_grps)

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
            if len(ids) > 0 :
                circuit = self.get(ids[0])
                if circuit :
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
    
        running = self._analyze_groups(self.circuits)
        remaining = self._analyze_groups(self.waiting_circuits)
 
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

        return False


    def launch_remaining_waitings(self, reason):
        """ Calls the next waiting circuit. """
        while self.free_slots > 0 :
            started_next = self.launch_next_waiting()
            if not started_next :
                break

    def process_non_valid(self, result):
        """
        Calls the database method checking overtimed circuits and removes
        them from internal container.

        @return: list of commands to check to clean up
        @rtype: list
        
        """
        commands_to_cleanup_check = []
        for id in process_non_valid(self.config.name, 
                                    self.config.max_to_overtimed, 
                                    self.config.non_fatal_steps):
            circuit = self.get(id)
            if circuit :
                if not circuit.cmd_id in commands_to_cleanup_check :
                    commands_to_cleanup_check.append(circuit.cmd_id)
                circuit.release()
        return commands_to_cleanup_check

    def check_for_clean_up(self, commands_to_cleanup_check):
        """
        Checks if commands to check are already finished.

        @param commands_to_cleanup_check: list of commands
        @type commands_to_cleanup_check: list
        """
        for cmd_id in commands_to_cleanup_check:
            if is_command_finished(self.config.name, cmd_id):
                self.set_ready_to_cleanup(cmd_id)

    def clean_up(self, result):
        """ Calls the clean up scheduler if commands are candidats. """

        cohs = []
        for cmd_id in self.ready_candidats_to_cleanup :

            cohs.extend(get_cohs_with_failed_phase(cmd_id, "execute"))
            del self.candidats_to_cleanup[cmd_id]
        if len(cohs) > 0 :
            schedule = CleanUpSchedule(cohs)
            schedule.process()

    def awake_waiting_overtimed(self, result):
        """Looks for zombies circuits in waitings and releases them """
        circuits = self._get_candidats_to_overtimed(self.waiting_circuits)
        for circuit in circuits :
            circuit.release()


 
    def mainloop(self):
        """ The main loop of scheduler """
        d = maybeDeferred(self._mainloop)
        d.addCallback(self.process_non_valid)
        d.addCallback(self.check_for_clean_up)
        d.addCallback(self.clean_up)
        d.addCallback(self.launch_remaining_waitings)
        d.addCallback(self.awake_waiting_overtimed)
        d.addErrback(self.eb_mainloop)

        return d

    def eb_mainloop(self, failure):
        self.logger.error("Mainloop failed: %s" % str(failure))

 
    def _mainloop(self):
        """ The main loop of scheduler """

        self.logger.info("Looking for new commands")
        try :
            self.rn_stats()
            self.wt_stats()

            if self.has_free_slots() : 
                top = self.free_slots * 2
                if top > 0 :

                    starting_ids = [c.id for c in self.circuits if not c.is_running]
                    running_ids = [c.id for c in self.circuits if c.initialized]
                    waiting_ids = [c.id for c in self.get_valid_waitings()]

                    ids_to_exclude = running_ids + waiting_ids + starting_ids

                    ids = get_ids_to_start(self.config.name,
                                           ids_to_exclude, 
                                           top)
                    if len(ids) > 0 :
                        self.logger.info("Prepare %d new commands to initialize" % len(ids))
                    else :
                        self.logger.info("Nothing to initialize")
                        return True

                    self.start_all(ids)
                else :
                    self.logger.info("Slots will be filled with by waiting circuits")
            else :
                self.logger.info("Slots full: continue and waiting on next awake")
            return True

        except Exception, e:
            self.logger.error("Mainloop execution failed: %s" % str(e))
            return True


       
        



