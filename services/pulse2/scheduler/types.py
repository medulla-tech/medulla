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

""" 
Definitions of base types of scheduler. 

Atomic structure / relationships:

<MscDispatcher> (inherited from <MscContainer>) is the core of scheduler.
Internal container stocks at least one <Circuit> instance which represents 
in database model one record in commands_on_host table.

<MscDispatcher> provides all the operations trough the circuits
and communicates with these external services :
    - outgoing requests on launchers
    - incoming responses from launchers (on push_pull mode)
    - incoming requests from mmc-agent

<Circuit> represents the workflow with custom steps personnalized 
on creation. One circuit is destinated on one target (machine)

<Phase> represents a step of circuit, which can be an action
doing something on target.
"""

import logging
import inspect
import time

from twisted.internet.defer import Deferred, maybeDeferred

from pulse2.consts import PULSE2_SUCCESS_ERROR
from pulse2.utils import SingletonN, extractExceptionMessage
from pulse2.network import NetUtils
from pulse2.scheduler.queries import CoHQuery, any_failed
from pulse2.scheduler.utils import chooseClientInfo
from pulse2.scheduler.launchers_driving import RemoteCallProxy
from pulse2.scheduler.checks import getAnnounceCheck
from pulse2.scheduler.utils import getClientCheck, getServerCheck
from pulse2.scheduler.stats import StatisticsProcessing
from pulse2.scheduler.bundles import BundleReferences
from pulse2.scheduler.timeaxis import LaunchTimeResolver

from pulse2.database.msc.orm.commands_history import CommandsHistory


def enum(*args, **kwargs):
    """
    Returns a named enumerator based on simple list of integers.

    @param *args: list of names of constants to create
    @type *args: list 
    """
    return type('Enum', 
                (), 
                dict((y, x) for x, y in enumerate(args), **kwargs)
               ) 

# List of phase actions 
DIRECTIVE = enum("GIVE_UP", 
                 "PERFORM", 
                 "NEXT", 
                 "OVER_TIMED",
                 "FAILED",
                 "STOPPED",
                 "KILLED",
                 )
# status of circuit
CC_STATUS = enum("ACTIVE",
                 "WAITING",
                 "RECURRENT",
                 )


class PhaseProxyMethodContainer(object):
    """
    Identification of methods tagged by launcher_proxymethod decorator.

    Each phase checks occurences the tagged methods and registers them
    to internal dictionnary (_proxy_methods).
    This methods represents an interface for incoming responses 
    from launchers. 
    """

    _register_only = False
    _proxy_methods = {}


    @property
    def proxy_methods(self):
        """Returns all proxy methods of phase"""
        return self._proxy_methods

    def register(self):
        """Registers all proxymethods in inherited Phase class"""
        self._register_only = True
        for name in dir(self) :
            fnc = getattr(self, name)

            if not hasattr(fnc, "is_proxy_fnc"): continue
            if not callable(fnc) : continue
            if fnc.is_proxy_fnc :
                args, vargs, kwds, defaults = inspect.getargspec(fnc)
                fnc(self, *args)


        self._register_only = True
 
        
