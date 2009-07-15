# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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

# Big modules
import logging
import time
import re
import os
import random
import datetime

import sqlalchemy
import sqlalchemy.orm

# Twisted modules
import twisted.internet

# MMC plugins
from pulse2.database.msc import MscDatabase
import pulse2.apis.clients.mirror

# ORM mappings
from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost
from pulse2.database.msc.orm.commands_history import CommandsHistory
from pulse2.database.msc.orm.target import Target
from pulse2.database.utilities import handle_deconnect

# our modules
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.launchers_driving import callOnBestLauncher, callOnLauncher, getLaunchersBalance, probeClient
import pulse2.scheduler.network
from pulse2.scheduler.assign_algo import MGAssignAlgoManager
from pulse2.scheduler.checks import getCheck, getAnnounceCheck
from pulse2.scheduler.launchers_driving import pingAndProbeClient
from pulse2.scheduler.tracking.proxy import LocalProxiesUsageTracking

handle_deconnect()

def gatherStuff():
    """ handy function to gather widely used objects """
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    logger = logging.getLogger()
    return (session, database, logger)

def gatherCoHStuff(idCommandOnHost):
    """ same as gatherStuff(), this time for a particular CommandOnHost """
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    myCommandOnHost = session.query(CommandsOnHost).get(idCommandOnHost)
    if type(myCommandOnHost) != CommandsOnHost:
        session.close()
        logging.getLogger().error("trying to gather CoH on an inexisting CoH '%s' !! (Maybe you are currently cleaning the database?)"%(str(idCommandOnHost)))
        return (None, None, None)
    myCommand = session.query(Commands).get(myCommandOnHost.getIdCommand())
    myTarget = session.query(Target).get(myCommandOnHost.getIdTarget())
    session.close()
    if type(myCommand) != Commands or type(myTarget) != Target:
        logging.getLogger().error("trying to gather CoH on an inexisting CoH '%s' !! (Maybe you are currently cleaning the database?)"%(str(idCommandOnHost)))
        return (None, None, None)
    return (myCommandOnHost, myCommand, myTarget)

def isLastToInventoryInBundle(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return []

    session = sqlalchemy.orm.create_session()
    database = MscDatabase()

    futur_states = ['reboot_in_progress', 'reboot_done', 'reboot_failed', 'halt_in_progress', 'halt_done', 'halt_failed', 'done', 'failed', 'over_timed']

    nb = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)).\
        filter(database.commands.c.fk_bundle == myC.fk_bundle).\
        filter(database.commands.c.order_in_bundle == myC.order_in_bundle).\
        filter(sqlalchemy.not_(database.commands_on_host.c.current_state.in_(futur_states))).\
        count()

    session.close()
    if nb != 1:
        logging.getLogger().debug("isLastToInventoryInBundle on #%s : still %s coh in the same bundle to do"%(str(myCommandOnHostID), str(nb-1)))
        return False
    return True

def isLastToHaltInBundle(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return []

    session = sqlalchemy.orm.create_session()
    database = MscDatabase()

    nb = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)).\
        filter(database.commands.c.fk_bundle == myC.fk_bundle).\
        filter(database.commands.c.order_in_bundle == myC.order_in_bundle).\
        filter(sqlalchemy.and_(
            database.commands_on_host.c.current_state != 'done', \
            database.commands_on_host.c.current_state != 'failed', \
            database.commands_on_host.c.current_state != 'over_timed')).\
        count()

    session.close()
    if nb != 1:
        logging.getLogger().debug("isLastToHaltInBundle on #%s : still %s coh in the same bundle to do"%(str(myCommandOnHostID), str(nb-1)))
        return False
    return True

def getDependancies(myCommandOnHostID):
    """
        check deps, returns;
            "dead": will never be able to complete
            "wait": may be able to complet, but not yet
            "run": can run now
    """

    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return []

    session = sqlalchemy.orm.create_session()
    database = MscDatabase()

    # look for CoH from same bundle
    # look for CoH from lower order
    # look for unfinished CoH
    # look for CoH on same host
    coh_finished_deps = [] # mostly deps with 'done' status
    coh_unfinishable_deps = [] # deps with 'failed' or 'over_timed' status
    coh_relevant_deps = [] # other deps

    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.fk_bundle == myC.fk_bundle).\
        filter(database.commands.c.order_in_bundle < myC.order_in_bundle).\
        filter(database.target.c.target_uuid ==  myT.target_uuid).\
        all():
            if q.current_state in ['done']:
                coh_finished_deps.append(q.id)
            elif q.current_state  in ['failed', 'over_timed']:
                coh_unfinishable_deps.append(q.id)
            else:
                coh_relevant_deps.append(q.id)
    session.close()


    if len(coh_unfinishable_deps) > 0: # at least one dep will never be complete, give up
        logging.getLogger().debug("command_on_host #%s: was waiting on %s, all of them beeing unfinishable" % (myCoH.getId(), coh_unfinishable_deps))
        return 'dead'

    if len(coh_relevant_deps) > 0: # at least one dep should be completed, wait
        logging.getLogger().debug("command_on_host #%s: was waiting on %s, to be completed" % (myCoH.getId(), coh_relevant_deps))
        return 'wait'

    logging.getLogger().debug("command_on_host #%s: was waiting on %s, all of them beeing completed" % (myCoH.getId(), coh_finished_deps))
    return 'run'

def localProxyUploadStatus(myCommandOnHostID):
    """ attempt to analyse coh in the same command in order to now how we may advance.
    possible return values:
        - 'waiting': my time is not yet come
        - 'server': I'm an active proxy server
        - 'dead': I'm a client and all proxies seems dead
        - 'error': Something wrong was found in the command (usually mess in priorities)
        - an int: I'm a client and the returned value is the CoH I will use
    """

    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return 'error'

    # as for now, if we previously found a proxy, use it
    # commented out: may break the split proxy model
    #if myCoH.getUsedProxy() != None:
    #    logging.getLogger().debug("scheduler %s: keeping coh #%s as local proxy for #%s" % (SchedulerConfig().name, myCoH.getUsedProxy(), myCommandOnHostID))
    #    return 'keeping'

    # see what to do next
    proxy_mode = getProxyModeForCommand(myCommandOnHostID)
    if proxy_mode == 'queue':
        return localProxyAttemptQueueMode(myCommandOnHostID)
    elif proxy_mode == 'split':
        return localProxyAttemptSplitMode(myCommandOnHostID)
    else:
        logging.getLogger().debug("scheduler %s: command #%s seems to be wrong (bad priorities ?)" % (SchedulerConfig().name, myC.id))
        return 'dead'

def localProxyAttemptQueueMode(myCommandOnHostID):
    # queue mode (serial) implementation of proxy mode
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return 'error'

    smallest_done_upload_order_in_proxy = None
    best_ready_proxy_server_coh = None
    potential_proxy_server_coh = None

    # iterate over CoH which
    # are linked to the same command
    # are not our CoH
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.id == myC.id).\
        filter(database.commands_on_host.c.id != myCoH.id).\
        all():
            if q.uploaded == 'DONE':                                            # got a pal which succeeded in doing its upload
                if q.order_in_proxy != None:                                    # got a potent proxy server
                    if smallest_done_upload_order_in_proxy < q.order_in_proxy:  # keep its id as it seems to be the best server ever
                        smallest_done_upload_order_in_proxy = q.order_in_proxy
                        best_ready_proxy_server_coh = q.id
            elif q.current_state != 'failed':                                   # got a pal which may still do something
                if q.order_in_proxy != None:                                    # got a potential proxy server
                    if myCoH.order_in_proxy == None:                            # i may use this server, as I'm not server myself
                        potential_proxy_server_coh = q.id
                    elif myCoH.order_in_proxy > q.order_in_proxy:               # i may use this server, as it has a lower priority than me
                        potential_proxy_server_coh = q.id
    session.close()

    # we now know:
    # a proxy that may be used
    # a proxy that might be used
    # let's take a decision about our future

    if myCoH.getOrderInProxy() == None:                                 # I'm a client: I MUST use a proxy server ...
        if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
            (current_client_number, max_client_number) = getClientUsageForProxy(best_ready_proxy_server_coh)
            if current_client_number < max_client_number:
                logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID))
                return best_ready_proxy_server_coh
            else:
                logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID, current_client_number))
                return 'waiting'
        elif potential_proxy_server_coh != None:                        # ... and one may become ready => WAITING
            logging.getLogger().debug("scheduler %s: coh #%s still waiting for a local proxy to use" % (SchedulerConfig().name, myCommandOnHostID))
            return 'waiting'
        else:                                                           # ... but all seems dead => ERROR
            logging.getLogger().debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, myCommandOnHostID))
            return 'dead'
    else:                                                               # I'm a server: I MAY use a proxy ...
        if best_ready_proxy_server_coh != None:                         # ... and a proxy seems ready => PROXY CLIENT MODE
            (current_client_number, max_client_number) = getClientUsageForProxy(best_ready_proxy_server_coh)
            if current_client_number < max_client_number:
                logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID))
                return best_ready_proxy_server_coh
            else:
                logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s, but proxy is full (%d clients), so I'm waiting" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID, current_client_number))
                return 'waiting'
        elif potential_proxy_server_coh:                                # ... but a better candidate may become ready => WAITING
            logging.getLogger().debug("scheduler %s: coh #%s still waiting to know if is is local proxy client or server" % (SchedulerConfig().name, myCommandOnHostID))
            return 'waiting'
        else:                                                           # ... and other best candidates seems dead => PROXY SERVER MODE
            logging.getLogger().debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, myCommandOnHostID))
            return 'server'

