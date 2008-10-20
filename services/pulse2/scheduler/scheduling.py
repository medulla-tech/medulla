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
import sqlalchemy
import time
import re
import os
import random
import datetime

# Twisted modules
import twisted.internet

# MMC plugins
from mmc.plugins.msc.database import MscDatabase
import mmc.plugins.msc.mirror_api

# ORM mappings
from mmc.plugins.msc.orm.commands import Commands
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost
from mmc.plugins.msc.orm.commands_history import CommandsHistory
from mmc.plugins.msc.orm.target import Target

# our modules
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.launchers_driving import callOnBestLauncher, callOnLauncher, getLaunchersBalance
import pulse2.scheduler.network
from pulse2.scheduler.assign_algo import MGAssignAlgoManager
from pulse2.scheduler.checks import getCheck, getAnnounceCheck

def gatherStuff():
    """ handy function to gather widely used objects """
    session = sqlalchemy.create_session()
    database = MscDatabase()
    logger = logging.getLogger()
    return (session, database, logger)

def gatherCoHStuff(idCommandOnHost):
    """ same as gatherStuff(), this time for a particular CommandOnHost """
    session = sqlalchemy.create_session()
    database = MscDatabase()
    myCommandOnHost = session.query(CommandsOnHost).get(idCommandOnHost)
    myCommand = session.query(Commands).get(myCommandOnHost.getIdCommand())
    myTarget = session.query(Target).get(myCommandOnHost.getIdTarget())
    session.close()
    return (myCommandOnHost, myCommand, myTarget)

def getDependancies(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)

    session = sqlalchemy.create_session()
    database = MscDatabase()

    # look for CoH from same bundle
    # look for CoH from lower order
    # look for unfinished CoH
    # look for CoH on same host
    coh_dependencies = []
    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.bundle_id == myC.bundle_id).\
        filter(database.commands.c.order_in_bundle < myC.order_in_bundle).\
        filter(database.commands_on_host.c.current_state !=  'done').\
        filter(database.target.c.target_uuid ==  myT.target_uuid).\
        all():
        coh_dependencies.append(q.id)
    session.close()
    return coh_dependencies

def localProxyUploadStatus(myCommandOnHostID):
    """ attempt to analyse coh in the same command in order to now how we may advance.
    possible return values:
        - 'waiting': my time is not yet come
        - 'server': I'm an active proxy server
        - 'dead': I'm a client and all proxies seems dead
        - an int: I'm a client and the returned value is the CoH I will use
    """
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)

    # as for now, if we previously found a proxy, use it
    if myCoH.getUsedProxy() != None:
        logging.getLogger().debug("scheduler %s: keeping coh #%s as local proxy for #%s" % (SchedulerConfig().name, myCoH.getUsedProxy(), myCommandOnHostID))
        return 'keeping'

    session = sqlalchemy.create_session()
    database = MscDatabase()

    smallest_done_upload_order_in_proxy = None
    best_ready_proxy_server_coh = None
    potential_proxy_server_coh = None

    # iterate over CoH which
    # are linked to the same command
    # are not our CoH
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

    if myCoH.getOrderInProxy() == None:                                 # I'm a client: I MUST use a proxy server
        if best_ready_proxy_server_coh != None:                         # a proxy seems ready => PROXY CLIENT MODE
            logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID))
            return best_ready_proxy_server_coh
        elif potential_proxy_server_coh != None:                        # but one may become ready => WAITING
            logging.getLogger().debug("scheduler %s: coh #%s still waiting for a local proxy to use" % (SchedulerConfig().name, myCommandOnHostID))
            return 'waiting'
        else:                                                           # and all seems dead => ERROR
            logging.getLogger().debug("scheduler %s: coh #%s won't likely be able to use a local proxy" % (SchedulerConfig().name, myCommandOnHostID))
            return 'dead'
    else:                                                               # I'm a server: I MAY use a proxy
        if best_ready_proxy_server_coh != None:                         # a proxy seems ready => PROXY CLIENT MODE
            logging.getLogger().debug("scheduler %s: found coh #%s as local proxy for #%s" % (SchedulerConfig().name, best_ready_proxy_server_coh, myCommandOnHostID))
            return best_ready_proxy_server_coh
        elif potential_proxy_server_coh:                                # but one better candidate may become ready => WAITING
            logging.getLogger().debug("scheduler %s: coh #%s still waiting to know if is is local proxy client or server" % (SchedulerConfig().name, myCommandOnHostID))
            return 'waiting'
        else:                                                           # and others better candidates seems dead => PROXY SERVER MODE
            logging.getLogger().debug("scheduler %s: coh #%s become local proxy server" % (SchedulerConfig().name, myCommandOnHostID))
            return 'server'