class PhaseBase (PhaseProxyMethodContainer):
    """A base frame of phase """

    # name of phase
    name = None
    state_name = None


    # commands_on_host record
    coh = None
    # commands record
    cmd = None
    # target record
    target = None
    # phase record
    phase = None

    # hostname or IP address of target
    host = None

    # reference to RemoteCallProxy providing the communication with launchers
    launchers_provider = None
    # shortcut to main MscContainer
    dispatcher = None

    last_activity_time = None

    def __init__(self, cohq, host, config):
        """
        @param cohq: database reference
        @type cohq: CoHQuery 

        @param host: hostname or IP address
        @type host: str

        """
        self.register()
        
        self.logger = logging.getLogger()
        self.host = host
        if cohq:
            self.set_cohq(cohq)
        self.config = config

    def set_cohq(self, cohq):
        """
        CoHQuery setter.

        @param cohq: database reference
        @type cohq: CoHQuery 
        """

        if not isinstance(cohq, CoHQuery):
           raise TypeError("Not CoHQuery type")

        self.coh = cohq.coh
        self.cmd = cohq.cmd
        self.target = cohq.target

        self.phase = cohq.get_phase(self.name)

    def _apply_initial_rules(self):
        """
        Checks the phase states and decides on next behavoir.

        @return: action or state of phase 
        @rtype: DIRECTIVE
        """
        if self.coh.isStateStopped():
            self.logger.info("Circuit #%s: Stop"  %self.coh.id)
            return DIRECTIVE.STOPPED
        if not self.cmd.in_valid_time(): 
            return DIRECTIVE.OVER_TIMED
 
        if self.coh.is_out_of_attempts() and self.phase.is_failed():
            self.coh.setStateFailed()
            return DIRECTIVE.KILLED
 
        self.logger.debug("Circuit #%s: %s phase" % (self.coh.id, self.name))

        if self.phase.is_done(): 
            # phase has already already done, jump to next phase
            self.logger.debug("command_on_host #%s: %s done" % (self.coh.id, self.name))
            return self.next()
        if self.phase.is_running(): 
            # phase still running, immediately returns, do nothing
            self.logger.debug("command_on_host #%s: %s still running" % (self.coh.id, self.name))
        return DIRECTIVE.PERFORM

    def _switch_on(self):
        """Phase is ready to run, let's go !"""
        self.phase.set_running()
        if not self.state_name :
            self.state_name = self.name
        self.update_history_in_progress()
        return DIRECTIVE.PERFORM


    def apply_initial_rules(self):
        """
        Checks the phase states and decides on next behavoir.

        @return: action or state of phase 
        @rtype: DIRECTIVE
        """
        ret = self._apply_initial_rules()
        if ret not in (DIRECTIVE.NEXT,
                       DIRECTIVE.GIVE_UP, 
                       DIRECTIVE.KILLED,
                       DIRECTIVE.STOPPED,
                       DIRECTIVE.OVER_TIMED) :
            return self._switch_on()
        return ret


    def run(self):
        """ 
        Method to be overriden, but always returning perform() method.
        
        Contains usually a command state checks and eventual shortcuts
        to final or give_up phases.

        """
        try:
            if self.apply_initial_rules():
                return self.coh
        except Exception, e:
            self.logger.error("Flags or rules failed: %s"  % str(e))
        return self.perform()

    def perform(self):
        pass

    def next(self):
        return DIRECTIVE.NEXT 

    def give_up(self):
        """ Releasing the circuit. """
        raise NotImplementedError

    def failed(self):
        raise NotImplementedError