def localProxyAttemptSplitMode(myCommandOnHostID):
    # split mode (parallel) implementation of proxy mode

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
        final_uuid = LocalProxiesUsageTracking().take_one(alive_proxies.keys(), myC.getId())
        if not final_uuid: # not free proxy, wait
            logging.getLogger().debug("scheduler %s: coh #%s wait for a local proxy for to be usable" % (SchedulerConfig().name, myCommandOnHostID))
            return 'waiting'
        else: # take a proxy in alive proxies
            final_proxy = alive_proxies[final_uuid]
            logging.getLogger().debug("scheduler %s: coh #%s found coh #%s as local proxy, taking one slot (%d left)" % (SchedulerConfig().name, myCommandOnHostID, final_proxy, LocalProxiesUsageTracking().how_much_left_for(final_uuid, myC.getId())))
            return final_proxy

    def __processProbe(result, uuid, proxy):
        logging.getLogger().debug("scheduler %s: coh #%s probed on %s, got %s" % (SchedulerConfig().name, proxy, uuid, result))
        return (result, uuid, proxy)

    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return 'error'
    if myCoH.getOrderInProxy() == None:                                 # I'm a client: I MUST use a proxy server ...
        temp_dysfunc_proxy = list() # proxies with no data (UPLOADED != DONE)
        def_dysfunc_proxy = list()  # proxies with no data (UPLOADED != DONE) and which definitely wont't process further (current_state != scheduled)
        available_proxy = list()    # proxies with complete data (UPLOADED = DONE)

        # iterate over CoH which
        # are linked to the same command
        # are not our CoH
        # are proxy server
        session = sqlalchemy.orm.create_session()
        database = MscDatabase()
        for q in session.query(CommandsOnHost).\
            select_from(database.commands_on_host.join(database.commands).join(database.target)).\
            filter(database.commands.c.id == myC.id).\
            filter(database.commands_on_host.c.id != myCoH.id).\
            filter(database.commands_on_host.c.order_in_proxy != None).\
            all():
                # got 4 categories here:
                #  - DONE and not DONE
                #  - scheduled and not scheduled
                # => upload DONE, (scheduled or not): proxy free to use (depnding on nb of clients, see below)
                # => upload !DONE + (failed, over_timed) => will never be available => defin. failed
                # => upload !DONE + ! (failed or over_timed) => may be available in some time => temp. failed
                if q.current_state in ('failed', 'over_timed', 'stopped', 'stop'):
                    def_dysfunc_proxy.append(q.id)
                elif q.uploaded == 'DONE':
                    available_proxy.append(q.id)
                else:
                    temp_dysfunc_proxy.append(q.id)
        session.close()

        if len(available_proxy) == 0: # not proxy seems ready ?
            if len(temp_dysfunc_proxy) == 0: # and others seems dead
                logging.getLogger().debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, myCommandOnHostID))
                return 'dead'
            else:
                logging.getLogger().debug("scheduler %s: coh #%s wait for a local proxy to be ready" % (SchedulerConfig().name, myCommandOnHostID))
                return 'waiting'

        deffered_list = list()

        for proxy in available_proxy: # proxy is the proxy coh id
            (proxyCoH, proxyC, proxyT) = gatherCoHStuff(proxy)
            d = probeClient(
                proxyT.getUUID(),
                proxyT.getFQDN(),
                proxyT.getShortName(),
                proxyT.getIps(),
                proxyT.getMacs()
            )
            d.addCallback(__processProbe, proxyT.getUUID(), proxy)
            deffered_list.append(d)
        dl = twisted.internet.defer.DeferredList(deffered_list)
        dl.addCallback(__processProbes)
        return dl

    else:                                                               # I'm a server: let's upload
        logging.getLogger().debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, myCommandOnHostID))
        return 'server'

def getClientUsageForProxy(proxyCommandOnHostID):
    # count the (current number, max number) of clients using this proxy
    # a client is using a proxy if:
    # - getUsedProxy == proxyCommandOnHostID
    # current_state == upload_in_progress
    # to save some time, iteration is done as usual (on command from coh)
    (myCoH, myC, myT) = gatherCoHStuff(proxyCommandOnHostID)
    if myCoH == None: # current_client_number == max_client_number => dont use this target as a possible proxy
        return (0, 0)
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    client_count = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.id == myC.id).\
        filter(database.commands_on_host.c.fk_use_as_proxy == myCoH.id).\
        filter(database.commands_on_host.c.current_state == 'upload_in_progress').\
        count()
    session.close()
    return (client_count, myCoH.getMaxClientsPerProxy())

def getProxyModeForCommand(myCommandOnHostID):
    # Preliminar iteration to gather information about this command
    # the idea being to obtain some informations about what's going on
    # we are looking for the following elements
    # - the amount of priorities:
    #   + only one => split mode (returns "split")
    #   + as many as proxies => queue mode (returns "queue")
    #   + no / not enough priorities => error condition (returns False)

    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return False

    spotted_priorities = dict()

    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.id == myC.id).\
        all():
            if q.order_in_proxy != None: # some potential proxy
                if q.order_in_proxy in spotted_priorities:
                    spotted_priorities[q.order_in_proxy] += 1
                else:
                    spotted_priorities[q.order_in_proxy] = 1
    session.close()

    if len(spotted_priorities) == 0:
        return False
    elif len(spotted_priorities) == 1: # only one priority for all => split mode
        logging.getLogger().debug("scheduler %s: command #%s is in split proxy mode" % (SchedulerConfig().name, myC.id))
        return 'split'
    elif len(spotted_priorities) == reduce(lambda x, y: x+y, spotted_priorities.values()): # one priority per proxy => queue mode
        logging.getLogger().debug("scheduler %s: command #%s is in queue proxy mode" % (SchedulerConfig().name, myC.id))
        return 'queue'
    else: # other combinations are errors
        logging.getLogger().debug("scheduler %s: can'f guess proxy mode for command #%s" % (SchedulerConfig().name, myC.id))
        return False

def localProxyMayContinue(myCommandOnHostID):
    """ attempt to analyse coh in the same command in order to now how we may advance.
    """
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return False # TODO : when an error occur, do we want to clean the local proxy ?

    # Clean algorithm:
    # client => always cleanup
    # server => cleanup only if *everybody" are in one of the following state:
    #   - upload done
    #   - upload ignored
    #   - failed
    #   - over_timed
    # to prevent race condition, not check is perform to count only our clients but everybody client

    if myCoH.isLocalProxy(): # proxy server, way for clients to be done
        logging.getLogger().debug("scheduler %s: checking if we may continue coh #%s" % (SchedulerConfig().name, myCommandOnHostID))
        our_client_count = 0
        if myC.hasToUseQueueProxy():
            session = sqlalchemy.orm.create_session()
            database = MscDatabase()
            our_client_count = session.query(CommandsOnHost).\
                select_from(database.commands_on_host.join(database.commands).join(database.target)).\
                filter(database.commands.c.id == myC.id).\
                filter(database.commands_on_host.c.id != myCoH.id).\
                filter(database.commands_on_host.c.uploaded != 'DONE').\
                filter(database.commands_on_host.c.uploaded != 'IGNORED').\
                filter(database.commands_on_host.c.current_state != 'failed').\
                filter(database.commands_on_host.c.current_state != 'done').\
                filter(database.commands_on_host.c.current_state != 'over_timed').\
                count()
            logging.getLogger().debug("scheduler %s: found %s coh to be uploaded in command #%s" % (SchedulerConfig().name, our_client_count, myC.id))
            session.close()
        elif myC.hasToUseSplitProxy():
            session = sqlalchemy.orm.create_session()
            database = MscDatabase()
            our_client_count = session.query(CommandsOnHost).\
                select_from(database.commands_on_host.join(database.commands).join(database.target)).\
                filter(database.commands.c.id == myC.id).\
                filter(database.commands_on_host.c.id != myCoH.id).\
                filter(database.commands_on_host.c.order_in_proxy == None).\
                filter(database.commands_on_host.c.uploaded != 'DONE').\
                filter(database.commands_on_host.c.uploaded != 'IGNORED').\
                filter(database.commands_on_host.c.current_state != 'failed').\
                filter(database.commands_on_host.c.current_state != 'done').\
                filter(database.commands_on_host.c.current_state != 'over_timed').\
                count()
            logging.getLogger().debug("scheduler %s: found %s coh to be uploaded in command #%s" % (SchedulerConfig().name, our_client_count, myC.id))
            session.close()
        # proxy tracking update
        if our_client_count != 0:
            LocalProxiesUsageTracking().create_proxy(myT.getUUID(), myCoH.getMaxClientsPerProxy(), myC.getId())
            logging.getLogger().debug("scheduler %s: (re-)adding %s (#%s) to proxy pool" % (SchedulerConfig().name, myT.getUUID(), myC.getId()))
        else:
            LocalProxiesUsageTracking().delete_proxy(myT.getUUID(), myC.getId())
            logging.getLogger().debug("scheduler %s: (re-)removing %s (#%s) from proxy pool" % (SchedulerConfig().name, myT.getUUID(), myC.getId()))
        return our_client_count == 0
    else:
        return True

