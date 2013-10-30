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

import time

from twisted.internet.defer import DeferredList

from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.tracking.proxy import LocalProxiesUsageTracking
from pulse2.scheduler.types import MscContainer


class MscQueryManager(MscContainer):
    """ Ensapsulates all queries applied on circuit containers. """

    nbr_groups = len(SchedulerConfig().preferred_network)
    groups = [ip for (ip, mask) in SchedulerConfig().preferred_network]

    def _analyze_groups(self, circuits):
        """
        Counts the circuits by network (equivalent to SQL group by clause).
        
        @param circuits: list of Circuit instances
        @type circuits: list

        @return: grouped counts of circuits by network
        @rtype: dict
        """
        result = {}

        for group in self.groups :
            count = len([c for c in circuits if c.network_address==group])

            result[group] = count

        return result

    def get_circuits(self, ids):
        """
        Get the all circuits from internal circuits container.

        @param ids: list of commands_on_host
        @type ids: list

        @return: list of all circuits
        @rtype: list
        """
        return [c for c in self.circuits if c.id in ids]

    def get_running_circuits(self):
        """
        Get the all waitings circuits. 

        @param ids: list of commands_on_host
        @type ids: list

        @return: list of all circuits
        @rtype: list
        """
        return self.circuits
 

    def get_waiting_circuits(self, ids):
        """
        Get the all waitings circuits. 

        @param ids: list of commands_on_host
        @type ids: list

        @return: list of all circuits
        @rtype: list
        """
        return [c for c in self.waiting_circuits if c.id in ids]


    def get_active_circuits(self, cmd_ids=[]):
        """
        Get the all circuits already initialized and having a running phase.

        @param ids: list of commands
        @type ids: list

        @return: list of all circuits
        @rtype: list
        """
        if len(self.circuits) == 0 :
            return []
        circuits = [c for c in self.circuits if c.initialized and c.is_running]
        if len(circuits) == 0 :
            return [] 
        circuits = [c for c in circuits 
                       if not (c.qm.coh.isStateStopped() or c.qm.coh.isStatePaused())
                       and c.qm.cmd.in_valid_time()
                   ]
        if len(cmd_ids) > 1:
            circuits = [c for c in circuits if c.qm.cmd.id in cmd_ids]
            return circuits
        else :
            return []
 

    def rn_stats(self): return self._stats(self.circuits, "active")
    def wt_stats(self): return self._stats(self.waiting_circuits, "waiting")
    def _stats(self, circuits, c_name):
        if len(circuits) == 0 :
            return []
        cics = [c for c in circuits if c.is_running]

        ready   = len([c for c in cics if c.qm.phase.is_ready()])
        running = len([c for c in cics if c.qm.phase.is_running()])
        failed  = len([c for c in cics if c.qm.phase.is_failed()])
        done    = len([c for c in cics if c.qm.phase.is_done()])

        non_started = len([c for c in circuits if not c.is_running])
        self.logger.info("total %s circuits(%d) not started yet(%d)" % (c_name, len(cics), non_started)) 
        self.logger.info("- ready=%d running=%d failed=%d done=%d" % (ready, running, failed, done))


    def get_unprocessed_waitings(self):
        return [c for c in self.waiting_circuits if c.initialized and not c.is_running]
 
    def get_valid_waitings(self):

        now = time.time()
        circuits = [c for c in self.waiting_circuits if c.initialized and c.is_running]
        circuits = [c for c in circuits
                               if c.qm.coh.get_next_launch_timestamp() < now
                                  and not c.qm.coh.is_out_of_attempts()
                   ]
        return circuits

    def _get_candidats_to_failed(self, circuits):
        circuits = [c for c in circuits if c.initialized and c.is_running]
        return [c for c in circuits if c.qm.coh.is_out_of_attempts()
                                    and c.qm.phase.is_failed() 
               ]

    def _get_candidats_to_overtimed(self, circuits):
        circuits = [c for c in circuits if c.initialized and c.is_running]
        return [c for c in circuits if not c.qm.cmd.in_valid_time()]

    #def is_last_in_bundle(self, id, phase_name):
    def is_last_in_bundle(self, cmd, target, phase_name):
        """
        Checks the final state of all circuits in the same bundle.

        If remaining circuits terminated, returns True.
        Called typically by inventory or halt phase to waiting to finish
        of all attached circuits.

        @param id: commands_on_host id
        @type id: int

        @param phase_name: name of checked phase
        @type phase_name: str

        @return: True if checked circuit is last in bundle
        @rtype: bool
        """
        fk_bundle = cmd.fk_bundle
        order_in_bundle = cmd.order_in_bundle
        target_uuid = target.target_uuid

        nbr = len([c for c in self.get_active_circuits() 
                 if fk_bundle == c.qm.cmd.fk_bundle
                 and order_in_bundle == c.qm.cmd.order_in_bundle
                 and target_uuid == c.qm.target.target_uuid
                 and c.qm.phase.state == phase_name
                 and not c.qm.phase.is_done()
                 ])
        if nbr > 1 :
            self.logger.info("is last in bundle on #%s : still %s coh in the same bundle to do" % (str(id), str(nbr-1)))
            return False
        else :
            return True

    def local_proxy_upload_status(self, cohq):
        """ 
        attempt to analyse coh in the same command in order to now how we may advance.
        possible return values:
            - 'waiting': my time is not yet come
            - 'server': I'm an active proxy server
            - 'dead': I'm a client and all proxies seems dead
            - 'error': Something wrong was found in the command (usually mess in priorities)
            - an int: I'm a client and the returned value is the CoH I will use
        """
        proxy_mode = self.get_proxy_mode_for_command(cohq)
        if proxy_mode == 'queue':
            return self.local_proxy_attempt_queue_mode(cohq)
        elif proxy_mode == 'split':
            return self.local_proxy_attempt_split_mode(cohq)
        else:
            self.logger.debug("scheduler %s: command #%s seems to be wrong (bad priorities?)" % (SchedulerConfig().name, cohq.cmd.id))
            return 'dead'

        
    def get_proxy_mode_for_command(self, cmd_id):
        """ 
        Preliminar iteration to gather information about this command
        the idea being to obtain some informations about what's going on
        we are looking for the following elements
        - the amount of priorities:
          + only one => split mode (returns "split")
          + as many as proxies => queue mode (returns "queue")
          + no / not enough priorities => error condition (returns False)
        """

        spotted_priorities = {}

        circuits = [c for c in self.get_active_circuits() if c.qm.cmd.id==id]
        for c in circuits :
            if c.qm.cmd.order_in_proxy != None: # some potential proxy
                if c.qm.cmd.order_in_proxy in spotted_priorities:
                    spotted_priorities[c.qm.cmd.order_in_proxy] += 1
                else:
                    spotted_priorities[c.qm.cmd.order_in_proxy] = 1

        if len(spotted_priorities) == 0:
            return False
        elif len(spotted_priorities) == 1: # only one priority for all => split mode
            self.logger.debug("scheduler %s: command #%s is in split proxy mode"
                    % (SchedulerConfig().name, cmd_id))
            return 'split'
        elif len(spotted_priorities) == reduce(lambda x, y: x+y, spotted_priorities.values()): # one priority per proxy => queue mode
            self.logger.debug("scheduler %s: command #%s is in queue proxy mode"
                    % (SchedulerConfig().name, cmd_id))
            return 'queue'
        else: # other combinations are errors
            self.logger.debug("scheduler %s: can'f guess proxy mode for command #%s" % (SchedulerConfig().name, cmd_id))
            return False

    def local_proxy_attempt_split_mode(self, cohq):
        """split mode (parallel) implementation of proxy mode"""

        def __processProbes(result):
            # remove bad proxy (result => alive_proxy):
            alive_proxies = dict()
            for (success, (probe, uuid, coh_id)) in result:
                if success: # XMLRPC call do succeedeed
                    if probe:
                        if probe != "Not available":
                            alive_proxies[uuid] = coh_id

            # map if to go from {uuid1: (coh1, max1), uuid2: (coh2, max2)} to ((uuid1, max1), (uuid2, max2))
            # ret val is an uuid
            final_uuid = LocalProxiesUsageTracking().take_one(alive_proxies.keys(), cohq.cmd.id)
            if not final_uuid: # not free proxy, wait
                self.logger.debug("scheduler %s: coh #%s wait for a local proxy for to be usable" % (SchedulerConfig().name, cohq.coh.id))
                return 'waiting'
            else: # take a proxy in alive proxies
                final_proxy = alive_proxies[final_uuid]
                self.logger.debug("scheduler %s: coh #%s found coh #%s as local proxy, taking one slot (%d left)" % (SchedulerConfig().name, cohq.coh.id, final_proxy, LocalProxiesUsageTracking().how_much_left_for(final_uuid, cohq.cmd.getId())))
                return final_proxy

        def __processProbe(result, uuid, proxy):
            self.logger.debug("scheduler %s: coh #%s probed on %s, got %s" % (SchedulerConfig().name, proxy, uuid, result))
            return (result, uuid, proxy)

        if cohq.coh.getOrderInProxy() is None:   # I'm a client: I MUST use a proxy server ...
            temp_dysfunc_proxy = list() # proxies with no data (UPLOADED != DONE)
            def_dysfunc_proxy = list()  # proxies with no data (UPLOADED != DONE) and which definitely wont't process further (current_state != scheduled)
            available_proxy = list()    # proxies with complete data (UPLOADED = DONE)

            # iterate over CoH which
            # are linked to the same command
            # are not our CoH
            # are proxy server
            circuits = [c for c in self.get_active_circuits() 
                                if c.qm.cmd.id == cohq.cmd.id
                               and c.qm.coh.id != cohq.coh.id
                               and c.qm.coh.order_in_proxy is None]

            for c in circuits :
                # got 4 categories here:
                #  - DONE and not DONE
                #  - scheduled and not scheduled
                # => upload DONE, (scheduled or not): proxy free to use (depnding on nb of clients, see below)
                # => upload !DONE + (failed, over_timed) => will never be available => defin. failed
                # => upload !DONE + ! (failed or over_timed) => may be available in some time => temp. failed
                if (c.qm.coh.isStateFailed() or c.qm.coh.isStateOverTimed() or \
                    c.qm.coh.isStateStopped()) :
                    def_dysfunc_proxy.append(c.qm.coh.id)
                elif c.qm.phase.is_done():
                    available_proxy.append(c.qm.coh.id)
                else:
                    temp_dysfunc_proxy.append(c.qm.coh.id)

            if len(available_proxy) == 0: # not proxy seems ready ?
                if len(temp_dysfunc_proxy) == 0: # and others seems dead
                    self.logger.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, cohq.coh.id))
                    return 'dead'
                else:
                    self.logger.debug("scheduler %s: coh #%s wait for a local proxy to be ready" % (SchedulerConfig().name, cohq.coh.id))
                    return 'waiting'

            deffered_list = list()

            for proxy in available_proxy: # proxy is the proxy coh id
                #proxyCoH = session.query(CommandsOnHost).get(proxy)
                proxy_target = [c.qm.target for c in self.get_active_circuits() if c.qm.coh.id==proxy]
                assert len(proxy_target) == 1

                #proxyT = session.query(Target).get(proxyCoH.getIdTarget())

                #d = probeClient(
                d = self.launchers_provider.probe_client(proxy_target.getUUID(),
                                                         proxy_target.getFQDN(),
                                                         proxy_target.getShortName(),
                                                         proxy_target.getIps(),
                                                         proxy_target.getMacs(),
                                                         proxy_target.getNetmasks()
                                                        )
                d.addCallback(__processProbe, proxy_target.getUUID(), proxy)
                deffered_list.append(d)
            dl = DeferredList(deffered_list)
            dl.addCallback(__processProbes)
            return dl

        else:                                                               # I'm a server: let's upload
            self.logger.debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, cohq.coh.id))
            return 'server'


    def local_proxy_attempt_queue_mode(self, cohq):
        """ queue mode (serial) implementation of proxy mode """

        smallest_done_upload_order_in_proxy = None
        best_ready_proxy_server_coh = None
        potential_proxy_server_coh = None

        # iterate over CoH which
        # are linked to the same command
        # are not our CoH
        circuits = [c for c in self.get_active_circuits() 
                            if c.qm.cmd.id==cohq.cmd.id
                           and c.qm.coh.id != cohq.coh.id]

        for c in circuits :



            if c.qm.phase_is_done():          # got a pal which succeeded in doing its upload
                if not c.qm.coh.order_in_proxy is None :# got a potent proxy server
                    if smallest_done_upload_order_in_proxy < c.qm.coh.order_in_proxy:  
                        # keep its id as it seems to be the best server ever
                        smallest_done_upload_order_in_proxy = c.qm.coh.order_in_proxy
                        best_ready_proxy_server_coh = c.qm.coh.id

            elif not c.qm.coh.isStateFailed():   # got a pal which may still do something
                if c.qm.coh.order_in_proxy != None:     # got a potential proxy server
                    if cohq.coh.order_in_proxy is None:    # i may use this server, as I'm not server myself
                        potential_proxy_server_coh = c.qm.coh.id
                    elif cohq.coh.order_in_proxy > c.qm.coh.order_in_proxy:               
                        # i may use this server, as it has a lower priority than me
                        potential_proxy_server_coh = c.qm.coh.id

        # we now know:
        # a proxy that may be used
        # a proxy that might be used
        # let's take a decision about our future

        if cohq.coh.getOrderInProxy() == None:  # I'm a client: I MUST use a proxy server ...
            if best_ready_proxy_server_coh != None:    # ... and a proxy seems ready => PROXY CLIENT MODE
                (current_client_number, max_client_number) = self.get_client_usage_for_proxy(best_ready_proxy_server_coh)
                if current_client_number < max_client_number:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s" %
                            (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id))
                    return best_ready_proxy_server_coh
                else:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % 
                            (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
                    return 'waiting'
            elif potential_proxy_server_coh != None:                        # ... and one may become ready => WAITING
                self.logger.debug("scheduler %s: coh #%s still waiting for a local proxy to use" % 
                        (SchedulerConfig().name, cohq.coh.id))
                return 'waiting'
            else:                                                           # ... but all seems dead => ERROR
                self.logger.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % 
                        (SchedulerConfig().name, cohq.coh.id))
                return 'dead'
        else:                                                               # I'm a server: I MAY use a proxy ...
            if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
                (current_client_number, max_client_number) = self.get_client_usage_for_proxy(best_ready_proxy_server_coh)
                if current_client_number < max_client_number:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s" % 
                            (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id))
                    return best_ready_proxy_server_coh
                else:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % 
                            (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
                    return 'waiting'
            elif potential_proxy_server_coh:                                # ... but a better candidate may become ready => WAITING
                self.logger.debug("scheduler %s: coh #%s still waiting to know if is is local proxy client or server" % 
                        (SchedulerConfig().name, cohq.coh.id))
                return 'waiting'
            else:                                                           # ... and other best candidates seems dead => PROXY SERVER MODE
                self.logger.debug("scheduler %s: coh #%s become local proxy server" % 
                        (SchedulerConfig().name, cohq.coh.id))
                return 'server'
 
    def get_client_usage_for_proxy(self, id):
        """
        count the (current number, max number) of clients using this proxy
        a client is using a proxy if:
        - getUsedProxy == proxyCommandOnHostID
        current_state == upload_in_progress
        to save some time, iteration is done as usual (on command from coh)
        """
        commands_ids, max_clients = [(c.qm.cmd.id,
                                      c.qm.coh.getMaxClientsPerProxy()) 
                                     for c in self.get_active_circuits() if c.qm.coh.id==id] 
        assert len(commands_ids) == 1

        cmd_id = commands_ids[0]
        circuits = [c for c in self.get_active_circuits() 
                            if c.qm.cmd.id==cmd_id
                           and c.qm.coh.fk_use_as_proxy==id
                           and c.qm.phase.is_running()
                   ]
        return (len(circuits), max_clients)


    def local_proxy_may_continue(self, cohq):
        """ attempt to analyse coh in the same command in order to now how we may advance.

        Clean algorithm:
        client => always cleanup
        server => cleanup only if *everybody" are in one of the following state:
          - upload done
          - upload ignored
          - failed
          - over_timed
        to prevent race condition, not check is perform to count only our clients but everybody client
        """

        if cohq.coh.isLocalProxy(): # proxy server, way for clients to be done
            self.logger.debug("scheduler %s: checking if we may continue coh #%s" % (SchedulerConfig().name, cohq.coh.id))
            our_client_count = 0
            clients = [c for c in self.get_active_circuits() 
                               if c.qm.cmd.id==cohq.cmd.id
                              and c.qm.coh.id != cohq.coh.id
                              and not c.qm.phase.id_done()
                              and not c.qm.coh.isStateDone()
                              and not c.qm.coh.isStateOverTimed()]

            if cohq.cmd.hasToUseQueueProxy():
                our_client_count = len(clients)
                self.logger.debug("scheduler %s: found %s coh to be uploaded in command #%s" % 
                        (SchedulerConfig().name, our_client_count, cohq.cmd.id))

            elif cohq.cmd.hasToUseSplitProxy():
 
                clients = [c for c in clients if c.qm.coh.order_in_proxy is None]
                our_client_count = len(clients)

            self.logger.debug("scheduler %s: found %s coh to be uploaded in command #%s" % 
                    (SchedulerConfig().name, our_client_count, cohq.cmd.id))


            # proxy tracking update
            if our_client_count != 0:
                LocalProxiesUsageTracking().create_proxy(cohq.target.getUUID(),                        
                                                         cohq.coh.getMaxClientsPerProxy(), 
                                                         cohq.cmd.id)
                self.logger.debug("scheduler %s: (re-)adding %s (#%s) to proxy pool" % 
                        (SchedulerConfig().name, cohq.target.getUUID(), cohq.cmd.getId()))
            else:
                LocalProxiesUsageTracking().delete_proxy(cohq.target.getUUID(), 
                                                         cohq.cmd.getId())
                self.logger.debug("scheduler %s: (re-)removing %s (#%s) from proxy pool" % 
                        (SchedulerConfig().name, cohq.target.getUUID(), cohq.cmd.getId()))
            return our_client_count == 0
        else:
            return True

 





#log = logging.getLogger()

#handle_deconnect()
#
#class Analyses :
#    def __init__(self):
#        from pulse2.database.msc import MscDatabase
#        self.database = MscDatabase()
#
#    def isLastToInventoryInBundle(self, coh, cmd, target):
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        
#        if coh == None:
#            return []
#
#        session = sqlalchemy.orm.create_session()
#
#        nb = session.query(CommandsOnHost
#            ).select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)
#            ).filter(self.database.commands.c.fk_bundle == cmd.fk_bundle
#            ).filter(self.database.commands.c.order_in_bundle == cmd.order_in_bundle
#            ).filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)
#            ).filter(self.database.target.c.target_uuid ==  target.target_uuid
#            ).filter(sqlalchemy.not_(
#                self.database.commands_on_host.c.current_state.in_(PULSE2_POST_INVENTORY_STATES))
#            ).count()
#
#        session.close()
#        if nb != 1:
#            log.debug("isLastToInventoryInBundle on #%s : still %s coh in the same bundle to do" % (str(coh.id), str(nb-1)))
#            return False
#        return True
#
#    def isLastToHaltInBundle(self, coh, cmd, target):
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        #if myCoH == None:
#        #    return []
#
#        session = sqlalchemy.orm.create_session()
#
#        nb = session.query(CommandsOnHost
#            ).select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)
#            ).filter(self.database.commands.c.fk_bundle == cmd.fk_bundle
#            ).filter(self.database.commands.c.order_in_bundle == cmd.order_in_bundle
#            ).filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)                
#            ).filter(self.database.target.c.target_uuid ==  target.target_uuid
#            ).filter(sqlalchemy.not_(
#                self.database.commands_on_host.c.current_state.in_(PULSE2_POST_HALT_STATES))
#            ).count()
#
#        session.close()
#        if nb > 1:
#            log.debug("isLastToHaltInBundle on #%s : still %s coh in the same bundle to do" % (str(coh.id), str(nb-1)))
#            return False
#        return True

#    def localProxyUploadStatus(self, cohq):
#        """ attempt to analyse coh in the same command in order to now how we may advance.
#        possible return values:
#            - 'waiting': my time is not yet come
#            - 'server': I'm an active proxy server
#            - 'dead': I'm a client and all proxies seems dead
#            - 'error': Something wrong was found in the command (usually mess in priorities)
#            - an int: I'm a client and the returned value is the CoH I will use
#        """
#        #myCommandOnHostID = cohq.coh.id
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        #if myCoH == None:
#        #    return 'error'
#
#        # as for now, if we previously found a proxy, use it
#        # commented out: may break the split proxy model
#        #if myCoH.getUsedProxy() != None:
#        #    log.debug("scheduler %s: keeping coh #%s as local proxy for #%s" % (SchedulerConfig().name, myCoH.getUsedProxy(), myCommandOnHostID))
#        #    return 'keeping'
#
#        # see what to do next
#        proxy_mode = self.getProxyModeForCommand(cohq)
#        if proxy_mode == 'queue':
#            return self.localProxyAttemptQueueMode(cohq)
#        elif proxy_mode == 'split':
#            return self.localProxyAttemptSplitMode(cohq)
#        else:
#            log.debug("scheduler %s: command #%s seems to be wrong (bad priorities?)" % (SchedulerConfig().name, cohq.cmd.id))
#            return 'dead'


#    def localProxyAttemptQueueMode(self, cohq):
#        # queue mode (serial) implementation of proxy mode
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        #if myCoH == None:
#        #    return 'error'
#
#        smallest_done_upload_order_in_proxy = None
#        best_ready_proxy_server_coh = None
#        potential_proxy_server_coh = None
#
#        # iterate over CoH which
#        # are linked to the same command
#        # are not our CoH
#        session = sqlalchemy.orm.create_session()
#        
#        for q in session.query(CommandsOnHost).\
#            select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#            filter(self.database.commands.c.id == cohq.cmd.id).\
#            filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#            filter(self.database.commands_on_host.c.id != cohq.coh.getId()).\
#            all():
#                if q.uploaded == PULSE2_STAGE_DONE:                                 # got a pal which succeeded in doing its upload
#                    if q.order_in_proxy != None:                                    # got a potent proxy server
#                        if smallest_done_upload_order_in_proxy < q.order_in_proxy:  # keep its id as it seems to be the best server ever
#                            smallest_done_upload_order_in_proxy = q.order_in_proxy
#                            best_ready_proxy_server_coh = q.id
#                elif q.current_state != 'failed':                                   # got a pal which may still do something
#                    if q.order_in_proxy != None:                                    # got a potential proxy server
#                        if cohq.coh.order_in_proxy == None:                            # i may use this server, as I'm not server myself
#                            potential_proxy_server_coh = q.id
#                        elif cohq.coh.order_in_proxy > q.order_in_proxy:               # i may use this server, as it has a lower priority than me
#                            potential_proxy_server_coh = q.id
#        session.close()
#
#        # we now know:
#        # a proxy that may be used
#        # a proxy that might be used
#        # let's take a decision about our future
#
#        if cohq.coh.getOrderInProxy() == None:                                 # I'm a client: I MUST use a proxy server ...
#            if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
#                (current_client_number, max_client_number) = self.getClientUsageForProxy(best_ready_proxy_server_coh)
#                if current_client_number < max_client_number:
#                    log.debug("scheduler %s: found coh #%s as local proxy for #%s" %
#                            (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id))
#                    return best_ready_proxy_server_coh
#                else:
#                    log.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
#                    return 'waiting'
#            elif potential_proxy_server_coh != None:                        # ... and one may become ready => WAITING
#                log.debug("scheduler %s: coh #%s still waiting for a local proxy to use" % (SchedulerConfig().name, cohq.coh.id))
#                return 'waiting'
#            else:                                                           # ... but all seems dead => ERROR
#                log.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, cohq.coh.id))
#                return 'dead'
#        else:                                                               # I'm a server: I MAY use a proxy ...
#            if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
#                (current_client_number, max_client_number) = self.getClientUsageForProxy(best_ready_proxy_server_coh)
#                if current_client_number < max_client_number:
#                    log.debug("scheduler %s: found coh #%s as local proxy for #%s" % (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id))
#                    return best_ready_proxy_server_coh
#                else:
#                    log.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % (SchedulerConfig().name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
#                    return 'waiting'
#            elif potential_proxy_server_coh:                                # ... but a better candidate may become ready => WAITING
#                log.debug("scheduler %s: coh #%s still waiting to know if is is local proxy client or server" % (SchedulerConfig().name, cohq.coh.id))
#                return 'waiting'
#            else:                                                           # ... and other best candidates seems dead => PROXY SERVER MODE
#                log.debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, cohq.coh.id))
#                return 'server'
    
#    def localProxyAttemptSplitMode(self, cohq):
#        # split mode (parallel) implementation of proxy mode
#
#        def __processProbes(result):
#            # remove bad proxy (result => alive_proxy):
#            alive_proxies = dict()
#            for (success, (probe, uuid, coh_id)) in result:
#                if success: # XMLRPC call do succeedeed
#                    if probe:
#                        if probe != "Not available":
#                            alive_proxies[uuid] = coh_id
#
#            # map if to go from {uuid1: (coh1, max1), uuid2: (coh2, max2)} to ((uuid1, max1), (uuid2, max2))
#            # ret val is an uuid
#            final_uuid = LocalProxiesUsageTracking().take_one(alive_proxies.keys(), cohq.cmd.getId())
#            if not final_uuid: # not free proxy, wait
#                log.debug("scheduler %s: coh #%s wait for a local proxy for to be usable" % (SchedulerConfig().name, cohq.coh.id))
#                return 'waiting'
#            else: # take a proxy in alive proxies
#                final_proxy = alive_proxies[final_uuid]
#                log.debug("scheduler %s: coh #%s found coh #%s as local proxy, taking one slot (%d left)" % (SchedulerConfig().name, cohq.coh.id, final_proxy, LocalProxiesUsageTracking().how_much_left_for(final_uuid, cohq.cmd.getId())))
#                return final_proxy
#
#        def __processProbe(result, uuid, proxy):
#            log.debug("scheduler %s: coh #%s probed on %s, got %s" % (SchedulerConfig().name, proxy, uuid, result))
#            return (result, uuid, proxy)
#
#        #(myCoH, myC, myT) = gatherCoHStuff(cohq.coh.id)
#        #if myCoH == None:
#        #    return 'error'
#        if cohq.coh.getOrderInProxy() == None:                                 # I'm a client: I MUST use a proxy server ...
#            temp_dysfunc_proxy = list() # proxies with no data (UPLOADED != DONE)
#            def_dysfunc_proxy = list()  # proxies with no data (UPLOADED != DONE) and which definitely wont't process further (current_state != scheduled)
#            available_proxy = list()    # proxies with complete data (UPLOADED = DONE)
#
#            # iterate over CoH which
#            # are linked to the same command
#            # are not our CoH
#            # are proxy server
#            session = sqlalchemy.orm.create_session()
#            
#            for q in session.query(CommandsOnHost).\
#                select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#                filter(self.database.commands.c.id == cohq.cmd.id).\
#                filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#                filter(self.database.commands_on_host.c.id != cohq.coh.getId()).\
#                filter(self.database.commands_on_host.c.order_in_proxy != None).\
#                all():
#                    # got 4 categories here:
#                    #  - DONE and not DONE
#                    #  - scheduled and not scheduled
#                    # => upload DONE, (scheduled or not): proxy free to use (depnding on nb of clients, see below)
#                    # => upload !DONE + (failed, over_timed) => will never be available => defin. failed
#                    # => upload !DONE + ! (failed or over_timed) => may be available in some time => temp. failed
#                    if q.current_state in ('failed', 'over_timed', 'stopped', 'stop'):
#                        def_dysfunc_proxy.append(q.id)
#                    elif q.uploaded == PULSE2_STAGE_DONE:
#                        available_proxy.append(q.id)
#                    else:
#                        temp_dysfunc_proxy.append(q.id)
#            session.close()
#
#            if len(available_proxy) == 0: # not proxy seems ready ?
#                if len(temp_dysfunc_proxy) == 0: # and others seems dead
#                    log.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, cohq.coh.id))
#                    return 'dead'
#                else:
#                    log.debug("scheduler %s: coh #%s wait for a local proxy to be ready" % (SchedulerConfig().name, cohq.coh.id))
#                    return 'waiting'
#
#            deffered_list = list()
#
#            for proxy in available_proxy: # proxy is the proxy coh id
#                #(proxyCoH, proxyC, proxyT) = gatherCoHStuff(proxy)
#                proxyCoH = session.query(CommandsOnHost).get(proxy)
#                proxyT = session.query(Target).get(proxyCoH.getIdTarget())
#
#                #d = probeClient(
#                d = LauncherProxy(SchedulerConfig().launchers_uri).probe_client(
#                    proxyT.getUUID(),
#                    proxyT.getFQDN(),
#                    proxyT.getShortName(),
#                    proxyT.getIps(),
#                    proxyT.getMacs(),
#                    proxyT.getNetmasks()
#                )
#                d.addCallback(__processProbe, proxyT.getUUID(), proxy)
#                deffered_list.append(d)
#            dl = twisted.internet.defer.DeferredList(deffered_list)
#            dl.addCallback(__processProbes)
#            return dl
#
#        else:                                                               # I'm a server: let's upload
#            log.debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, cohq.coh.id))
#            return 'server'
#
    
#    def getClientUsageForProxy(self, cohq):
#        # count the (current number, max number) of clients using this proxy
#        # a client is using a proxy if:
#        # - getUsedProxy == proxyCommandOnHostID
#        # current_state == upload_in_progress
#        # to save some time, iteration is done as usual (on command from coh)
#        #(myCoH, myC, myT) = gatherCoHStuff(proxyCommandOnHostID)
#        #if myCoH == None: # current_client_number == max_client_number => dont use this target as a possible proxy
#        #    return (0, 0)
#        session = sqlalchemy.orm.create_session()
#        client_count = session.query(CommandsOnHost).\
#            select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#            filter(self.database.commands.c.id == cohq.cmd.id).\
#            filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#            filter(self.database.commands_on_host.c.fk_use_as_proxy == cohq.coh.getId()).\
#            filter(self.database.commands_on_host.c.current_state == 'upload_in_progress').\
#            count()
#        session.close()
#        return (client_count, cohq.coh.getMaxClientsPerProxy())
#
    
#    def getProxyModeForCommand(self, cohq):
#        # Preliminar iteration to gather information about this command
#        # the idea being to obtain some informations about what's going on
#        # we are looking for the following elements
#        # - the amount of priorities:
#        #   + only one => split mode (returns "split")
#        #   + as many as proxies => queue mode (returns "queue")
#        #   + no / not enough priorities => error condition (returns False)
#
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        #if myCoH == None:
#        #    return False
#
#        spotted_priorities = dict()
#
#        session = sqlalchemy.orm.create_session()
#        
#        for q in session.query(CommandsOnHost).\
#            select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#            filter(self.database.commands.c.id == cohq.cmd.id).\
#            filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#            all():
#                if q.order_in_proxy != None: # some potential proxy
#                    if q.order_in_proxy in spotted_priorities:
#                        spotted_priorities[q.order_in_proxy] += 1
#                    else:
#                        spotted_priorities[q.order_in_proxy] = 1
#        session.close()
#
#        if len(spotted_priorities) == 0:
#            return False
#        elif len(spotted_priorities) == 1: # only one priority for all => split mode
#            log.debug("scheduler %s: command #%s is in split proxy mode" % (SchedulerConfig().name, cohq.cmd.id))
#            return 'split'
#        elif len(spotted_priorities) == reduce(lambda x, y: x+y, spotted_priorities.values()): # one priority per proxy => queue mode
#            log.debug("scheduler %s: command #%s is in queue proxy mode" % (SchedulerConfig().name, cohq.cmd.id))
#            return 'queue'
#        else: # other combinations are errors
#            log.debug("scheduler %s: can'f guess proxy mode for command #%s" % (SchedulerConfig().name, cohq.cmd.id))
#            return False

    
#    def localProxyMayContinue(self, cohq):
#        """ attempt to analyse coh in the same command in order to now how we may advance.
#        """
#        #(myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
#        #if myCoH == None:
#        #    return False # TODO : when an error occur, do we want to clean the local proxy ?
#
#        # Clean algorithm:
#        # client => always cleanup
#        # server => cleanup only if *everybody" are in one of the following state:
#        #   - upload done
#        #   - upload ignored
#        #   - failed
#        #   - over_timed
#        # to prevent race condition, not check is perform to count only our clients but everybody client
#
#        if cohq.coh.isLocalProxy(): # proxy server, way for clients to be done
#            log.debug("scheduler %s: checking if we may continue coh #%s" % (SchedulerConfig().name, cohq.coh.id))
#            our_client_count = 0
#            if cohq.cmd.hasToUseQueueProxy():
#                session = sqlalchemy.orm.create_session()
#                our_client_count = session.query(CommandsOnHost).\
#                    select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#                    filter(self.database.commands.c.id == cohq.cmd.id).\
#                    filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#                    filter(self.database.commands_on_host.c.id != cohq.coh.getId()).\
#                    filter(self.database.commands_on_host.c.uploaded != 'DONE').\
#                    filter(self.database.commands_on_host.c.uploaded != 'IGNORED').\
#                    filter(self.database.commands_on_host.c.current_state != 'failed').\
#                    filter(self.database.commands_on_host.c.current_state != 'done').\
#                    filter(self.database.commands_on_host.c.current_state != 'over_timed').\
#                    count()
#                log.debug("scheduler %s: found %s coh to be uploaded in command #%s" % (SchedulerConfig().name, our_client_count, cohq.cmd.id))
#                session.close()
#            elif cohq.cmd.hasToUseSplitProxy():
#                session = sqlalchemy.orm.create_session()
#                our_client_count = session.query(CommandsOnHost).\
#                    select_from(self.database.commands_on_host.join(self.database.commands).join(self.database.target)).\
#                    filter(self.database.commands.c.id == cohq.cmd.id).\
#                    filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)).\
#                    filter(self.database.commands_on_host.c.id != cohq.coh.getId()).\
#                    filter(self.database.commands_on_host.c.order_in_proxy == None).\
#                    filter(self.database.commands_on_host.c.uploaded != 'DONE').\
#                    filter(self.database.commands_on_host.c.uploaded != 'IGNORED').\
#                    filter(self.database.commands_on_host.c.current_state != 'failed').\
#                    filter(self.database.commands_on_host.c.current_state != 'done').\
#                    filter(self.database.commands_on_host.c.current_state != 'over_timed').\
#                    count()
#                log.debug("scheduler %s: found %s coh to be uploaded in command #%s" % (SchedulerConfig().name, our_client_count, cohq.cmd.id))
#                session.close()
#            # proxy tracking update
#            if our_client_count != 0:
#                LocalProxiesUsageTracking().create_proxy(cohq.target.getUUID(), cohq.coh.getMaxClientsPerProxy(), cohq.cmd.getId())
#                log.debug("scheduler %s: (re-)adding %s (#%s) to proxy pool" % (SchedulerConfig().name, cohq.target.getUUID(), cohq.cmd.getId()))
#            else:
#                LocalProxiesUsageTracking().delete_proxy(cohq.target.getUUID(), cohq.cmd.getId())
#                log.debug("scheduler %s: (re-)removing %s (#%s) from proxy pool" % (SchedulerConfig().name, cohq.target.getUUID(), cohq.cmd.getId()))
#            return our_client_count == 0
#        else:
#            return True

    
#    def gatherIdsToStart(self, scheduler_name, ids_to_exclude = []):
#        session = sqlalchemy.orm.create_session()
#
#        # gather candidates : long story short, takes everything which is not
#        # beeing processed (in PULSE2_PROGRESSING_STATES))
#        # unpreemptable (in PULSE2_UNPREEMPTABLE_STATES))
#        # ignore tasks with no retries left
#        # take tasks with next launch time in the future
#        #
#        # Please pay attention that as nowhere is is specified the commands start_date and end_date
#        # fields 'special' values ("0000-00-00 00:00:00" and "2031-12-31 23:59:59"), I
#        # consider that:
#        #  - start_date:
#        #   + "0000-00-00 00:00:00" means "as soon as possible",
#        #   + "2031-12-31 23:59:59" means "never",
#        #  - end_date:
#        #   + "0000-00-00 00:00:00" means "never" (yeah, that's f*****g buggy, but how really matter the *specs*, hu ?),
#        #   + "2031-12-31 23:59:59" means "never",
#        #
#        # consequently, I may process tasks:
#        #     with start_date = "0000-00-00 00:00:00" or start_date <= now
#        # and start_date <> "2031-12-31 23:59:59"
#        # and end_date = "0000-00-00 00:00:00" or end_date = "2031-12-31 23:59:59" or end_date >= now
#        #
#        # TODO: check command state integrity AND command_on_host state integrity in a separtseparate function
#
#        now = time.strftime("%Y-%m-%d %H:%M:%S")
#        soon = time.strftime("0000-00-00 00:00:00")
#        later = time.strftime("2031-12-31 23:59:59")
#
#        commands_query = session.query(CommandsOnHost).\
#            select_from(self.database.commands_on_host.join(self.database.commands)
#            ).filter(sqlalchemy.not_(self.database.commands_on_host.c.current_state.in_(PULSE2_PROGRESSING_STATES))
#            ).filter(sqlalchemy.not_(self.database.commands_on_host.c.current_state.in_(PULSE2_UNPREEMPTABLE_STATES))
#            ).filter(self.database.commands_on_host.c.attempts_left > self.database.commands_on_host.c.attempts_failed
#            ).filter(self.database.commands_on_host.c.next_launch_date <= now
#            ).filter(self.database.commands.c.state.in_(PULSE2_COMMANDS_ACTIVE_STATES)                
#            ).filter(sqlalchemy.or_(
#                self.database.commands.c.start_date == soon,
#                self.database.commands.c.start_date <= now)
#            ).filter(self.database.commands.c.start_date != later
#            ).filter(sqlalchemy.or_(
#                self.database.commands.c.end_date == soon,
#                self.database.commands.c.end_date == later,
#                self.database.commands.c.end_date > now)
#            ).filter(sqlalchemy.or_(
#                self.database.commands_on_host.c.scheduler == '',
#                self.database.commands_on_host.c.scheduler == scheduler_name,
#                self.database.commands_on_host.c.scheduler == None)
#            ).filter(sqlalchemy.not_(
#                self.database.commands_on_host.c.id.in_(ids_to_exclude))
#            ).order_by(self.database.commands_on_host.c.current_state.desc())
#            # IMPORTANT NOTE : This ordering is not alphabetical!
#            # Field 'current_state' is ENUM type, so decisive condition
#            # is order of element in the declaration of field.
#            # Because this order of elements is suitable on workflow, 
#            # using of descending order allows to favouring the commands
#            # which state is approaching to end of worklow.
#
#
#        commands_to_perform = [q.id for q in commands_query.all()]
#
#        session.close()
#        return commands_to_perform
#