class Phase (PhaseBase):
    """ Main phase frame providing all the actions"""

    def got_error_in_error(self, failure):
        """
        An errorback called if an error occured in an error response.

        @param failure: reason of error
        @type failure: twisted failure 
        """

        logging.getLogger().error("Circuit #%s: got an error within an error: %s" %
                (self.coh.id, extractExceptionMessage(failure)))
        return self.give_up()

    def update_history_in_progress(self, 
                            error_code = PULSE2_SUCCESS_ERROR, 
                            stdout = '',
                            stderr = ''):
        """
        Logging the MSC activity - switch the state to running.

        @param error_code: returned error code
        @type error_code: int

        @param stdout: remote command output
        @type stdout: str

        @param stderr: remote command error output
        @type stderr: str
        """
        self._update_history("running", error_code, stdout, stderr)

    def update_history_done(self, 
                            error_code = PULSE2_SUCCESS_ERROR, 
                            stdout = '',
                            stderr = ''):
        """
        Logging the MSC activity - switch the state to done.

        @param error_code: returned error code
        @type error_code: int

        @param stdout: remote command output
        @type stdout: str

        @param stderr: remote command error output
        @type stderr: str
        """
        self._update_history("done", error_code, stdout, stderr)

    def update_history_failed(self, 
                            error_code = PULSE2_SUCCESS_ERROR, 
                            stdout = '',
                            stderr = ''):
        """
        Logging the MSC activity - switch the state to failed.

        @param error_code: returned error code
        @type error_code: int

        @param stdout: remote command output
        @type stdout: str

        @param stderr: remote command error output
        @type stderr: str
        """
        self._update_history("failed", error_code, stdout, stderr)


    def _update_history(self, state, error_code, stdout, stderr):
        """
        Logging the MSC activity.

        @param error_code: returned error code
        @type error_code: int

        @param stdout: remote command output
        @type stdout: str

        @param stderr: remote command error output
        @type stderr: str
        """
        encoding = self.config.dbencoding
        history = CommandsHistory()
        history.fk_commands_on_host = self.coh.id
        history.date = time.time()
        history.error_code = error_code
        history.stdout = stdout.encode(encoding, 'replace')
        history.stderr = stderr.encode(encoding, 'replace')
        history.phase = self.name
        history.state = state
        history.flush()

    def get_client(self, announce):
        client_group = ""
        if self.host :

            for pref_net_ip, pref_netmask in self.config.preferred_network :
                if NetUtils.on_same_network(self.host, pref_net_ip, pref_netmask):

                    client_group = pref_net_ip
                    break
        else :
            if len(self.config.preferred_network) > 0 :
                (pref_net_ip, pref_netmask) = self.config.preferred_network[0] 
                client_group = pref_net_ip 
            

        return {'host': self.host, 
                'uuid': self.target.getUUID(), 
                'maxbw': self.cmd.maxbw, 
                'protocol': 'ssh', 
                'client_check': getClientCheck(self.target), 
                'server_check': getServerCheck(self.target), 
                'action': getAnnounceCheck(announce), 
                'group': client_group
               }

    def give_up(self):
        """
        Encapsulates give-up directive.

        @return: give-up directive
        @rtype: DIRECTIVE
        """
        self.logger.debug("Circuit #%s: Releasing" % self.coh.id)
        if self.coh.isStateStopped():
            return DIRECTIVE.STOPPED
        else :
            return DIRECTIVE.GIVE_UP

    def failed(self):
        """
        Encapsulates failed directive.

        @return: failed directive
        @rtype: DIRECTIVE
        """
        return DIRECTIVE.FAILED

    def switch_phase_failed(self, decrement=True):
        """
        Toggles phase to failed.

        @param decrement: decrements the number of failed attempts
        @type decrement: bool
        """
        ltr = LaunchTimeResolver(start_date=self.coh.start_date,
                                 end_date=self.coh.end_date,
                                 attempts_failed=self.coh.attempts_failed,
                                 attempts_left=self.coh.attempts_left,
                                 max_wol_time=self.config.max_wol_time,
                                 deployment_intervals=self.cmd.deployment_intervals,
                                 now=time.time()
                                 )

        self.coh.reSchedule(ltr.get_launch_date(), decrement)
        
        self.phase.switch_to_failed()
        if self.coh.is_out_of_attempts():
            logging.getLogger().info("Circuit #%s: failed" % (self.coh.id))
            self.coh.setStateFailed()
            return DIRECTIVE.KILLED
        return self.failed() 
           
    def parse_order(self, name, taken_in_account):
        """
        Resolves if remote call on push_pull mode is successfull.

        @param name: name of phase
        @type name: str

        @param taken_in_account: if True, order successfully stacked
        @type taken_in_account: bool
        """
        if taken_in_account: # success
            self.update_history_in_progress()
            self.logger.info("Circuit #%s: %s order stacked" %
                    (self.coh.id, name))
            return self.give_up()
        else: # failed: launcher seems to have rejected it
            if self.coh.isStateStopped():
                return self.give_up()

            self.coh.setStateScheduled()
            self.logger.warn("Circuit #%s: %s order NOT stacked" % (self.coh.id, name))
            return self.switch_phase_failed(True)