def startAllCommands(scheduler_name, commandIDs = []):
    logger = logging.getLogger()

    if commandIDs:
        logger.debug('scheduler "%s": START: Starting commands %s' % (scheduler_name, commandIDs))
    else:
        logger.debug('scheduler "%s": START: Starting all commands' % scheduler_name)
    return twisted.internet.threads.deferToThread(gatherIdsToStart, scheduler_name, commandIDs).addCallback(sortCommands)

def gatherIdsToStart(scheduler_name, commandIDs = []):

    session = sqlalchemy.orm.create_session()
    database = MscDatabase()

    # gather candidates:
    # ignore completed tasks (done / failed / over_timed)
    # ignore paused tasks
    # ignore stopped tasks
    # ignore tasks already in progress (excepted WOL in progress 'cause of the tempo)
    # ignore tasks which failed
    # ignore tasks with no retries left
    # take tasks with next launch time in the future
    #
    # Please pay attention that as nowhere is is specified the commands start_date and end_date
    # fields 'special' values ("0000-00-00 00:00:00" and "2031-12-31 23:59:59"), I
    # consider that:
    #  - start_date:
    #   + "0000-00-00 00:00:00" means "as soon as possible",
    #   + "2031-12-31 23:59:59" means "never",
    #  - end_date:
    #   + "0000-00-00 00:00:00" means "never" (yeah, that's f*****g buggy, but how really matter the *specs*, hu ?),
    #   + "2031-12-31 23:59:59" means "never",
    #
    # consequently, I may process tasks:
    #     with start_date = "0000-00-00 00:00:00" or start_date <= now
    # and start_date <> "2031-12-31 23:59:59"
    # and end_date = "0000-00-00 00:00:00" or end_date = "2031-12-31 23:59:59" or end_date >= now
    #
    #
    # TODO: check command state integrity AND command_on_host state integrity in a separtseparate function

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    soon = time.strftime("0000-00-00 00:00:00")
    later = time.strftime("2031-12-31 23:59:59")

    commands_query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)).\
        filter(database.commands_on_host.c.current_state != 'done').\
        filter(database.commands_on_host.c.current_state != 'failed').\
        filter(database.commands_on_host.c.current_state != 'over_timed').\
        filter(database.commands_on_host.c.current_state != 'pause').\
        filter(database.commands_on_host.c.current_state != 'stop').\
        filter(database.commands_on_host.c.current_state != 'upload_in_progress').\
        filter(database.commands_on_host.c.current_state != 'execution_in_progress').\
        filter(database.commands_on_host.c.current_state != 'delete_in_progress').\
        filter(database.commands_on_host.c.current_state != 'inventory_in_progress').\
        filter(database.commands_on_host.c.current_state != 'reboot_in_progress').\
        filter(database.commands_on_host.c.current_state != 'halt_in_progress').\
        filter(database.commands_on_host.c.next_launch_date <= now).\
        filter(sqlalchemy.or_(
            database.commands.c.start_date == soon,
            database.commands.c.start_date <= now)
        ).\
        filter(database.commands.c.start_date != later).\
        filter(sqlalchemy.or_(
            database.commands.c.end_date == soon,
            database.commands.c.end_date == later,
            database.commands.c.end_date > now)
        ).\
        filter(sqlalchemy.or_(
            database.commands_on_host.c.scheduler == '',
            database.commands_on_host.c.scheduler == scheduler_name,
            database.commands_on_host.c.scheduler == None)
        )

    if commandIDs:
        commands_query = commands_query.filter(database.commands.c.id.in_(commandIDs))

    commands_to_perform = []
    for q in commands_query.all():
        commands_to_perform.append(q.id)

    session.close()
    return commands_to_perform

def sortCommands(commands_to_perform):
    """
    Process CommandsOnHost objects list and fires needed deferred objects to
    perform the commands on background.
    """

    def _cb(result, tocome_distribution):
        deffereds = [] # will hold all deferred

        ids_list = [] # will contain the IDs from commands to run
        # list is pre-filled in case of something goes wrong below
        for ids in tocome_distribution.values():
            ids_list += ids

        if len(ids_list) == 0:
            logging.getLogger().info('scheduler "%s": START: starting %d commands' % (SchedulerConfig().name, len(ids_list)))
            return deffereds

        logging.getLogger().debug("scheduler %s: sorting the following commands: %s" % (SchedulerConfig().name, ids_list))
        try: # this code is not well tested: let's protect it :D
            # tocome_distribution is a dict, keys are the current group names, values are the ids (array) of commands to launch
            current_distribution = dict()
            for launcher in result:
                for group in result[launcher]['by_group']:
                    if not group in current_distribution:
                        current_distribution[group] = result[launcher]['by_group'][group]['running']
                    else:
                        current_distribution[group] += result[launcher]['by_group'][group]['running']
            # => now current_distribution is a dict, keys are the current group names, values are the used slots per group fully aggregated over all launchers

            # lets build an array with aggregated stats
            aggregated_distribution = dict()
            for key in tocome_distribution:
                if key not in aggregated_distribution:
                    aggregated_distribution[key] = {'tocome': 0, 'current': 0}
                aggregated_distribution[key]['tocome'] = len(tocome_distribution[key])
            for key in current_distribution:
                if key not in aggregated_distribution:
                    aggregated_distribution[key] = {'tocome': 0, 'current': 0}
                aggregated_distribution[key]['current'] = current_distribution[key]
            # we now got a dict, which for each group contains how mush stuff we are doing, and how much stuff we want to add

            # the next step is to know how much command we want to run
            # we got two options here:
            # - either run as many commands as possible while staying below a certain ceil per group
            # - or run as any commands as possible while keeping deployment equilibrated group per group

            # first case: we want to
            # - run as many commands as possible,
            # - at last obtain as many commands running as configured in scheduler.ini
            # thus we have reach max_slots / max group count
            to_reach = int(SchedulerConfig().max_slots / getMaxNumberOfGroups())

            # second case: we want to
            # - run as many commands as possible,
            # - at last obtain the same ammount of running command per group
            # so the idea is to find the group where tocome + current is minimum,
            # then raise all groups to this level
            # the calculs are done here, but please read carefuly:
            # !!!!! DO NOT USE THIS VALUE !!!!!
            # IT MAY PREVENT SCHEDULER TO RUN AT FULL CAPACITY IF A GROUP IS ALMOST EMPTY
            # to_reach = min(map(lambda(x,y): y['current'] + y['tocome'], aggregated_distribution.items()))

            # we can now obtain the full list of command_id
            ids_list = []
            for group in tocome_distribution.keys():
                for i in range(0, to_reach - aggregated_distribution[group]['current']): # some space left in this group
                    if aggregated_distribution[group]['tocome'] > 0:                     # and some stuff to add to this group
                        if len(tocome_distribution[group]):
                            ids_list.append(tocome_distribution[group].pop(0))
            random.shuffle(ids_list)
            logging.getLogger().debug("scheduler %s: commands sorted: %s" % (SchedulerConfig().name, ids_list))
        except: # hum, something goes weird, try to get ids_list anyway
            logging.getLogger().debug("scheduler %s: something goes wrong while sorting commands, keeping list untouched" % (SchedulerConfig().name))

        logging.getLogger().info('scheduler "%s": START: %d commands to start' % (SchedulerConfig().name, len(ids_list)))
        for id in ids_list:
            deffered = runCommand(id)
            if deffered:
                deffereds.append(deffered)
        return deffereds

    # build array of commands to perform
    tocome_distribution = dict()

    # a few pre-randomization to avoid dead locks
    random.shuffle(commands_to_perform)

    for command_id in commands_to_perform:
        (myCoH, myC, myT) = gatherCoHStuff(command_id)
        if myCoH == None:
            continue
        command_group = getClientGroup(myT)
        if not command_group in tocome_distribution:
            tocome_distribution[command_group] = [command_id]
        else:
            tocome_distribution[command_group].append(command_id)

    # build array of commands being processed by available launchers
    return getLaunchersBalance().\
        addCallback(_cb, tocome_distribution)

def running_states_sqlalchemy(database):
    return sqlalchemy.or_(
        database.commands_on_host.c.current_state == 'upload_in_progress',
        database.commands_on_host.c.current_state == 'execution_in_progress',
        database.commands_on_host.c.current_state == 'delete_in_progress',
        database.commands_on_host.c.current_state == 'inventory_in_progress'
    )

def getRunningCommandsOnHost(session, scheduler_name):
    database = MscDatabase()
    return session.query(CommandsOnHost).\
        select_from(database.commands_on_host).\
        filter(
            running_states_sqlalchemy(database)
        ).filter(sqlalchemy.or_(
            database.commands_on_host.c.scheduler == '',
            database.commands_on_host.c.scheduler == scheduler_name,
            database.commands_on_host.c.scheduler == None)
        ).all()
    