def localProxyMayCleanup(myCommandOnHostID):
    """ attempt to analyse coh in the same command in order to now how we may advance.
    """
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)

    session = sqlalchemy.create_session()
    database = MscDatabase()

    # iterate over CoH which
    # are linked to the same command
    # are not our CoH
    # are our client
    # have finished their upload or totally failed
    res = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).join(database.target)).\
        filter(database.commands.c.id == myC.id).\
        filter(database.commands_on_host.c.id != myCoH.id).\
        filter(database.commands_on_host.c.uploaded != 'DONE').\
        filter(database.commands_on_host.c.current_state != 'failed').\
        filter(database.commands_on_host.c.fk_use_as_proxy == myCoH.id).\
        all()
    session.close()
    return len(res) == 0

def startAllCommands(scheduler_name, commandIDs = []):
    session = sqlalchemy.create_session()
    database = MscDatabase()
    logger = logging.getLogger()
    if commandIDs:
        logger.debug("MSC_Scheduler->startAllCommands() for commands %s..." % commandIDs)
    else:
        logger.debug("MSC_Scheduler->startAllCommands()...")
    # gather candidates:
    # ignore completed tasks
    # ignore paused tasks
    # ignore stopped tasks
    # ignore tasks already in progress
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
        filter(database.commands_on_host.c.current_state != 'pause').\
        filter(database.commands_on_host.c.current_state != 'stop').\
        filter(database.commands_on_host.c.current_state != 'failed').\
        filter(database.commands_on_host.c.current_state != 'upload_in_progress').\
        filter(database.commands_on_host.c.current_state != 'execution_in_progress').\
        filter(database.commands_on_host.c.current_state != 'delete_in_progress').\
        filter(database.commands_on_host.c.current_state != 'inventory_in_progress').\
        filter(database.commands_on_host.c.current_state != 'upload_failed').\
        filter(database.commands_on_host.c.current_state != 'execution_failed').\
        filter(database.commands_on_host.c.current_state != 'delete_failed').\
        filter(database.commands_on_host.c.current_state != 'inventory_failed').\
        filter(database.commands_on_host.c.next_launch_date <= now).\
        filter(sqlalchemy.or_(
            database.commands.c.start_date == soon,
            database.commands.c.start_date <= now)
        ).\
        filter(database.commands.c.start_date != later).\
        filter(sqlalchemy.or_(
            database.commands.c.end_date == soon,
            database.commands.c.end_date == later,
            database.commands.c.end_date >= now)
        ).\
        filter(sqlalchemy.or_(
            database.commands_on_host.c.scheduler == '',
            database.commands_on_host.c.scheduler == scheduler_name,
            database.commands_on_host.c.scheduler == None)
        )
    if commandIDs:
        commands_query = commands_query.filter(database.commands.c.id.in_(*commandIDs))
    commands_to_perform = []
    for q in commands_query.all():
        commands_to_perform.append(q.id)
    session.close()

    return sortCommands(commands_to_perform)

