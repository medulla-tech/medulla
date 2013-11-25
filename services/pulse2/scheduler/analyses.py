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

from pulse2.scheduler.tracking.proxy import LocalProxiesUsageTracking
from pulse2.scheduler.types import MscContainer


class MscQueryManager(MscContainer):
    """ Ensapsulates all queries applied on circuit containers. """

    @property
    def nbr_groups(self):
        return len(self.config.preferred_network)

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


    def get_active_circuits(self, coh_ids=[]):
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
        if len(coh_ids) > 1:
            circuits = [c for c in circuits if c.id in coh_ids]
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
        banned = self.bundles.get_banned_cohs()
 
        now = time.time()
        circuits = [c for c in self.waiting_circuits if c.initialized and c.is_running]
        circuits = [c for c in circuits
                               if c.qm.coh.get_next_launch_timestamp() < now
                                  and not c.qm.coh.is_out_of_attempts()
                                  and c.id not in banned
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


    def _group_by_command(self, circuits):
        cmd_ids = []
        # get unique command ids
        [cmd_ids.append(c.cmd_id) for c in circuits if c.cmd_id not in cmd_ids]
        
        grouped = dict([(id,[]) for id in cmd_ids])
        for circuit in circuits :
            grouped[circuit.cmd_id].append(circuit)
            
        return grouped

    def get_all_running_bundles(self):
        b_ids = []
        [b_ids.append(c.cohq.cmd.fk_bundle) for c in self.circuits 
                                          if c.cohq.cmd.fk_bundle
                                          and c.cohq.cmd.fk_bundle not in b_ids
                ]
        return b_ids


    def get_unfinished_circuits(self):
        circuits = [c for c in self._circuits if c.initialized and c.is_running]
        circuits = [c for c in circuits if not c.qm.coh.isStateStopped()]

        failed = [c for c in circuits if c.qm.coh.isStateFailed()]
        overtimed = [c for c in circuits if c.qm.coh.isStateOverTimed()]

        return self._group_by_command(failed + overtimed)


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
            self.logger.debug("scheduler %s: command #%s seems to be wrong (bad priorities?)" % (self.config.name, cohq.cmd.id))
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
                    % (self.config.name, cmd_id))
            return 'split'
        elif len(spotted_priorities) == reduce(lambda x, y: x+y, spotted_priorities.values()): # one priority per proxy => queue mode
            self.logger.debug("scheduler %s: command #%s is in queue proxy mode"
                    % (self.config.name, cmd_id))
            return 'queue'
        else: # other combinations are errors
            self.logger.debug("scheduler %s: can'f guess proxy mode for command #%s" % (self.config.name, cmd_id))
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
                self.logger.debug("scheduler %s: coh #%s wait for a local proxy for to be usable" % (self.config.name, cohq.coh.id))
                return 'waiting'
            else: # take a proxy in alive proxies
                final_proxy = alive_proxies[final_uuid]
                self.logger.debug("scheduler %s: coh #%s found coh #%s as local proxy, taking one slot (%d left)" % (self.config.name, cohq.coh.id, final_proxy, LocalProxiesUsageTracking().how_much_left_for(final_uuid, cohq.cmd.getId())))
                return final_proxy

        def __processProbe(result, uuid, proxy):
            self.logger.debug("scheduler %s: coh #%s probed on %s, got %s" % (self.config.name, proxy, uuid, result))
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
                    self.logger.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (self.config.name, cohq.coh.id))
                    return 'dead'
                else:
                    self.logger.debug("scheduler %s: coh #%s wait for a local proxy to be ready" % (self.config.name, cohq.coh.id))
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
            self.logger.debug("scheduler %s: coh #%s become local proxy server" % (self.config.name, cohq.coh.id))
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
                            (self.config.name, best_ready_proxy_server_coh, cohq.coh.id))
                    return best_ready_proxy_server_coh
                else:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % 
                            (self.config.name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
                    return 'waiting'
            elif potential_proxy_server_coh != None:                        # ... and one may become ready => WAITING
                self.logger.debug("scheduler %s: coh #%s still waiting for a local proxy to use" % 
                        (self.config.name, cohq.coh.id))
                return 'waiting'
            else:                                                           # ... but all seems dead => ERROR
                self.logger.debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % 
                        (self.config.name, cohq.coh.id))
                return 'dead'
        else:                                                               # I'm a server: I MAY use a proxy ...
            if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
                (current_client_number, max_client_number) = self.get_client_usage_for_proxy(best_ready_proxy_server_coh)
                if current_client_number < max_client_number:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s" % 
                            (self.config.name, best_ready_proxy_server_coh, cohq.coh.id))
                    return best_ready_proxy_server_coh
                else:
                    self.logger.debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % 
                            (self.config.name, best_ready_proxy_server_coh, cohq.coh.id, current_client_number))
                    return 'waiting'
            elif potential_proxy_server_coh:                                # ... but a better candidate may become ready => WAITING
                self.logger.debug("scheduler %s: coh #%s still waiting to know if is is local proxy client or server" % 
                        (self.config.name, cohq.coh.id))
                return 'waiting'
            else:                                                           # ... and other best candidates seems dead => PROXY SERVER MODE
                self.logger.debug("scheduler %s: coh #%s become local proxy server" % 
                        (self.config.name, cohq.coh.id))
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
            self.logger.debug("scheduler %s: checking if we may continue coh #%s" % (self.config.name, cohq.coh.id))
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
                        (self.config.name, our_client_count, cohq.cmd.id))

            elif cohq.cmd.hasToUseSplitProxy():
 
                clients = [c for c in clients if c.qm.coh.order_in_proxy is None]
                our_client_count = len(clients)

            self.logger.debug("scheduler %s: found %s coh to be uploaded in command #%s" % 
                    (self.config.name, our_client_count, cohq.cmd.id))


            # proxy tracking update
            if our_client_count != 0:
                LocalProxiesUsageTracking().create_proxy(cohq.target.getUUID(),                        
                                                         cohq.coh.getMaxClientsPerProxy(), 
                                                         cohq.cmd.id)
                self.logger.debug("scheduler %s: (re-)adding %s (#%s) to proxy pool" % 
                        (self.config.name, cohq.target.getUUID(), cohq.cmd.getId()))
            else:
                LocalProxiesUsageTracking().delete_proxy(cohq.target.getUUID(), 
                                                         cohq.cmd.getId())
                self.logger.debug("scheduler %s: (re-)removing %s (#%s) from proxy pool" % 
                        (self.config.name, cohq.target.getUUID(), cohq.cmd.getId()))
            return our_client_count == 0
        else:
            return True