def stopElapsedCommands(scheduler_name):
    logger = logging.getLogger()

    logger.debug('scheduler "%s": STOP: Stopping all commands' % scheduler_name)

    return twisted.internet.threads.deferToThread(gatherIdsToStop, scheduler_name).addCallback(stopCommandsOnHosts)

def gatherIdsToStop(scheduler_name):
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()

    # this loop only put the current_state in over_timed, but as the coh are not running, we dont need to stop them.
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)).\
        filter(sqlalchemy.or_(
            database.commands_on_host.c.scheduler == '',
            database.commands_on_host.c.scheduler == scheduler_name,
            database.commands_on_host.c.scheduler == None)
        ).filter(sqlalchemy.and_(
            database.commands.c.end_date <= now,
            database.commands.c.end_date != '0000-00-00 00:00:00')
        ).filter(sqlalchemy.and_(
            database.commands_on_host.c.current_state != 'failed',
            database.commands_on_host.c.current_state != 'over_timed',
            database.commands_on_host.c.current_state != 'done')
        ).all():

        (myCoH, myC, myT) = gatherCoHStuff(q.id)
        if myCoH == None:
            continue
        logging.getLogger().info("Scheduler: over timed command_on_host #%s"%(str(q.id)))
        myCoH.setStateOverTimed()

    # gather candidates:
    # retain tasks already in progress
    # take tasks with end_date in the future, but not null
    ids = list()
    for q in getRunningCommandsOnHost(session, scheduler_name):
        # enter the maze: tag command as to-be-stopped if relevant

        (myCoH, myC, myT) = gatherCoHStuff(q.id)
        if myCoH == None:
            continue
        if not myC.inDeploymentInterval(): # stops command not in interval
            ids.append(q.id)
        elif myC.end_date.__str__() != '0000-00-00 00:00:00' and myC.end_date.__str__()  <= time.strftime("%Y-%m-%d %H:%M:%S"):
            # change the CoH current_state (we are not going to be able to try to start this coh ever again)
            myCoH.setStateOverTimed()
            ids.append(q.id)

    session.close()
    logging.getLogger().debug("Scheduler: stopping %s" % ids)
    return ids

def setCommandsOnHostAsStopped(ids):
    try:
        for id in ids:
            (myCoH, myC, myT) = gatherCoHStuff(id)
            myCoH.current_state = 'stopped'
            myCoH.flush()
    except Exception, e:
        logging.getLogger().debug("Scheduler: error %s"%(str(e)))

def cleanStates(scheduler_name):
    session = sqlalchemy.orm.create_session()
    database = MscDatabase()
    logger = logging.getLogger()

    logger.info("Scheduler: cleanStates")
    # get all running coh ids
    ids = map(lambda q: q.id, getRunningCommandsOnHost(session, scheduler_name))
    session.close()

    cleanStatesAllRunningIds(ids)
    return None

def cleanStatesAllRunningIds(ids):
    def treatBadStateCommandsOnHost(result, ids = ids):
        fails = []
        for id in ids:
            success = False
            for running_ids in result:
                if id in running_ids[1]:
                    success = True
                    continue
            if not success:
                fails.append(id)
        logging.getLogger().info('scheduler "%s": CLEAN STATES: fails : %s' % (SchedulerConfig().name, str(fails)))
        setCommandsOnHostAsStopped(fails)

    deffereds = [] # will hold all deferred
    for launcher in SchedulerConfig().launchers_uri.values():
        deffered = callOnLauncher(None, launcher, 'get_process_ids')
        if deffered:
            deffereds.append(deffered)

    twisted.internet.defer.DeferredList(deffereds).addCallbacks(
        treatBadStateCommandsOnHost,
        lambda reason: logging.getLogger().error('scheduler "%s": CLEAN STATES: error %s'  % (SchedulerConfig().name, reason.value))
    )

def stopCommandsOnHosts(ids):
    deffereds = [] # will hold all deferred
    logging.getLogger().info('scheduler "%s": STOP: %d commands to stop' % (SchedulerConfig().name, len(ids)))
    if len(ids) > 0:
        for launcher in SchedulerConfig().launchers_uri.values():
            deffered = callOnLauncher(None, launcher, 'term_processes', ids)
            if deffered:
                deffereds.append(deffered)
    return deffereds