def sortCommands(commands_to_perform):
    """
    Process CommandsOnHost objects list and fires needed deferred objects to
    perform the commands on background.
    """

    def _cb(result, tocome_distribution):

        ids_list = [] # will contain the IDs from commands to run
        # list is pre-filled in case of something goes wrong below
        for ids in tocome_distribution.values():
            ids_list += ids

        if len(ids_list) == 0:
            logging.getLogger().info("Scheduler: 0 task to start")
            return 0

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
            # IT MAY PREVENT SCHEDULER TO RUN AT FULL CAPACITY IF A GROUP ALMOST EMPTY
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

        deffereds = [] # will hold all deferred
        for id in ids_list:
            deffered = runCommand(id)
            if deffered:
                deffereds.append(deffered)
        logging.getLogger().info("Scheduler: %d tasks to start" % len(deffereds))
        return len(deffereds)


    # build array of commands to perform
    tocome_distribution = dict()
    for command_id in commands_to_perform:
        (myCoH, myC, myT) = gatherCoHStuff(command_id)
        command_group = getClientGroup(myT)
        if not command_group in tocome_distribution:
            tocome_distribution[command_group] = [command_id]
        else:
            tocome_distribution[command_group].append(command_id)

    # build array of commands being processed by available launchers
    getLaunchersBalance().\
        addCallback(_cb, tocome_distribution)

def stopElapsedCommands(scheduler_name):
    # we return a list of deferred
    deffereds = [] # will hold all deferred
    session = sqlalchemy.create_session()
    database = MscDatabase()
    logger = logging.getLogger()
    logger.debug("MSC_Scheduler->stopElapsedCommands()...")
    # gather candidates:
    # retain tasks already in progress
    # take tasks with end_date in the future, but not null
    for q in session.query(CommandsOnHost).\
        select_from(database.commands_on_host).\
        filter(sqlalchemy.or_(
            database.commands_on_host.c.current_state == 'upload_in_progress',
            database.commands_on_host.c.current_state == 'execution_in_progress',
            database.commands_on_host.c.current_state == 'delete_in_progress',
            database.commands_on_host.c.current_state == 'inventory_in_progress',
        )).filter(sqlalchemy.or_(
            database.commands_on_host.c.scheduler == '',
            database.commands_on_host.c.scheduler == scheduler_name,
            database.commands_on_host.c.scheduler == None)
        ).all():
        # enter the maze: tag command as to-be-stopped if relevant

        deffered = None
        (myCoH, myC, myT) = gatherCoHStuff(q.id)
        if not myC.inDeploymentInterval(): # stops command not in interval
            deffered = stopCommand(q.id)# stops command no valid anymore
        elif myC.end_date.__str__() != '0000-00-00 00:00:00' and myC.end_date.__str__()  <= time.strftime("%Y-%m-%d %H:%M:%S"):
            deffered = stopCommand(q.id)

        if deffered:
            deffereds.append(deffered)
    session.close()
    logging.getLogger().info("Scheduler: %d tasks to stop" % len(deffereds))
    return deffereds

def stopCommandsOnHosts(ids):
    for launcher in SchedulerConfig().launchers_uri.values():
        callOnLauncher(launcher, 'term_processes', ids)