class QueryContext :
    """A simply aliasing of CoHQuery container of circuit. """

    def __init__(self, running_phase):
        self.coh = running_phase.coh
        self.cmd = running_phase.cmd
        self.phase = running_phase.phase
        self.target = running_phase.target

  

class CircuitBase(object):
    """ 
    Data container of circuit.
    
    Provides the base operations with phases and builds all the needed
    references between phases and dispatcher.
    """
    # commands_on_host id
    id = None
    # commands id
    cmd_id = None



    status = CC_STATUS.ACTIVE
    # Main container of selected phases
    phases = None
 
    # methods called by scheduler-proxy
    _proxy_methods = {}
    # list of phases to refer phase objects 
    installed_phases = {}
    # Main container of selected phases
    _phases = None
    # msc data persistence model
    cohq = None
    # running phase reference
    running_phase = None
    # detected IP address of target
    host = None
    # detected network address of target
    network_address = None
    # first initialisation flag 
    initialized = False
    # A callable to self-releasing from the container 
    releaser = None
    # last activity timestamp
    last_activity_time = None
    # 
    launcher = None
    launchers_provider = None

    def __init__(self, _id, installed_phases, config, pull=False):
        """
        @param id: CommandOnHost id
        @type id: int

        @param installed_phases: all possible phases classes to use
        @type installed_phases: dict

        @param config: scheduler's configuration container
        @type config: SchedulerConfig

        @param pull: True if pull mode
        @type pull: bool
        """
        self.logger = logging.getLogger()
        self.id = _id
        self.config = config

        self.cohq = CoHQuery(int(_id))
        self.cmd_id = self.cohq.cmd.id

        self.installed_phases = installed_phases
        self.pull = pull

    @property 
    def is_running(self):
        return isinstance(self.running_phase, Phase)

    def setup(self, recurrent=False):
        """
        Post-init - detecting the networking info of target. 

        @param recurrent: if True, the circuit is on pull mode
        @type recurrent: bool
        """
        self.recurrent = recurrent

        if not self.initialized :
            d = maybeDeferred(self._flow_create)

            if not recurrent :
                d.addCallback(self._chooseClientNetwork)
                d.addCallback(self._host_detect) 
                d.addCallback(self._network_detect)

            d.addCallback(self._init_end)
            d.addErrback(self._init_failed)

            return d
        else :
            return Deferred()
     
    def _flow_create(self):
        """ Builds the workflow of circuit """
        
        phases = []
        selected = self.cohq.get_phases()
        if self.pull:
            d_mode = "pull"
        else :
            d_mode = "push"

        self.logger.debug("Circuit #%s: started on %s mode" %(self.id, d_mode))

        for phase_name in selected :
            matches = [p for p in self.installed_phases[d_mode] if p.name==phase_name]
            if len(matches) == 1:
                phases.append(matches[0])
            else :
                # TODO - log it and process something .. ?
                raise KeyError


        self.phases = phases
        return True

    @property
    def phases(self):
        """Gets the phases iterator"""
        return self._phases


    @phases.setter # pyflakes.ignore 
    def phases(self, value):
        """
        Phases property set processing.

        - Initial verifications of list of phases
        - converting the _phases attribute to iterator
        """
        if isinstance(value, list) and all(p for p in value if issubclass(p, Phase)):
            self._phases = iter(value)
        else :
            raise TypeError("All elements must be <Phase> type")

        self.__phases_list = value
 
    def on_last_phase(self):
        try:
            last_phase_names = [p.name for p in self.__phases_list[-2:]]
            return self.running_phase.name in last_phase_names
        except Exception, e:

            self.logger.error("\033[32mlast phase failed: %s\033[0m" % str(e))

    def install_releaser(self, releaser):
        """
        Links a release method of main dispatcher.

        When this method is called, circuit is removed from contaner.

        @param releaser: link to MscContainer().release()
        @type releaser: callable
        """
        if callable(releaser) :
            self.releaser = releaser
        else :
            raise TypeError("Releaser must be a callable")

    def install_dispatcher(self, dispatcher):
        """
        Link to dispatcher.

        @param dispatcher: link to main dispatcher
        @type dispatcher: MscDispatcher 
        """
        self.dispatcher = dispatcher

        # handle the dispatcher's release() method
        self.install_releaser(dispatcher.release)

    def release(self, suspend_to_waitings=False):
        """
        A 'self-destroy' method called on end of circuit.

        Called by MscContainer which contains list of processing circuits.
        This method is called when the circuits ends.  
        """
        self.dispatcher.stopped_track.remove(self.id)
        if self.recurrent :
            return
        try :
            self.releaser(self.cohq.coh.id, suspend_to_waitings)
            self.update_stats()
        except Exception, e:
            self.logger.error("Circuit release failed: %s" % str(e))


    @property
    def qm(self):
        """
        An aliasing context to CoHQeury container

        Aliased contexts:
        - self.qm.coh
        - self.qm.cmd
        - self.qm.phase
        - self.qm.target
        """
        return QueryContext(self.running_phase)

    def update_stats(self):
        """
        Handle the collected statistics from global collector.

        Statistics are collected each awake_time period and 
        updated when the circuit is processed.
        """
        self.dispatcher.statistics.update(self.cmd_id)

        if self.cmd_id in self.dispatcher.statistics.stats :
            stats = self.dispatcher.statistics.stats[self.cmd_id]
            self.cohq.cmd.update_stats(**stats)

    def schedule_last_stats(self):
        """
        Called when circuit is going to expire.

        Schedules the final update of command statistics.
        """
        self.dispatcher.statistics.watchdog_schedule(self.cmd_id)

    def _chooseClientNetwork(self, reason=None):
        """
        Choosing the correct IP address based on target info.

        @param reason: void parameter, used as twisted callback reason
        @type reason: twisted callback reason
        """
        return chooseClientInfo(self.cohq.target)

      
    def _host_detect(self, host):
        """
        Network address detect callback.
        
        Invoked by correct IP address of machine.

        @param host: IP address
        @type host: str

        @return: network address
        @rtype: str
        """
        if host :
            self.host = host

            for pref_net_ip, pref_netmask in self.config.preferred_network :
                if NetUtils.on_same_network(host, pref_net_ip, pref_netmask):

                    return pref_net_ip

            if len(self.config.preferred_network) > 0 :
                self.logger.debug("Circuit #%s: network detect failed, assigned the first of scheduler" % (self.id))
                (pref_net_ip, pref_netmask) = self.config.preferred_network[0] 
                return pref_net_ip
        else:
            self.logger.warn("Circuit #%s: IP address detect failed" % (self.id))

        if len(self.config.preferred_network) > 0 :
            self.logger.debug("Circuit #%s: network detect failed, assigned the first of scheduler" % (self.id))
            (pref_net_ip, pref_netmask) = self.config.preferred_network[0] 
            return pref_net_ip

 
 
    def _network_detect(self, address):
        """
        Network detect callback.

        @param address: network address
        @type address: str

        @return: True and Circuit instance when success
        @rtype: tuple
        """
        if address :
            self.network_address = address
        else :
            self.logger.debug("Circuit #%s: network not assigned" % (self.id))


        return True

    def _init_end(self, reason):
        """
        The final callback of initialization of circuit.

        @param reason: True and Circuit instance when success
        @type reason: tuple

        @return: Circuit instance
        @rtype: Circuit
        """

        self.initialized = True
        return self

    def _init_failed(self, failure):
        """
        Setup errorback.

        @param failure: failure reason
        @type failure: twisted failure
        """
        self.logger.error("An error occured while detecting target's ip address: %s" % str(failure))