def stopCommand(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return False
    logger = logging.getLogger()
    logger.info("going to terminate command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
    logger.debug("command_on_host state is %s" % myCoH.toH())
    logger.debug("command state is %s" % myC.toH())
    for launcher in SchedulerConfig().launchers_uri.values():
        callOnLauncher(None, launcher, 'term_process', myCommandOnHostID)
    return True

def startCommand(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return False
    logger = logging.getLogger()
    if myCoH.scheduler not in [SchedulerConfig().name, '', None]:
        logger.warn("attempt to start command_on_host #%s from command #%s using the wrong scheduler" % (myCoH.getId(), myCoH.getIdCommand()))
        return False

    logger.info("going to start command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
    logger.debug("command_on_host state is %s" % myCoH.toH())
    logger.debug("command state is %s" % myC.toH())
    runCommand(myCommandOnHostID)
    return True

def startTheseCommands(scheduler_name, commandIDs):
    """
    Tell the scheduler to immediately start a given command
    """
    return startAllCommands(scheduler_name, commandIDs)

def runCommand(myCommandOnHostID):
    """
        Just a simple start point, chain-load on Upload Phase
    """

    if checkAndFixCommand(myCommandOnHostID):
        return runWOLPhase(myCommandOnHostID)

def checkAndFixCommand(myCommandOnHostID):
    """
        pass command through a filter, trying to guess is command is valid
        four cases here:
         - command IS valid, return True
         - command is ALMOST valid, fix it, return True
         - command is a little invalid, neutralize it, return False
         - command IS completely messed-up, return False
    """
    logger = logging.getLogger()

    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)

    # a simple database checkup
    if myCoH == None:
        return False

    # give up in comman not in interval
    if not myC.inDeploymentInterval():
        return False

    if myC.isPartOfABundle():
        logger.debug("command_on_host #%s: part of bundle %s, order %s " % (myCoH.getId(), myC.getBundleId(), myC.getOrderInBundle()))
        deps_status = getDependancies(myCommandOnHostID)
        # give up if bundle and can't guess dependancies
        if type(deps_status) == bool and not deps_status:
            logger.debug("command_on_host #%s: failed to get dependencies" % (myCoH.getId()))
            return False
        # give up if bundle and some dependancies remain
        if deps_status == "dead":
            myCoH.setStateFailed()
            return False # give up, some deps have failed
        if deps_status == "wait":
            return False # wait, some deps has to be done
        if deps_status != "run":
            return False # werd, should not append

    logger.debug("going to do command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
    logger.debug("command_on_host state is %s" % myCoH.toH())
    logger.debug("command state is %s" % myC.toH())
    myCoH.setStartDate()
    return True

def runWOLPhase(myCommandOnHostID):
    """
        Attempt do see if a wake-on-lan should be done
    """
    def _cb(result):
        """ results
            0 => ping NOK => do WOL
            1 => ping OK, ssh NOK  => do WOL (computer may just have awoken)
            2 => ping OK, ssh OK => don't do WOL
        """
        if result == 2:
            logger.info("command_on_host #%s: do not wol (target already up)" % myCommandOnHostID)
            updateHistory(myCommandOnHostID, 'wol_done', 0, "skipped: host already up", "")
            myCoH.setWOLIgnored()
            myCoH.setStateScheduled()
            return runUploadPhase(myCommandOnHostID)
        logger.info("command_on_host #%s: do wol (target not up)" % myCommandOnHostID)
        return performWOLPhase(myCommandOnHostID)

    def _eb(reason):
        logger.warn("command_on_host #%s: while probing: %s" % (myCommandOnHostID, reason))
        logger.info("command_on_host #%s: do wol (target not up)" % myCommandOnHostID)
        return performWOLPhase(myCommandOnHostID)

    # check for WOL condition in order to give up if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None

    logger = logging.getLogger()
    logger.info("command_on_host #%s: WOL phase" % myCommandOnHostID)

    if myCoH.isWOLRunning():            # WOL in progress
        if myCoH.getLastWOLAttempt() != None: # WOL *really* progress, hem
            if (datetime.datetime.now()-myCoH.getLastWOLAttempt()).seconds < (SchedulerConfig().max_wol_time + 300):
                # we should wait a little more
                return None
            else:
                # we already pass the delay from at least 300 seconds, let's continue
                # FIXME: dirty fix, better use a sem system to handle collision situations :/
                logging.getLogger().warn("command_on_host #%s: WOL should have been set as done !" % (myCommandOnHostID))
                myCoH.setWOLDone()
                myCoH.setStateScheduled()
                return runUploadPhase(myCommandOnHostID)
        else: # WOL marked as "in progress", but no time given ?!
            # return None to avoid some possible race conditions
            return None

        logger.info("command_on_host #%s: WOL still running" % myCommandOnHostID)
        return None
    if myCoH.isWOLIgnored(): # wol has already been ignored, jump to next stage
        logger.info("command_on_host #%s: wol ignored" % myCoH.getId())
        return runUploadPhase(myCommandOnHostID)
    if myCoH.isWOLDone(): # wol has already already done, jump to next stage
        logger.info("command_on_host #%s: wol done" % myCoH.getId())
        return runUploadPhase(myCommandOnHostID)
    if not myCoH.isWOLImminent():       # nothing to do right now, give out
        logger.info("command_on_host #%s: not the right time to WOL" % myCoH.getId())
        return None
    if not myC.hasToWOL(): # don't have to WOL
        logger.info("command_on_host #%s: do not wol" % myCoH.getId())
        myCoH.setWOLIgnored()
        myCoH.setStateScheduled()
        return runUploadPhase(myCommandOnHostID)

    # WOL has to be performed, but only if computer is down (ie. no ping)
    uuid = myT.target_uuid
    fqdn = myT.target_name
    shortname = myT.target_name
    ips = myT.target_ipaddr.split('||')
    macs = myT.target_macaddr.split('||')
    mydeffered = pingAndProbeClient(uuid, fqdn, shortname, ips, macs)
    mydeffered.\
        addCallback(_cb).\
        addErrback(_eb)
    return mydeffered

def performWOLPhase(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    myCoH.setLastWOLAttempt()
    myCoH.setWOLInProgress()
    updateHistory(myCommandOnHostID, 'wol_in_progress')
    myCoH.setStateWOLInProgress()

    # perform call
    mydeffered = callOnBestLauncher(myCommandOnHostID,
        'wol',
        False,
        myT.target_macaddr.split('||'),
        myT.target_bcast.split('||')
    )

    mydeffered.\
        addCallback(parseWOLResult, myCommandOnHostID).\
        addErrback(parseWOLError, myCommandOnHostID)
    return mydeffered


def runUploadPhase(myCommandOnHostID):
    """
        Handle first Phase: upload time
    """
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: copy phase" % myCommandOnHostID)
    if myCoH == None:
        return None

    # check for upload condition in order to give up if needed
    if myCoH.isUploadRunning(): # upload still running, immediately returns
        logging.getLogger().info("command_on_host #%s: still running" % myCoH.getId())
        return None
    if myCoH.isUploadIgnored(): # upload has already been ignored, jump to next stage
        logging.getLogger().info("command_on_host #%s: upload ignored" % myCoH.getId())
        return runExecutionPhase(myCoH.getId())
    if myCoH.isUploadDone(): # upload has already already done, jump to next stage
        logging.getLogger().info("command_on_host #%s: upload done" % myCoH.getId())
        return runExecutionPhase(myCoH.getId())
    if not myCoH.isUploadImminent(): # nothing to do right now, give out
        logging.getLogger().info("command_on_host #%s: nothing to upload right now" % myCoH.getId())
        return None
    if not myC.hasSomethingToUpload(): # nothing to upload here, jump to next stage
        logging.getLogger().info("command_on_host #%s: nothing to upload" % myCoH.getId())
        myCoH.setUploadIgnored()
        myCoH.setStateScheduled()
        return runExecutionPhase(myCoH.getId())

    # if we are here, upload has either previously failed or never be done
    # do copy here

    # fullfil used proxy (if we can)
    if myC.hasToUseProxy():
        d = twisted.internet.defer.maybeDeferred(localProxyUploadStatus, myCommandOnHostID)
        d.addCallback(_cbChooseUploadMode, myCoH, myC, myT)
        return d

    return _chooseUploadMode(myCoH, myC, myT)

def _cbChooseUploadMode(result, myCoH, myC, myT):
    if result == 'waiting':
        logging.getLogger().info("command_on_host #%s: waiting for a local proxy" % myCoH.getId())
        return None
    elif result == 'dead':
        logging.getLogger().warn("command_on_host #%s: waiting for a local proxy which will never be ready !" % myCoH.getId())
        return None
    elif result == 'server':
        logging.getLogger().info("command_on_host #%s: becoming local proxy server" % myCoH.getId())
        myCoH.setUsedProxy(myCoH.getId()) # special case: this way we know we were server
    elif result == 'keeping':
        logging.getLogger().info("command_on_host #%s: keeping previously acquiered local proxy settings" % myCoH.getId())
    else:
        logging.getLogger().info("command_on_host #%s: becoming local proxy client" % myCoH.getId())
        myCoH.setUsedProxy(result)
    return _chooseUploadMode(myCoH, myC, myT)

def _chooseUploadMode(myCoH, myC, myT):
    logger = logging.getLogger()
    # check if we have enough informations to reach the client
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('transfert'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parsePushError, myCoH.getId())

    # first attempt to guess is mirror is local (push) or remove (pull) or through a proxy
    if myCoH.isProxyClient(): # proxy client
        d = _runProxyClientPhase(client, myC, myCoH)
    elif re.compile('^file://').match(myT.mirrors): # local mirror starts by "file://" : prepare a remote_push
        d = _runPushPhase(client, myC, myCoH, myT)
    else: # remote push/pull

        try: # mirror is formated like this: https://localhost:9990/mirror1||https://localhost:9990/mirror1
            mirrors = myT.mirrors.split('||')
        except:
            logger.warn("command_on_host #%s: target.mirror do not seems to be as expected, got '%s', skipping command" % (myCoH.getId(), myT.mirrors))
            return None

        # Check mirrors
        if len(mirrors) != 2:
            logger.warn("command_on_host #%s: we need two mirrors ! '%s'" % (myCoH.getId(), myT.mirrors))
            return None
        mirror = mirrors[0]
        fbmirror = mirrors[1]

        ma = pulse2.apis.clients.mirror.Mirror(mirror)
        d = ma.isAvailable(myC.package_id)
        d.addCallback(_cbRunPushPullPhaseTestMirror, mirror, fbmirror, client, myC, myCoH)

    return d

def _cbRunPushPullPhaseTestMirror(result, mirror, fbmirror, client, myC, myCoH):
    if result:
        return _runPushPullPhase(mirror, fbmirror, client, myC, myCoH)
    else:
        # Test the fallback mirror
        return _cbRunPushPullPhaseTestFallbackMirror(result, mirror, fbmirror, client, myC, myCoH)

def _cbRunPushPullPhaseTestFallbackMirror(result, mirror, fbmirror, client, myC, myCoH):
    if fbmirror != mirror:
        # Test the fallback mirror only if the URL is the different than the
        # primary mirror
        ma = pulse2.apis.clients.mirror.Mirror(fbmirror)
        d = ma.isAvailable(myC.package_id)
        d.addCallback(_cbRunPushPullPhase, mirror, fbmirror, client, myC, myCoH, True)
        return d
    else:
        # Go to upload phase, but pass False to tell that the package is not
        # available on the fallback mirror too
        _cbRunPushPullPhase(False, mirror, fbmirror, client, myC, myCoH)

def _cbRunPushPullPhase(result, mirror, fbmirror, client, myC, myCoH, useFallback = False):
    if result:
        # The package is available on a mirror, start upload phase
        return _runPushPullPhase(mirror, fbmirror, client, myC, myCoH, useFallback)
    else:
        updateHistory(myCoH.id, 'upload_failed', '0', '', 'Package \'%s\' is not available on any mirror' % (myC.package_id))
        myCoH.switchToUploadFailed(myC.getNextConnectionDelay(), False) # report this as an error, but do not decrement attempts
        logging.getLogger().warn("command_on_host #%s: Package '%s' is not available on any mirror" % (myCoH.id, myC.package_id))

def _runProxyClientPhase(client, myC, myCoH):
    # fulfill protocol
    client['protocol'] = 'rsyncproxy'

    # get informations about our proxy
    (proxyCoH, proxyC, proxyT) = gatherCoHStuff(myCoH.getUsedProxy())
    if proxyCoH == None:
        return twisted.internet.defer.fail(Exception("Cant access to CoH")).addErrback(parsePushError, myCoH.getId())
    proxy = { 'host': chooseClientIP(proxyT), 'uuid': proxyT.getUUID(), 'maxbw': proxyC.maxbw, 'client_check': getClientCheck(proxyT), 'server_check': getServerCheck(proxyT), 'action': getAnnounceCheck('transfert'), 'group': getClientGroup(proxyT)}
    if not proxy['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get proxy IP address")).addErrback(parsePushError, myCoH.getId())
    # and fill struct
    # only proxy['host'] used until now
    client['proxy'] = {
        'command_id': myCoH.getUsedProxy(),
        'host': proxy['host'],
        'uuid': proxy['uuid']
    }

    # build file list
    files_list = []
    for file in myC.files.split("\n"):
        fname = file.split('##')[1]
        if re.compile('^/').search(fname):
            fname = re.compile('^/[^/]*/(.*)$').search(fname).group(1) # keeps last compontent of path
        files_list.append(fname)

    # update command state
    myCoH.setUploadInProgress()
    myCoH.setStateUploadInProgress()

    # prepare deffereds
    if SchedulerConfig().mode == 'sync':
        updateHistory(myCoH.getId(), 'upload_in_progress')
        mydeffered = callOnBestLauncher(
            myCoH.getId(),
            'sync_remote_pull',
            False,
            myCoH.getId(),
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePushResult, myCoH.getId()).\
            addErrback(parsePushError, myCoH.getId())
    elif SchedulerConfig().mode == 'async':
        # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
        mydeffered = callOnBestLauncher(
            myCoH.getId(),
            'async_remote_pull',
            False,
            myCoH.getId(),
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePushOrder, myCoH.getId()).\
            addErrback(parsePushError, myCoH.getId())
    else:
        mydeffered = None

    return mydeffered

def _runPushPhase(client, myC, myCoH, myT):
    # fulfill protocol
    client['protocol'] = 'rsyncssh'

    # build file list
    files_list = list()
    for file in myC.files.split("\n"):
        fname = file.split('##')[1]
        if re.compile('^/').search(fname):
            fname = re.compile('^/(.*)$').search(fname).group(1)
        files_list.append(os.path.join(re.compile('^file://(.*)$').search(myT.mirrors).group(1), fname)) # get folder on mirror

    # update command state
    myCoH.setUploadInProgress()
    myCoH.setStateUploadInProgress()

    # prepare deffereds
    if SchedulerConfig().mode == 'sync':
        updateHistory(myCoH.getId(), 'upload_in_progress')
        mydeffered = callOnBestLauncher(
            myCoH.getId(),
            'sync_remote_push',
            False,
            myCoH.getId(),
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePushResult, myCoH.getId()).\
            addErrback(parsePushError, myCoH.getId())
    elif SchedulerConfig().mode == 'async':
        # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
        mydeffered = callOnBestLauncher(
            myCoH.getId(),
            'async_remote_push',
            False,
            myCoH.getId(),
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePushOrder, myCoH.getId()).\
            addErrback(parsePushError, myCoH.getId())
    else:
        mydeffered = None

    # run deffereds
    return mydeffered

def _runPushPullPhase(mirror, fbmirror, client, myC, myCoH, useFallback = False):
    if useFallback:
        msg = 'Package \'%s\' is not available on mirror %s\nPackage \'%s\' is available on fallback mirror %s' % (myC.package_id, mirror, myC.package_id, fbmirror)
        mirror = fbmirror
    else:
        msg = 'Package \'%s\' is available on mirror %s' % (myC.package_id, mirror)
    updateHistory(myCoH.id, 'upload_in_progress', '0', '', msg)
    logging.getLogger().debug("command_on_host #%s: Package '%s' is available on %s" % (myCoH.id, myC.package_id, mirror))
    ma = pulse2.apis.clients.mirror.Mirror(mirror)
    fids = []
    for line in myC.files.split("\n"):
        fids.append(line.split('##')[0])
    d = ma.getFilesURI(fids)
    d.addCallback(_cbRunPushPullPhasePushPull, mirror, fbmirror, client, myC, myCoH, useFallback)

def _cbRunPushPullPhasePushPull(result, mirror, fbmirror, client, myC, myCoH, useFallback):
    files_list = result
    file_uris = {}
    choosen_mirror = mirror
    if not False in files_list and not '' in files_list:
        # build a dict with the protocol and the files uris
        if re.compile('^http://').match(choosen_mirror) or re.compile('^https://').match(choosen_mirror): # HTTP download
            file_uris = {'protocol': 'wget', 'files': files_list}
        elif re.compile('^smb://').match(choosen_mirror): # TODO: NET download
            pass
        elif re.compile('^ftp://').match(choosen_mirror): # FIXME: check that wget may handle FTP as HTTP
            file_uris = {'protocol': 'wget', 'files': files_list}
        elif re.compile('^nfs://').match(choosen_mirror): # TODO: NFS download
            pass
        elif re.compile('^ssh://').match(choosen_mirror): # TODO: SSH download
            pass
        elif re.compile('^rsync://').match(choosen_mirror): # TODO: RSYNC download
            pass
        else: # do nothing
            pass

    # from here, either file_uris is a dict with a bunch of uris, or it is void in which case we give up
    if not file_uris:
        if useFallback:
            logging.getLogger().warn("command_on_host #%s: can't get files URI from fallback mirror, skipping command" % (myCoH.id))
            updateHistory(myCoH.id, 'upload_failed', '0', '', 'Can\'t get files URI for package \'%s\' on fallback mirror %s' % (myC.package_id, fbmirror))
            # the getFilesURI call failed on the fallback. We have a serious
            # problem and we better decrement attempts
            if not myCoH.switchToUploadFailed(myC.getNextConnectionDelay(), True):
                runFailedPhase(myCoH.id)
        else:
            # Use the fallback mirror
            logging.getLogger().warn("command_on_host #%s: can't get files URI from mirror %s, trying with fallback mirror" % (myCoH.id, mirror))
            _cbRunPushPullPhaseTestFallbackMirror(None, mirror, fbmirror, client, myC, myCoH)
        return

    client['protocol'] = file_uris['protocol']
    files_list = file_uris['files']

    myCoH.setUploadInProgress()
    myCoH.setStateUploadInProgress()
    # upload starts here
    if SchedulerConfig().mode == 'sync':
        updateHistory(myCoH.id, 'upload_in_progress')
        mydeffered = callOnBestLauncher(
            myCoH.id,
            'sync_remote_pull',
            False,
            myCoH.id,
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePullResult, myCoH.id).\
            addErrback(parsePullError, myCoH.id)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            myCoH.id,
            'async_remote_pull',
            False,
            myCoH.id,
            client,
            files_list,
            SchedulerConfig().max_upload_time
        )
        mydeffered.\
            addCallback(parsePullOrder, myCoH.id).\
            addErrback(parsePullError, myCoH.id)
    else:
        return None
    return mydeffered

def runExecutionPhase(myCommandOnHostID):
    # Second step : execute file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: execution phase" % myCommandOnHostID)
    if myCoH == None:
        return None
    if myCoH.isExecutionRunning(): # execution still running, immediately returns
        logger.info("command_on_host #%s: still running" % myCommandOnHostID)
        return None
    if myCoH.isExecutionDone(): # execution has already been done, jump to next stage
        logger.info("command_on_host #%s: execution done" % myCommandOnHostID)
        return runDeletePhase(myCommandOnHostID)
    if myCoH.isExecutionIgnored(): # execution has already been ignored, jump to next stage
        logger.info("command_on_host #%s: execution ignored" % myCommandOnHostID)
        return runDeletePhase(myCommandOnHostID)
    if not myCoH.isExecutionImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to execute right now" % myCommandOnHostID)
        return None
    if not myC.hasSomethingToExecute(): # nothing to execute here, jump to next stage
        logger.info("command_on_host #%s: nothing to execute" % myCommandOnHostID)
        myCoH.setExecutionIgnored()
        myCoH.setStateScheduled()
        return runDeletePhase(myCommandOnHostID)

    if myC.hasToUseProxy():
        if not localProxyMayContinue(myCommandOnHostID):
            logger.info("command_on_host #%s: execution postponed, waiting for some clients" % myCommandOnHostID)
            myCoH.setStateScheduled()
            return None

    # if we are here, execution has either previously failed or never be done
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('execute'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseExecutionError, myCommandOnHostID)

    if myC.isQuickAction(): # should be a standard script
        myCoH.setExecutionInProgress()
        myCoH.setStateExecutionInProgress()
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'execution_in_progress')
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'sync_remote_quickaction',
                False,
                myCommandOnHostID,
                client,
                ' '.join([myC.start_file, myC.parameters]).strip(),
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseExecutionResult, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'async_remote_quickaction',
                False,
                myCommandOnHostID,
                client,
                ' '.join([myC.start_file, myC.parameters]).strip(),
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseExecutionOrder, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else:
        myCoH.setExecutionInProgress()
        myCoH.setStateExecutionInProgress()
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'execution_in_progress')
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'sync_remote_exec',
                False,
                myCommandOnHostID,
                client,
                ' '.join([myC.start_file, myC.parameters]).strip(),
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseExecutionResult, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'async_remote_exec',
                False,
                myCommandOnHostID,
                client,
                ' '.join([myC.start_file, myC.parameters]).strip(),
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseExecutionOrder, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        else:
            return None
        return mydeffered

def runDeletePhase(myCommandOnHostID):
    # Third step : delete file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: delete phase" % myCommandOnHostID)
    if myCoH == None:
        return None
    if myCoH.isDeleteRunning(): # delete still running, immediately returns
        logging.getLogger().info("command_on_host #%s: still deleting" % myCommandOnHostID)
        return None
    if myCoH.isDeleteDone(): # delete has already be done, jump to next stage
        logger.info("command_on_host #%s: delete done" % myCommandOnHostID)
        return runInventoryPhase(myCommandOnHostID)
    if myCoH.isDeleteIgnored(): # delete has already be ignored, jump to next stage
        logger.info("command_on_host #%s: delete ignored" % myCommandOnHostID)
        return runInventoryPhase(myCommandOnHostID)
    if not myCoH.isDeleteImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to delete right now" % myCommandOnHostID)
        return None
    if not myC.hasSomethingToDelete(): # nothing to delete here, jump to next stage
        logger.info("command_on_host #%s: nothing to delete" % myCommandOnHostID)
        myCoH.setDeleteIgnored()
        myCoH.setStateScheduled()
        return runInventoryPhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('delete'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseDeleteError, myCommandOnHostID)

    # if we are here, deletion has either previously failed or never be done
    if re.compile('^file://').match(myT.mirrors): # delete from remote push
        files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))

        myCoH.setDeleteInProgress()
        myCoH.setStateDeleteInProgress()
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'delete_in_progress')
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'sync_remote_delete',
                False,
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseDeleteResult, myCommandOnHostID).\
                addErrback(parseDeleteError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = callOnBestLauncher(
                myCommandOnHostID,
                'async_remote_delete',
                False,
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_command_time
            )
            mydeffered.\
                addCallback(parseDeleteOrder, myCommandOnHostID).\
                addErrback(parseDeleteError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else: # delete from remote pull
        mirrors = myT.mirrors.split('||')
        mirror = mirrors[0] # TODO: handle when several mirrors are available
        if re.compile('^http://').match(mirror) or re.compile('^https://').match(mirror): # HTTP download
            files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))

            myCoH.setDeleteInProgress()
            myCoH.setStateDeleteInProgress()
            if SchedulerConfig().mode == 'sync':
                updateHistory(myCommandOnHostID, 'delete_in_progress')
                mydeffered = callOnBestLauncher(
                    myCommandOnHostID,
                    'sync_remote_delete',
                    False,
                    myCommandOnHostID,
                    client,
                    files_list,
                    SchedulerConfig().max_command_time
                )
                mydeffered.\
                    addCallback(parseDeleteResult, myCommandOnHostID).\
                    addErrback(parseDeleteError, myCommandOnHostID)
            elif SchedulerConfig().mode == 'async':
                mydeffered = callOnBestLauncher(
                    myCommandOnHostID,
                    'async_remote_delete',
                    False,
                    myCommandOnHostID,
                    client,
                    files_list,
                    SchedulerConfig().max_command_time
                )
                mydeffered.\
                    addCallback(parseDeleteOrder, myCommandOnHostID).\
                    addErrback(parseDeleteError, myCommandOnHostID)
            else:
                return None
            return mydeffered
        elif re.compile('^smb://').match(mirror): # TODO: NET download
            pass
        elif re.compile('^ftp://').match(mirror): # TODO: FTP download
            pass
        elif re.compile('^nfs://').match(mirror): # TODO: NFS download
            pass
        elif re.compile('^ssh://').match(mirror): # TODO: SSH download
            pass
        elif re.compile('^rsync://').match(mirror): # TODO: RSYNC download
            pass
        else: # do nothing
            pass

    myCoH.setDeleteIgnored()
    myCoH.setStateScheduled()
    return runInventoryPhase(myCommandOnHostID)