def stopCommand(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("going to terminate command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
    logger.debug("command_on_host state is %s" % myCoH.toH())
    logger.debug("command state is %s" % myC.toH())
    for launcher in SchedulerConfig().launchers_uri.values():
        callOnLauncher(launcher, 'term_process', myCommandOnHostID)
    return True

def startCommand(myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
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
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()

    # FIXME: those tests are performed way too late !

    if not myC.inDeploymentInterval():
        return

    if not myC.isPartOfABundle(): # command is independant, we may advance
        logger.debug("command_on_host #%s: not part of a bundle" % myCoH.getId())
    else: # command is part of a bundle, let's check the bundle state
        logger.debug("command_on_host #%s: part of bundle %s, order %s " % (myCoH.getId(), myC.getBundleId(), myC.getOrderInBundle()))
        deps =  getDependancies(myCommandOnHostID)
        if len(deps) != 0:
            logger.debug("command_on_host #%s: depends on %s " % (myCoH.getId(), deps))
            return True # give up, some deps has to be done
        else:
            logger.debug("command_on_host #%s: do not depends on something" % (myCoH.getId()))

    myCoH.setStartDate()
    logger = logging.getLogger()
    logger.info("going to do command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
    logger.debug("command_on_host state is %s" % myCoH.toH())
    logger.debug("command state is %s" % myC.toH())
    return runWOLPhase(myCommandOnHostID)

def runWOLPhase(myCommandOnHostID):
    """
        Attempt do see if a wake-on-lan should be done
    """

    # check for WOL condition in order to give up if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    if not myC.hasToWOL():              # do not perform WOL
        logger.info("command_on_host #%s: WOL ignored" % myCommandOnHostID)
        return runUploadPhase(myCommandOnHostID)
    if myCoH.isWOLRunning():            # WOL in progress
        if myCoH.getLastWOLAttempt() != None: # WOL *really* progress, hem
            if (datetime.datetime.now()-myCoH.getLastWOLAttempt()).seconds < SchedulerConfig().max_wol_time:
                # we should wait a little more
                return None
            else:
                # we already pass the delay, let's continue
                logging.getLogger().warn("command_on_host #%s: WOL should have been set as done !" % (myCommandOnHostID))
                myCoH.setScheduled()
                return runUploadPhase(myCommandOnHostID)
        else: # WOL marked as "in progress", but no time given ?!
            # return None to avoid some possible race conditions
            return None

        logger.info("command_on_host #%s: WOL still running" % myCommandOnHostID)
        return None
    if not myCoH.isWOLImminent():       # nothing to do right now, give out
        logger.info("command_on_host #%s: not the right time to WOL" % myCoH.getId())
        return None

    logger.info("command_on_host #%s: WOL phase" % myCommandOnHostID)

    myCoH.setLastWOLAttempt()
    updateHistory(myCommandOnHostID, 'wol_in_progress')
    myCoH.setCommandStatut('wol_in_progress')

    # perform call
    mydeffered = callOnBestLauncher('wol', myT.target_macaddr.split('||'), myT.target_bcast.split('||'))

    mydeffered.\
        addCallback(parseWOLResult, myCommandOnHostID).\
        addErrback(parseWOLError, myCommandOnHostID)
    return mydeffered

def runUploadPhase(myCommandOnHostID):
    """
        Handle first Phase: upload time
    """
    # First step : copy files
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: copy phase" % myCommandOnHostID)

    # check for upload condition in order to give up if needed
    if myCoH.isUploadRunning(): # upload still running, immediately returns
        logger.info("command_on_host #%s: still running" % myCoH.getId())
        return None
    if myCoH.isUploadIgnored(): # upload has already been ignored, jump to next stage
        logger.info("command_on_host #%s: upload ignored" % myCoH.getId())
        return runExecutionPhase(myCommandOnHostID)
    if myCoH.isUploadDone(): # upload has already already done, jump to next stage
        logger.info("command_on_host #%s: upload done" % myCoH.getId())
        return runExecutionPhase(myCommandOnHostID)
    if not myCoH.isUploadImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to upload right now" % myCoH.getId())
        return None
    if not myC.hasSomethingToUpload(): # nothing to upload here, jump to next stage
        logger.info("command_on_host #%s: nothing to upload" % myCoH.getId())
        myCoH.setUploadIgnored()
        return runExecutionPhase(myCommandOnHostID)

    # check if we may reach client
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('transfert'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parsePushError, myCommandOnHostID)

    # fullfil used proxy (if we can)
    if myC.hasToUseProxy():
        proxystatus = localProxyUploadStatus(myCommandOnHostID)
        if proxystatus == 'waiting':
            logger.info("command_on_host #%s: waiting for a local proxy" % myCoH.getId())
            return None
        elif proxystatus == 'dead':
            logger.warn("command_on_host #%s: waiting for a local proxy which will never be ready !" % myCoH.getId())
            return None
        elif proxystatus == 'server':
            logger.info("command_on_host #%s: becoming local proxy server" % myCoH.getId())
            myCoH.setUsedProxy(myCommandOnHostID) # special case: this way we now we were server
        elif proxystatus == 'keeping':
            logger.info("command_on_host #%s: keeping previously acquiered local proxy settings" % myCoH.getId())
        else:
            logger.info("command_on_host #%s: becoming local proxy client" % myCoH.getId())
            myCoH.setUsedProxy(proxystatus)

    # if we are here, upload has either previously failed or never be done
    # do copy here
    # first attempt to guess is mirror is local (push) or remove (pull) or through a proxy
    if myCoH.isProxyClient():
        client['protocol'] = 'rsyncproxy'
        # get informations about our proxy
        (proxyCoH, proxyC, proxyT) = gatherCoHStuff(myCoH.getUsedProxy())
        proxy = { 'host': chooseClientIP(proxyT), 'uuid': proxyT.getUUID(), 'maxbw': proxyC.maxbw, 'client_check': getClientCheck(proxyT), 'server_check': getServerCheck(proxyT), 'action': getAnnounceCheck('transfert'), 'group': getClientGroup(proxyT)}
        if not proxy['host']: # We couldn't get an IP address for the target host
            return twisted.internet.defer.fail(Exception("Can't get proxy IP address")).addErrback(parsePushError, myCommandOnHostID)
        # and fill struct
        # only proxy['host'] used until now
        client['proxy'] = {
            'command_id': myCoH.getUsedProxy(),
            'host': proxy['host'],
            'uuid': proxy['uuid']
        }

        files_list = []
        for file in myC.files.split("\n"):
            fname = file.split('##')[1]
            if re.compile('^/').search(fname):
                fname = re.compile('^/[^/]*/(.*)$').search(fname).group(1) # drop first path component
            files_list.append(fname)

        myCoH.setUploadInProgress()
        myCoH.setCommandStatut('upload_in_progress')
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'upload_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_pull',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePushResult, myCommandOnHostID).\
                addErrback(parsePushError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
            mydeffered = callOnBestLauncher(
                'async_remote_pull',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePushOrder, myCommandOnHostID).\
                addErrback(parsePushError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    # local mirror starts by "file://"
    elif re.compile('^file://').match(myT.mirrors): # prepare a remote_push
        client['protocol'] = 'rsyncssh'
        files_list = []
        for file in myC.files.split("\n"):
            fname = file.split('##')[1]
            if re.compile('^/').search(fname):
                fname = re.compile('^/(.*)$').search(fname).group(1)
            files_list.append(os.path.join(re.compile('^file://(.*)$').search(myT.mirrors).group(1), fname))

        myCoH.setUploadInProgress()
        myCoH.setCommandStatut('upload_in_progress')
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'upload_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_push',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePushResult, myCommandOnHostID).\
                addErrback(parsePushError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
            mydeffered = callOnBestLauncher(
                'async_remote_push',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePushOrder, myCommandOnHostID).\
                addErrback(parsePushError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else: # remote push/pull

        # mirror is formated like this:
        # https://localhost:9990/mirror1||https://localhost:9990/mirror1
        try:
            mirrors = myT.mirrors.split('||')
        except:
            logger.warn("command_on_host #%s: target.mirror do not seems to be as expected, got '%', skipping command" % (myCommandOnHostID, myT.mirrors))
            return None

        # Check mirrors
        if len(mirrors) != 2:
            logger.warn("command_on_host #%s: we need two mirrors ! '%'" % (myCommandOnHostID, myT.mirrors))
            return None
        mirror = mirrors[0]
        fbmirror = mirrors[1]
        choosen_mirror = None

        # Test package availability on the two mirrors, primary and fallback
        available = mmc.plugins.msc.mirror_api.Mirror(mirror).isAvailable(myC.package_id)
        if available:
            logger.debug("command_on_host #%s: Package '%s' is available on %s" % (myCommandOnHostID, myC.package_id, mirror))
            choosen_mirror = mirror
        else:
            if fbmirror != mirror:
                available = mmc.plugins.msc.mirror_api.Mirror(fbmirror).isAvailable(myC.package_id)
                if available:
                    logger.debug("command_on_host #%s: Package '%s' is available on %s" % (myCommandOnHostID, myC.package_id, fbmirror))
                    choosen_mirror = fbmirror
        if not choosen_mirror:
            logger.warn("command_on_host #%s: Package '%s' is not available on mirrors %s and %s" % (myCommandOnHostID, myC.package_id, mirror, fbmirror))
            return None
        logger.debug("command_on_host #%s: mirror '%s' has been choosen" % (myCommandOnHostID, choosen_mirror))

        mirror_api = mmc.plugins.msc.mirror_api.Mirror(choosen_mirror)
        files_list = map(lambda x: mirror_api.getFileURI(x.split('##')[0]), myC.files.split("\n"))

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
            logger.warn("command_on_host #%s: can't get files URI from mirror, skipping command" % (myCommandOnHostID))
            return None

        client['protocol'] = file_uris['protocol']
        files_list = file_uris['files']

        myCoH.setUploadInProgress()
        myCoH.setCommandStatut('upload_in_progress')
        # upload starts here
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'upload_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_pull',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePullResult, myCommandOnHostID).\
                addErrback(parsePullError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = callOnBestLauncher(
                'async_remote_pull',
                myCommandOnHostID,
                client,
                files_list,
                SchedulerConfig().max_upload_time
            )
            mydeffered.\
                addCallback(parsePullOrder, myCommandOnHostID).\
                addErrback(parsePullError, myCommandOnHostID)
        else:
            return None
        return mydeffered

def runExecutionPhase(myCommandOnHostID):
    # Second step : execute file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: execution phase" % myCommandOnHostID)
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
        return runDeletePhase(myCommandOnHostID)

    # if we are here, execution has either previously failed or never be done
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('execute'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseExecutionError, myCommandOnHostID)

    if myC.isQuickAction(): # should be a standard script
        myCoH.setExecutionInProgress()
        myCoH.setCommandStatut('execution_in_progress')
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'execution_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_quickaction',
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
                'async_remote_quickaction',
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
        myCoH.setCommandStatut('execution_in_progress')
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'execution_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_exec',
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
                'async_remote_exec',
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
        return runInventoryPhase(myCommandOnHostID)
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('delete'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseDeleteError, myCommandOnHostID)

    if myC.hasToUseProxy():
        if not localProxyMayCleanup(myCommandOnHostID):
            logger.info("command_on_host #%s: cleanup postponed, waiting for some clients" % myCommandOnHostID)
            return None

    # if we are here, deletion has either previously failed or never be done
    if re.compile('^file://').match(myT.mirrors): # delete from remote push
        files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))

        myCoH.setDeleteInProgress()
        myCoH.setCommandStatut('delete_in_progress')
        if SchedulerConfig().mode == 'sync':
            updateHistory(myCommandOnHostID, 'delete_in_progress')
            mydeffered = callOnBestLauncher(
                'sync_remote_delete',
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
                'async_remote_delete',
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
            myCoH.setCommandStatut('delete_in_progress')
            if SchedulerConfig().mode == 'sync':
                updateHistory(myCommandOnHostID, 'delete_in_progress')
                mydeffered = callOnBestLauncher(
                    'sync_remote_delete',
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
                    'async_remote_delete',
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
    return runInventoryPhase(myCommandOnHostID)

def runInventoryPhase(myCommandOnHostID):
    # Run inventory if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: inventory phase" % myCommandOnHostID)
    if not myC.hasToRunInventory(): # do not run inventory
        logger.info("command_on_host #%s: inventory ignored" % myCommandOnHostID)
        return runRebootPhase(myCommandOnHostID)
    if myCoH.isInventoryRunning(): # inventory still running, immediately returns
        logger.info("command_on_host #%s: still inventoring" % myCommandOnHostID)
        return None
    if myCoH.isInventoryDone(): # inventory has already be done, jump to next stage
        logger.info("command_on_host #%s: inventory done" % myCommandOnHostID)
        return runRebootPhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('inventory'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseInventoryError, myCommandOnHostID)

    # if we are here, inventory has either previously failed or never be done
    myCoH.setInventoryInProgress()
    if SchedulerConfig().mode == 'sync':
        updateHistory(myCommandOnHostID, 'inventory_in_progress')
        mydeffered = callOnBestLauncher(
            'sync_remote_inventory',
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseInventoryResult, myCommandOnHostID).\
            addErrback(parseInventoryError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            'async_remote_inventory',
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
    if not myC.hasToReboot(): # do not run reboot
        logger.info("command_on_host #%s: reboot ignored" % myCommandOnHostID)
        return runEndPhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('inventory'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseInventoryError, myCommandOnHostID)

    if SchedulerConfig().mode == 'sync':
        updateHistory(myCommandOnHostID, 'reboot_in_progress')
        mydeffered = callOnBestLauncher(
            'sync_remote_reboot',
            myCommandOnHostID,
            client,
            SchedulerConfig().max_command_time
        )
        mydeffered.\
            addCallback(parseRebootResult, myCommandOnHostID).\
            addErrback(parseRebootError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = callOnBestLauncher(
            'async_remote_reboot',
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

def runEndPhase(myCommandOnHostID):
    # Last step : end file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: end phase" % myCommandOnHostID)
    myCoH.setDone()
    return None

def parseWOLResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    def setstate(myCommandOnHostID, stdout, stderr):
        logging.getLogger().info("command_on_host #%s: WOL done and done waiting" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'wol_done', 0, stdout, stderr)
        myCoH.setScheduled() # as WOL is not mandatory, set to "scheduled" for the upload to be performed
        runUploadPhase(myCommandOnHostID)

    logging.getLogger().info("command_on_host #%s: WOL done, now waiting %s seconds for the computer to wake up" % (myCommandOnHostID,SchedulerConfig().max_wol_time))
    twisted.internet.reactor.callLater(SchedulerConfig().max_wol_time, setstate, myCommandOnHostID, stdout, stderr)

    return None

def parsePushResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: push done (exitcode == 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
        if myCoH.switchToUploadDone():
            return runExecutionPhase(myCommandOnHostID)
        else:
            return None
    # failure: immediately give up
    logging.getLogger().info("command_on_host #%s: push failed (exitcode != 0)" % myCommandOnHostID)
    updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parsePullResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: pull done (exitcode == 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
        if myCoH.switchToUploadDone():
            return runExecutionPhase(myCommandOnHostID)
        else:
            return None
    # failure: immediately give up
    logging.getLogger().info("command_on_host #%s: pull failed (exitcode != 0)" % myCommandOnHostID)
    updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parseExecutionResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: execution done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'execution_done', exitcode, stdout, stderr)
        if myCoH.switchToExecutionDone():
            return runDeletePhase(myCommandOnHostID)
        else:
            return None
    # failure: immediately give up
    logging.getLogger().info("command_on_host #%s: execution failed (exitcode != 0)" % (myCommandOnHostID))
    updateHistory(myCommandOnHostID, 'execution_failed', exitcode, stdout, stderr)
    myCoH.switchToExecutionFailed(myC.getNextConnectionDelay())
    return None

def parseDeleteResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: delete done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'delete_done', exitcode, stdout, stderr)
        if myCoH.switchToDeleteDone():
            return runInventoryPhase(myCommandOnHostID)
        else:
            return None
    # failure: immediately give up
    logging.getLogger().info("command_on_host #%s: delete failed (exitcode != 0)" % (myCommandOnHostID))
    updateHistory(myCommandOnHostID, 'delete_failed', exitcode, stdout, stderr)
    myCoH.switchToDeleteFailed(myC.getNextConnectionDelay())
    return None

def parseInventoryResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: inventory done (exitcode == 0)" % (myCommandOnHostID))
        myCoH.setInventoryDone()
        updateHistory(myCommandOnHostID, 'inventory_done', exitcode, stdout, stderr)
        return runRebootPhase(myCommandOnHostID)
    # failure: immediately give up (FIXME: should not care of this failure)
    logging.getLogger().info("command_on_host #%s: inventory failed (exitcode != 0)" % (myCommandOnHostID))
    myCoH.setInventoryFailed()
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'inventory_failed', exitcode, stdout, stderr)
    return runRebootPhase(myCommandOnHostID)

def parseRebootResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: reboot done (exitcode == 0)" % (myCommandOnHostID))
        updateHistory(myCommandOnHostID, 'reboot_done', exitcode, stdout, stderr)
        return runEndPhase(myCommandOnHostID)
    # failure: immediately give up (FIXME: should not care of this failure)
    logging.getLogger().info("command_on_host #%s: reboot failed (exitcode != 0)" % (myCommandOnHostID))
    updateHistory(myCommandOnHostID, 'reboot_failed', exitcode, stdout, stderr)
    myCoH.reSchedule(myC.getNextConnectionDelay())
    return None

def parsePushOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'upload_in_progress')
        logging.getLogger().info("command_on_host #%s: push order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setUploadToDo()
        myCoH.setCommandStatut('scheduled')
        logging.getLogger().warn("command_on_host #%s: push order not taken in account" % myCommandOnHostID)
        return None

def parsePullOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'upload_in_progress')
        logging.getLogger().info("command_on_host #%s: pull order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setUploadToDo()
        myCoH.setCommandStatut('scheduled')
        logging.getLogger().warn("command_on_host #%s: pull order not taken in account" % myCommandOnHostID)
        return None

def parseExecutionOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'execution_in_progress')
        logging.getLogger().info("command_on_host #%s: execution order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setExecutionToDo()
        myCoH.setCommandStatut('scheduled')
        logging.getLogger().warn("command_on_host #%s: execution order not taken in account" % myCommandOnHostID)
        return None

def parseDeleteOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'delete_in_progress')
        logging.getLogger().info("command_on_host #%s: delete order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        myCoH.setDeleteToDo()
        myCoH.setCommandStatut('scheduled')
        logging.getLogger().warn("command_on_host #%s: delete order not taken in account" % myCommandOnHostID)
        return None

def parseRebootOrder(taken_in_account, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    if taken_in_account: # success
        updateHistory(myCommandOnHostID, 'reboot_in_progress')
        logging.getLogger().info("command_on_host #%s: reboot order taken in account" % myCommandOnHostID)
        return None
    else: # failed: launcher seems to have rejected it
        logging.getLogger().warn("command_on_host #%s: reboot order not taken in account" % myCommandOnHostID)
        return None

def parseWOLError(reason, myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: WOL failed" % myCommandOnHostID)

    updateHistory(myCommandOnHostID, 'wol_failed', 255, '', reason.getErrorMessage())
    myCoH.setScheduled() # as WOL is not mandatory, set to "scheduled" for the upload to be performed
    return runUploadPhase(myCommandOnHostID)

def parsePushError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: push failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parsePullError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: pull failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parseExecutionError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: execution failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'execution_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToExecutionFailed(myC.getNextConnectionDelay())
    # FIXME: should return a failure (but which one ?)
    return None

def parseDeleteError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().warn("command_on_host #%s: delete failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'delete_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToDeleteFailed(myC.getNextConnectionDelay())
    # FIXME: should return a failure (but which one ?)
    return None

def parseInventoryError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.warn("command_on_host #%s: inventory failed, unattented reason: %s" % (myCommandOnHostID, reason))
    myCoH.setInventoryFailed()
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'inventory_failed', 255, '', reason.getErrorMessage())
    # FIXME: should return a failure (but which one ?)
    return None

def parseRebootError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.warn("command_on_host #%s: reboot failed, unattented reason: %s" % (myCommandOnHostID, reason))
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'reboot_failed', 255, '', reason.getErrorMessage())
    # FIXME: should return a failure (but which one ?)
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