class Circuit (CircuitBase):
    """
    This frame represets the workflow destinated on one machine.

    All steps is provided with Phase instances which represents several actions 
    destinated to a computer.
    """
 
    def run(self):
        """ Start the workflow scenario. """

        self.logger.debug("circuit #%s - assigned network: %s" % (self.id, self.network_address))
        self.logger.debug("circuit #%s - command: #%s / order: %s" % 
                (self.id, str(self.cohq.cmd.id), str(self.cohq.cmd.order_in_bundle)))
 
        try :
            if not self.running_phase:

                first = next(self.phases)
                self.running_phase = first(self.cohq, 
                                           self.host,
                                           self.config)
                if not self.recurrent:
                    self.running_phase.launchers_provider = self.launchers_provider
                self.running_phase.dispatcher = self.dispatcher

        except StopIteration :
            # All phases passed -> relase the circuit
            self.logger.info("Circuit #%s: all phases already processed  - releasing" % self.id)
            self.cohq.coh.setStateDone()
            self.release()
            return
 
        return self.phase_process(True) 

    def phase_process(self, result):
        """
        A callback to recursive phase processing.
        Can be called as an ordinnary routine (i.e. on start) 

        @param result: returned result from initial phase tests
        @type result: str

        @return: recursive workflow routine
        @rtype: func
        """
        self.cohq = CoHQuery(self.id)
        self.update_stats()
        # if give-up - actual phase is probably running - do not move - wait...
        if result == DIRECTIVE.GIVE_UP or result == None :
            return lambda : DIRECTIVE.GIVE_UP
        elif result == DIRECTIVE.FAILED :
            self.logger.info("Circuit #%s: failed - releasing" % self.id)
            self.release(True)
            return
        elif result in (DIRECTIVE.KILLED, DIRECTIVE.OVER_TIMED) :
            self.logger.info("Circuit #%s: releasing" % self.id)
            if result == DIRECTIVE.OVER_TIMED :
                self.schedule_last_stats()
            self.release()
            return
        elif result == DIRECTIVE.STOPPED:
            self.logger.info("Circuit #%s: stopping" % self.id)
            self.cohq.coh.setStateStopped()
            self.release()
            return
        else :
            return self.phase_step() 


    def phase_error(self, failure): 
        """
        Phase processing errorback.

        @param failure: failure reason
        @type failure: twisted failure
        """
        self.logger.error("Phase error: %s" % str(failure))


    def phase_step(self, forced_directive=None): 
        """
        Main workflow processing.

        standard chain call over all the phases :
        Initial state tests resolves the next flow - perform actual phase
        or skip to the next (or wait if actual phase is running)...

        @return: recursive workflow routine
        @rtype: func
        """

        if forced_directive :
            res = forced_directive
        else :
            # state tests before phase processing to resolving next flow
            res = self.running_phase.apply_initial_rules()

        # move on the next phase ->
        if res == DIRECTIVE.NEXT :

            try :
                next_phase = next(self.phases)
                self.running_phase = next_phase(self.cohq, 
                                                self.host,
                                                self.config)
                if not self.recurrent :
                    self.running_phase.launchers_provider = self.launchers_provider
                self.running_phase.dispatcher = self.dispatcher
                self.logger.debug("next phase :%s" % (self.running_phase))
            except StopIteration :
                # end of workflow - done !
                self.logger.info("Circuit #%d: done" % self.id)
                self.release()
            except Exception, e:
                self.logger.error("Next phase get failed: %s"  % str(e))

            else:
                d = Deferred()
                self.logger.debug("next phase: %s" % (self.running_phase.name))
                d.addCallback(self.phase_process)
                d.addErrback(self.phase_error)
                d.callback(True)
 
        # perform the phase (initial rules allready passed)
        elif res == DIRECTIVE.PERFORM :
            d = maybeDeferred(self.running_phase.perform)
            self.logger.debug("perform the phase: %s" % (self.running_phase.name))
            d.addCallback(self.phase_process)
            d.addCallback(self._last_activity_record)
            d.addErrback(self.phase_error)
            return d

        # give-up - actual phase is probably running
        elif res == DIRECTIVE.GIVE_UP :
            return False
        elif res == DIRECTIVE.OVER_TIMED :

            if self.on_last_phase() :
                self.logger.info("Circuit #%s: forced finish %s" % (self.id, self.running_phase.name))
                return self.phase_step(DIRECTIVE.NEXT)


            if self.running_phase.coh.attempts_failed > 0 \
                    or any_failed(self.id, self.config.non_fatal_steps) :
                self.cohq.coh.setStateFailed()
                self.logger.info("Circuit #%s: failed" % self.id)
            else :
                self.cohq.coh.setStateOverTimed()
                self.logger.info("Circuit #%s: overtimed" % self.id)

            if self.cohq.cmd.fk_bundle:
                self.dispatcher.bundles.clean_up(coh_id=self.id)
            self.schedule_last_stats()
            
            self.release()
            return
        elif res == DIRECTIVE.KILLED :
            self.logger.info("Circuit #%s: released" % self.id)
            try :
                self.release()
            except Exception, e:
                self.logger.error("Release failed: %s"  % str(e))
            return
        elif res == DIRECTIVE.STOPPED :
            self.logger.info("Circuit #%s: stopped" % self.id)
            self.cohq.coh.setStateStopped()
            self.release()
            return
        elif res == DIRECTIVE.FAILED :
            self.logger.info("Circuit #%s: failed - releasing" % self.id)
            self.release(True)
        else :
            self.logger.error("UNRECOGNIZED DIRECTIVE") 

    def _last_activity_record(self, reason):
        now = time.time()
        self.last_activity_time = now
        self.running_phase.last_activity_time = now

        return reason
               
    def gotErrorInResult(self, id, reason):
        self.logger.error("Circuit #%s: got an error within an result: %s" % (id, extractExceptionMessage(reason)))
        return DIRECTIVE.GIVE_UP