def runInventoryPhase(myCommandOnHostID):
    # Run inventory if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: inventory phase" % myCommandOnHostID)
    if myCoH == None:
        return None

    if myCoH.isInventoryRunning(): # inventory still running, immediately returns
        logger.info("command_on_host #%s: still inventoriing" % myCoH.getId())
        return None
    if myCoH.isInventoryIgnored(): # inventory has already been ignored, jump to next stage
        logger.info("command_on_host #%s: inventory ignored" % myCoH.getId())
        return runRebootPhase(myCommandOnHostID)
    if myCoH.isInventoryDone(): # inventory has already already done, jump to next stage
        logger.info("command_on_host #%s: inventory done" % myCoH.getId())
        return runRebootPhase(myCommandOnHostID)
    if myC.isPartOfABundle() and not isLastToInventoryInBundle(myCommandOnHostID): # there is still a coh in the same bundle that has to launch inventory, jump to next stage
        logger.info("command_on_host #%s: another coh from the same bundle will launch the inventory" % myCommandOnHostID)
        myCoH.setInventoryIgnored()
        myCoH.setStateScheduled()
        return runRebootPhase(myCommandOnHostID)
    if not myCoH.isInventoryImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to inventory right now" % myCoH.getId())
        return None
    if not myC.hasToRunInventory(): # no inventory to perform, jump to next stage
        logger.info("command_on_host #%s: nothing to inventory" % myCoH.getId())
        myCoH.setInventoryIgnored()
        myCoH.setStateScheduled()
        return runRebootPhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('inventory'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseInventoryError, myCommandOnHostID)

    # if we are here, inventory has either previously failed or never be done
    myCoH.setInventoryInProgress()
    myCoH.setStateInventoryInProgress()
    if SchedulerConfig().mode == 'sync':
        updateHistory(myCommandOnHostID, 'inventory_in_progress')
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'sync_remote_inventory',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseInventoryResult, myCommandOnHostID).\
            addErrback(parseInventoryError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'async_remote_inventory',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseInventoryOrder, myCommandOnHostID).\
            addErrback(parseInventoryError, myCommandOnHostID)
    else:
        return None
    return mydeffered

def runRebootPhase(myCommandOnHostID):
    # Run reboot if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: reboot phase" % myCommandOnHostID)
    if myCoH == None:
        return None

    if myCoH.isRebootRunning(): # reboot still running, immediately returns
        logger.info("command_on_host #%s: still rebooting" % myCoH.getId())
        return None
    if myCoH.isRebootIgnored(): # reboot has already been ignored, jump to next stage
        logger.info("command_on_host #%s: reboot ignored" % myCoH.getId())
        return runHaltOnDone(myCommandOnHostID)
    if myCoH.isRebootDone(): # reboot has already been done, jump to next stage
        logger.info("command_on_host #%s: reboot done" % myCoH.getId())
        return runHaltOnDone(myCommandOnHostID)
    if not myCoH.isRebootImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: do not reboot right now" % myCoH.getId())
        return None
    if not myC.hasToReboot(): # no reboot to perform, jump to next stage
        logger.info("command_on_host #%s: do not reboot" % myCoH.getId())
        myCoH.setRebootIgnored()
        myCoH.setStateScheduled()
        return runHaltOnDone(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('reboot'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseRebootError, myCommandOnHostID)

    myCoH.setRebootInProgress()
    myCoH.setStateRebootInProgress()

    if SchedulerConfig().mode == 'sync':
        updateHistory(myCommandOnHostID, 'reboot_in_progress')
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'sync_remote_reboot',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseRebootResult, myCommandOnHostID).\
            addErrback(parseRebootError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'async_remote_reboot',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseRebootOrder, myCommandOnHostID).\
            addErrback(parseRebootError, myCommandOnHostID)
    else:
        return None
    return mydeffered

def runHaltOnDone(myCommandOnHostID): # supposed to be called at the very end of the process
    logger = logging.getLogger()
    logger.info("command_on_host #%s: halt-on-done phase" % myCommandOnHostID)
    return runHaltPhase(myCommandOnHostID, 'done')

def runHaltOnFailed(myCommandOnHostID): # supposed to be called when the command is trashed
    logger = logging.getLogger()
    logger.info("command_on_host #%s: halt-on-failed phase" % myCommandOnHostID)
    return runHaltPhase(myCommandOnHostID, 'failed')

def runHaltPhase(myCommandOnHostID, condition):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: halt phase" % myCommandOnHostID)
    if myCoH == None:
        return None
    if myCoH.isHaltRunning(): # halt still running, immediately returns
        logging.getLogger().info("command_on_host #%s: still halting" % myCommandOnHostID)
        return None
    if myCoH.isHaltIgnored(): # halt has already be ignored, jump to next stage
        logger.info("command_on_host #%s: halt ignored" % myCommandOnHostID)
        return runDonePhase(myCommandOnHostID)
    if myCoH.isHaltDone(): # halt has already be done, jump to next stage
        logger.info("command_on_host #%s: halt done" % myCommandOnHostID)
        return runDonePhase(myCommandOnHostID)
    if myC.isPartOfABundle() and not isLastToHaltInBundle(myCommandOnHostID): # there is still a coh in the same bundle that has to halt, jump to next stage
        logger.info("command_on_host #%s: another coh from the same bundle will do the halt" % myCommandOnHostID)
        myCoH.setHaltIgnored()
        return runDonePhase(myCommandOnHostID)
    if not myCoH.isHaltImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: do not halt right now" % myCoH.getId())
        return None
    if not myC.hasToHalt(): # do not run halt
        logger.info("command_on_host #%s: halt ignored" % myCommandOnHostID)
        myCoH.setHaltIgnored()
        myCoH.setStateScheduled()
        return runDonePhase(myCommandOnHostID)
    if condition == 'done' and not myC.hasToHaltIfDone(): # halt on done and we do not have to halt on done
        logger.info("command_on_host #%s: halt-on-done ignored" % myCommandOnHostID)
        myCoH.setHaltIgnored()
        myCoH.setStateScheduled()
        return runDonePhase(myCommandOnHostID)
    if condition == 'failed' and not myC.hasToHaltIfFailed(): # halt on failed and we do not have to halt on failure
        logger.info("command_on_host #%s: halt-on-failed ignored" % myCommandOnHostID)
        myCoH.setHaltIgnored()
        myCoH.setStateScheduled()
        return runDonePhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('halt'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseHaltError, myCommandOnHostID)

    myCoH.setHaltInProgress()
    myCoH.setStateHaltInProgress()

    if SchedulerConfig().mode == 'sync':
        updateHistory(myCommandOnHostID, 'halt_in_progress')
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'sync_remote_halt',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseHaltResult, myCommandOnHostID).\
            addErrback(parseHaltError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            myCommandOnHostID,
            'async_remote_halt',
            False,
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseHaltOrder, myCommandOnHostID).\
            addErrback(parseHaltError, myCommandOnHostID)
    else:
        return None
    return mydeffered