class MscContainer (object):
    __metaclass__ = SingletonN
    """
    Main database of circuits and access methods.

    All circuits to run are stocked here.
    """
    slots = {}
 
    # All the workflow circuits are stocked here
    _circuits = []

    # A lookup to refer all phases to use
    installed_phases = []

    # list of all networks
    groups = []

    # commands id to process a cleanup when a command expires
    # {cmd_id: fully_expired}
    # fully_expired :
    # - True if expired and ready to cleanup
    # - False if contains some unprocessed commands_on_host
    # This cmd_id is removed after the cleanup
    candidats_to_cleanup = {}

    # a provider to collect the commands statistics
    statistics = None

    @property
    def ready_candidats_to_cleanup(self):
        """ Shortcut to expired circuits according to cleanup conditions """
        return [cmd_id for (cmd_id, expired) in self.candidats_to_cleanup.items() if expired]

    def checkout_command(self, cmd_id):
        """
        Called on circuit releasing to hold a commands.id for cleanup

        @param cmd_id: id of commands record
        @type cmd_id: int
        """
        if cmd_id not in self.candidats_to_cleanup :
            self.candidats_to_cleanup[cmd_id] = False

    def set_ready_to_cleanup(self, cmd_id):
        """
        Corrensponding released circuits are ready to cleanup check

        @param cmd_id: id of commands record
        @type cmd_id: int
        """
        self.candidats_to_cleanup[cmd_id] = True
    
    @property 
    def circuits(self):
        """Shortcut to all active circuits"""
        return [c for c in self._circuits if c.status == CC_STATUS.ACTIVE]
    @property 
    def waiting_circuits(self):
        """Shortcut to all waiting circuits"""
        return [c for c in self._circuits if c.status == CC_STATUS.WAITING]

    def remove_circuit(self, circuit):
        """ 
        Release the circuit from container 

        @param circuit: circuit to remove
        @type circuit: Circuit
        """
        self.checkout_command(circuit.cmd_id)
        self._circuits.remove(circuit)

    @property
    def max_slots(self):
        """ All slots from all detected launchers """
        return reduce(lambda x, y: (x + y), self.slots.values()) 

    @property
    def free_slots(self):
        """ Free slots to use """
        return self.max_slots - len(self.get_active_circuits())

    def _in_waitings(self, id):
        """
        Test if a circuit is waiting.

        @param id: commands_on_host id
        @type id: int

        @return: True if command_on_host in container
        @rtype: bool
        """
        return id in [wf.id for wf in self.waiting_circuits]
 
    def __contains__(self, id):
        """ 
        Test if a circuit is already running,
        that means not released yet or added.

        @param id: commands_on_host id
        @type id: int

        @return: True if command_on_host in container
        @rtype: bool
        """
        return id in [wf.id for wf in self.circuits]

    def initialize(self, config):
        """ Initial setup """
        self.logger = logging.getLogger()
        self.config = config

        # provides the global statistics 
        self.statistics = StatisticsProcessing(config)

        # bundles tracking container
        self.bundles = BundleReferences(config)

        # launchers driving and slots detect
        self.groups = [net for (net, mask) in self.config.preferred_network]
        self.launchers_networks = dict([(launcher,[n[0] for n in net_and_mask]) 
                  for (launcher,net_and_mask) in self.config.launchers_networks.items()])
        self.logger.info("preferred networks by launchers: %s" % str(self.launchers_networks))
        self.launchers = self.config.launchers_uri
        # FIXME - main default launcher
        temp_launcher = self.launchers.keys()[0]
        self.launchers_provider = RemoteCallProxy(self.config.launchers_uri, temp_launcher)
        return self._get_all_slots()


    def _get_all_slots(self):
        """
        Detects the total of slots from all launchers.

        @return: total of slots per launcher
        @rtype: dict
        """
        d = self.launchers_provider.get_all_slots()

        d.addCallback(self._set_slots)
        d.addCallback(self._slots_info)
        @d.addErrback
        def _eb(failure):
            self.logger.error("An error occured when getting the slots:  %s" % failure)

        return d
     

    def _set_slots(self, slots):
        """
        Sets the detected slots from launchers

        @param slots: total of slots per launcher
        @type slots: dict
        """
        self.slots = slots
        return slots

    def _slots_info(self, result):
        """A little log stuff on start"""
        self.logger.info("Detected slots SUM from all launchers: %d" % self.max_slots)
        return result

    def has_free_slots(self):
        """ Checks if at least one slot is free"""
        return len(self.get_running_circuits()) < self.max_slots
 
    def get(self, id):
        """
        Get the circuit if exists.

        @param id: commands_on_host id
        @type id: int

        @return: requested circuit 
        @rtype: Circuit object
        """
        matches = [wf for wf in self._circuits if wf.id == id]
        if len(matches) > 0 :
            return matches[0]
        else :
            self.logger.debug("Circuit #%s: not exists" % id)
            return None

    def _release(self, id, suspend_to_waitings=False):
        """
        Circuit releasing from the main container.
        
        Called typicaly when last phase ends or overtimed. 
        A reference of this method is passed on each running phase to call
        when finished or overtimed.

        @param id: commands_on_host id
        @type id: int
        """
        if any([True for c in self._circuits if c.id == id]):
            self.logger.debug("circuit #%d finished" % id)
            circuit = self.get(id)
            if suspend_to_waitings :
                circuit.status = CC_STATUS.WAITING
                self.logger.info("Circuit #%d: failed and queued" % id)
            else :
                self.remove_circuit(circuit)
                self.stopped_track.remove(circuit.id)
            self.logger.info("Remaining content: %d circuits (+%d waitings)" % ((len(self.circuits)),len(self.waiting_circuits)))
            return True
        
        return False