def parseWOLResult((exitcode, stdout, stderr), myCommandOnHostID):
    def setstate(myCommandOnHostID, stdout, stderr):
        (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
        logging.getLogger().info("command_on_host #%s: WOL done and done waiting" % (myCommandOnHostID))
        if myCoH == None:
            return None
        updateHistory(myCommandOnHostID, 'wol_done', 0, stdout, stderr)
        if myCoH.switchToWOLDone():
            return runUploadPhase(myCommandOnHostID)
        else:
            return None

    logging.getLogger().info("command_on_host #%s: WOL done, now waiting %s seconds for the computer to wake up" % (myCommandOnHostID,SchedulerConfig().max_wol_time))
    twisted.internet.reactor.callLater(SchedulerConfig().max_wol_time, setstate, myCommandOnHostID, stdout, stderr)
    return None

def parsePushResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: push done (exitcode == 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
        if myCoH.switchToUploadDone():
            return runExecutionPhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: push failed (exitcode != 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
        if myCoH.switchToUploadFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parsePullResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None

    proxy_coh_id = myCoH.getUsedProxy()
    if proxy_coh_id:
        (myProxyCoH, myProxyC, myProxyT) = gatherCoHStuff(proxy_coh_id)
        proxy_uuid = myProxyT.getUUID()
        # see if we can unload a proxy
        # no ret val
        LocalProxiesUsageTracking().untake(proxy_uuid, myC.getId())
        logging.getLogger().debug("scheduler %s: coh #%s used coh #%s as local proxy, releasing one slot (%d left)" % (SchedulerConfig().name, myCommandOnHostID, proxy_coh_id, LocalProxiesUsageTracking().how_much_left_for(proxy_uuid, myC.getId())))

    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: pull done (exitcode == 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
        if myCoH.switchToUploadDone():
            return runExecutionPhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: pull failed (exitcode != 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
        if myCoH.switchToUploadFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parseExecutionResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: execution done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'execution_done', exitcode, stdout, stderr)
        if myCoH.switchToExecutionDone():
            return runDeletePhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: execution failed (exitcode != 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'execution_failed', exitcode, stdout, stderr)
        if myCoH.switchToExecutionFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parseDeleteResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: delete done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'delete_done', exitcode, stdout, stderr)
        if myCoH.switchToDeleteDone():
            return runInventoryPhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: delete failed (exitcode != 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'delete_failed', exitcode, stdout, stderr)
        if myCoH.switchToDeleteFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parseInventoryResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: inventory done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'inventory_done', exitcode, stdout, stderr)
        if myCoH.switchToInventoryDone():
            return runRebootPhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: inventory failed (exitcode != 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'inventory_failed', exitcode, stdout, stderr)
        if myCoH.switchToInventoryFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parseRebootResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    logger = logging.getLogger()
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: reboot done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'reboot_done', exitcode, stdout, stderr)
        if myCoH.switchToRebootDone():
            return runHaltOnDone(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: reboot failed (exitcode != 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'reboot_failed', exitcode, stdout, stderr)
        if myCoH.switchToRebootFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parseHaltResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    logger = logging.getLogger()
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: halt done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'halt_done', exitcode, stdout, stderr)
        if myCoH.switchToHaltDone():
            return runDonePhase(myCommandOnHostID)
        else:
            return None
    else: # failure: immediately give up
        logging.getLogger().info("command_on_host #%s: halt failed (exitcode != 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'halt_failed', exitcode, stdout, stderr)
        if myCoH.switchToHaltFailed(myC.getNextConnectionDelay()):
            return None
        else:
            return runFailedPhase(myCommandOnHostID)

def parsePushOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'upload_in_progress')
        logging.getLogger().info("command_on_host #%s: push order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setUploadToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: push order not taken in account" % myCommandOnHostID)
        return None

def parsePullOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'upload_in_progress')
        logging.getLogger().info("command_on_host #%s: pull order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setUploadToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: pull order not taken in account" % myCommandOnHostID)
        return None

def parseExecutionOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'execution_in_progress')
        logging.getLogger().info("command_on_host #%s: execution order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setExecutionToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: execution order not taken in account" % myCommandOnHostID)
        return None

def parseDeleteOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'delete_in_progress')
        logging.getLogger().info("command_on_host #%s: delete order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setDeleteToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: delete order not taken in account" % myCommandOnHostID)
        return None

def parseInventoryOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'inventory_in_progress')
        logging.getLogger().info("command_on_host #%s: inventory order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setInventoryToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: inventory order not taken in account" % myCommandOnHostID)
        return None

def parseRebootOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'reboot_in_progress')
        logging.getLogger().info("command_on_host #%s: reboot order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setRebootToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: reboot order not taken in account" % myCommandOnHostID)
        return None

def parseHaltOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if myCoH == None:
        return None
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'halt_in_progress')
        logging.getLogger().info("command_on_host #%s: halt order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setHaltToDo()
        myCoH.setStateScheduled()
        logging.getLogger().warn("command_on_host #%s: halt order not taken in account" % myCommandOnHostID)
        return None

def parseWOLError(reason, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: WOL failed" % myCommandOnHostID)
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'wol_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToWOLFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    return None

def parsePushError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: push failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    return None

def parsePullError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: pull failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None

    proxy_coh_id = myCoH.getUsedProxy()
    if proxy_coh_id:
        (myProxyCoH, myProxyC, myProxyT) = gatherCoHStuff(proxy_coh_id)
        proxy_uuid = myProxyT.getUUID()
        # see if we can unload a proxy
        # no ret val
        LocalProxiesUsageTracking().untake(proxy_uuid, myC.getId())
        logging.getLogger().debug("scheduler %s: coh #%s used coh #%s as local proxy, releasing one slot (%d left)" % (SchedulerConfig().name, myCommandOnHostID, proxy_coh_id, LocalProxiesUsageTracking().how_much_left_for(proxy_uuid, myC.getId())))

    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    return None

def parseExecutionError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: execution failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'execution_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToExecutionFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    # FIXME: should return a failure (but which one ?)
    return None

def parseDeleteError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: delete failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'delete_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToDeleteFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    # FIXME: should return a failure (but which one ?)
    return None

def parseInventoryError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.warn("command_on_host #%s: inventory failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'inventory_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToInventoryFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    # FIXME: should return a failure (but which one ?)
    return None

def parseRebootError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.warn("command_on_host #%s: reboot failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'reboot_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToRebootFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    # FIXME: should return a failure (but which one ?)
    return None

def parseHaltError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.warn("command_on_host #%s: halt failed, unattented reason: %s" % (myCommandOnHostID, reason))
    if myCoH == None:
        return None
    updateHistory(myCommandOnHostID, 'halt_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToHaltFailed(myC.getNextConnectionDelay(), False) # do not decrement tries as the error has most likeley be produced by an internal condition
    # FIXME: should return a failure (but which one ?)
    return None

def runDonePhase(myCommandOnHostID):
    # Last step : end file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: end (done) phase" % myCommandOnHostID)
    if myCoH == None:
        return None
    myCoH.setStateDone()
    return None

def runFailedPhase(myCommandOnHostID):
    # Last step : end file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: end (failed) phase" % myCommandOnHostID)
    if myCoH == None:
        return None
    myCoH.setStateFailed()
    return None

def updateHistory(id, state, error_code=0, stdout='', stderr=''):
    encoding = SchedulerConfig().dbencoding
    history = CommandsHistory()
    history.fk_commands_on_host = id
    history.date = time.time()
    history.error_code = error_code
    history.stdout = stdout.encode(encoding, 'replace')
    history.stderr = stderr.encode(encoding, 'replace')
    history.state = state
    history.flush()

def chooseClientIP(myT):
    return pulse2.scheduler.network.chooseClientIP({
        'uuid': myT.getUUID(),
        'fqdn': myT.getFQDN(),
        'shortname': myT.getShortName(),
        'ips': myT.getIps(),
        'macs': myT.getMacs()
    })

def getClientGroup(myT):
    return MGAssignAlgoManager().getMachineGroup(myT)

def getMaxNumberOfGroups():
    return MGAssignAlgoManager().getMaxNumberOfGroups()

def getClientCheck(myT):
    return getCheck(SchedulerConfig().client_check, {
        'uuid': myT.getUUID(),
        'shortname': myT.getShortName(),
        'ips': myT.getIps(),
        'macs': myT.getMacs()
    });

def getServerCheck(myT):
    return getCheck(SchedulerConfig().server_check, {
        'uuid': myT.getUUID(),
        'shortname': myT.getShortName(),
        'ips': myT.getIps(),
        'macs': myT.getMacs()
    });
