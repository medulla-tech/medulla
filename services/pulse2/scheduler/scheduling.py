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

def getDepencencies(myCommandOnHostID):
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
    # take tasks with a pid not already set
    # take tasks with next launch time in the future
    # TODO: check command state integrity AND command_on_host state integrity in a separtseparate function

    commands_query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)).\
        filter(database.commands_on_host.c.current_state != 'done').\
        filter(database.commands_on_host.c.current_state != 'pause').\
        filter(database.commands_on_host.c.current_state != 'stop').\
        filter(database.commands_on_host.c.current_state != 'upload_in_progress').\
        filter(database.commands_on_host.c.current_state != 'execution_in_progress').\
        filter(database.commands_on_host.c.current_state != 'delete_in_progress').\
        filter(database.commands_on_host.c.current_state != 'inventory_in_progress').\
        filter(database.commands_on_host.c.current_state != 'upload_failed').\
        filter(database.commands_on_host.c.current_state != 'execution_failed').\
        filter(database.commands_on_host.c.current_state != 'delete_failed').\
        filter(database.commands_on_host.c.current_state != 'inventory_failed').\
        filter(database.commands_on_host.c.next_launch_date <= time.strftime("%Y-%m-%d %H:%M:%S")).\
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
            logging.getLogger().info("Scheduler: 0 tasks to start")
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
            # thus we have reach max_slots / group count
            to_reach = int(SchedulerConfig().max_slots / len(aggregated_distribution))

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
        select_from(database.commands_on_host.join(database.commands)).\
        filter(database.commands.c.end_date != '0000-00-00 00:00:00').\
        filter(database.commands.c.end_date <= time.strftime("%Y-%m-%d %H:%M:%S")).\
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
        # enter the maze: stop command
        deffered = stopCommand(q.id)
        if deffered:
            deffereds.append(deffered)
    session.close()
    logging.getLogger().info("Scheduler: %d tasks to stop" % len(deffereds))
    return deffereds

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
        deps =  getDepencencies(myCommandOnHostID)
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
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    if not myC.hasToWOL(): # do not perform wake on lan
        logger.info("command_on_host #%s: WOL ignored" % myCommandOnHostID)
        return runUploadPhase(myCommandOnHostID)
    logger.info("command_on_host #%s: WOL phase" % myCommandOnHostID)

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
    if not myCoH.isUploadImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to upload right now" % myCoH.getId())
        return None
    if myCoH.isUploadDone(): # upload already done, jump to next stage
        logger.info("command_on_host #%s: upload done" % myCoH.getId())
        return runExecutionPhase(myCommandOnHostID)
    if myCoH.isUploadIgnored(): # upload has been ignored, jump to next stage
        logger.info("command_on_host #%s: upload ignored" % myCoH.getId())
        return runExecutionPhase(myCommandOnHostID)
    if not myC.hasSomethingToUpload(): # nothing to upload here, jump to next stage
        logger.info("command_on_host #%s: nothing to upload" % myCoH.getId())
        myCoH.setUploadIgnored()
        return runExecutionPhase(myCommandOnHostID)

    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('transfert'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parsePushError, myCommandOnHostID)

    # if we are here, upload has either previously failed or never be done
    # do copy here
    # first attempt to guess is mirror is local (push) or remove (pull)
    # local mirror starts by "file://"
    if re.compile('^file://').match(myT.mirrors): # prepare a remote_push
        client['protocol'] = 'rsyncssh'
        files_list = []
        for file in myC.files.split("\n"):
            fname = file.split('##')[1]
            if re.compile('^/').search(fname):
                fname = re.compile('^/(.*)$').search(fname).group(1)
            files_list.append(os.path.join(re.compile('^file://(.*)$').search(myT.mirrors).group(1), fname))

        myCoH.setUploadInProgress()
        myCoH.setCommandStatut('upload_in_progress')
        updateHistory(myCommandOnHostID, 'upload_in_progress')

        if SchedulerConfig().mode == 'sync':
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
            mydeffered.addErrback(parsePushError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else: # remote pull
        mirrors = myT.mirrors.split('||')
        mirror = mirrors[0] # TODO: handle when several mirrors are available
        if re.compile('^http://').match(mirror) or re.compile('^https://').match(mirror): # HTTP download
            client['protocol'] = 'wget'
            m1 = mmc.plugins.msc.mirror_api.Mirror(mirror)
            files = myC.files.split("\n")
            files_list = []
            for file in files:
                fid = file.split('##')[0]
                files_list.append(m1.getFilePath(fid))

            myCoH.setUploadInProgress()
            myCoH.setCommandStatut('upload_in_progress')
            updateHistory(myCommandOnHostID, 'upload_in_progress')

            if SchedulerConfig().mode == 'sync':
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
                mydeffered.addErrback(parsePullError, myCommandOnHostID)
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
    myCoH.setUploadIgnored() # can't guess what to do, jump to next phase
    return runExecutionPhase(myCommandOnHostID)

def runExecutionPhase(myCommandOnHostID):
    # Second step : execute file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: execution phase" % myCommandOnHostID)
    if myCoH.isExecutionRunning(): # execution still running, immediately returns
        logger.info("command_on_host #%s: still running" % myCommandOnHostID)
        return None
    if not myCoH.isExecutionImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to execute right now" % myCommandOnHostID)
        return None
    if myCoH.isExecutionDone(): # execution already done, jump to next stage
        logger.info("command_on_host #%s: execution done" % myCommandOnHostID)
        return runDeletePhase(myCommandOnHostID)
    if myCoH.isExecutionIgnored(): # execution previously ignored, jump to next stage
        logger.info("command_on_host #%s: execution ignored" % myCommandOnHostID)
        return runDeletePhase(myCommandOnHostID)
    if not myC.hasSomethingToExecute(): # nothing to execute here, jump to next stage
        logger.info("command_on_host #%s: nothing to execute" % myCommandOnHostID)
        myCoH.setExecutionIgnored()
        return runDeletePhase(myCommandOnHostID)

    # if we are here, execution has either previously failed or never be done
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('execute'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseExecutionError, myCommandOnHostID)

    myCoH.setExecutionInProgress()
    myCoH.setCommandStatut('execution_in_progress')
    updateHistory(myCommandOnHostID, 'execution_in_progress')

    if myC.isQuickAction(): # should be a standard script
        if SchedulerConfig().mode == 'sync':
            mydeffered = callOnBestLauncher(
                'sync_remote_quickaction',
                myCommandOnHostID,
                client,
                myC.start_file,
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
                myC.start_file,
                SchedulerConfig().max_command_time
            )
            mydeffered.addErrback(parseExecutionError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else:
        if SchedulerConfig().mode == 'sync':
            mydeffered = callOnBestLauncher(
                'sync_remote_exec',
                myCommandOnHostID,
                client,
                myC.start_file,
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
                myC.start_file,
                SchedulerConfig().max_command_time
            )
            mydeffered.addErrback(parseExecutionError, myCommandOnHostID)
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
    if not myCoH.isDeleteImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to delete right now" % myCommandOnHostID)
        return None
    if myCoH.isDeleteDone(): # delete has already be done, jump to next stage
        logger.info("command_on_host #%s: delete done" % myCommandOnHostID)
        return runInventoryPhase(myCommandOnHostID)
    if myCoH.isDeleteIgnored(): # delete ignored, jump to next stage
        logger.info("command_on_host #%s: delete ignored" % myCommandOnHostID)
        return runInventoryPhase(myCommandOnHostID)
    if not myC.hasSomethingToDelete(): # nothing to delete here, jump to next stage
        logger.info("command_on_host #%s: nothing to delete" % myCommandOnHostID)
        myCoH.setDeleteIgnored()
        return runInventoryPhase(myCommandOnHostID)
    client = { 'host': chooseClientIP(myT), 'uuid': myT.getUUID(), 'maxbw': myC.maxbw, 'protocol': 'ssh', 'client_check': getClientCheck(myT), 'server_check': getServerCheck(myT), 'action': getAnnounceCheck('delete'), 'group': getClientGroup(myT)}
    if not client['host']: # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseDeleteError, myCommandOnHostID)

    # if we are here, deletion has either previously failed or never be done
    if re.compile('^file://').match(myT.mirrors): # delete from remote push
        files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))

        myCoH.setDeleteInProgress()
        myCoH.setCommandStatut('delete_in_progress')
        updateHistory(myCommandOnHostID, 'delete_in_progress')

        if SchedulerConfig().mode == 'sync':
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
            mydeffered.addErrback(parseDeleteError, myCommandOnHostID)
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
            updateHistory(myCommandOnHostID, 'delete_in_progress')

            if SchedulerConfig().mode == 'sync':
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
                mydeffered.addErrback(parseDeleteError, myCommandOnHostID)
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
    updateHistory(myCommandOnHostID, 'inventory_in_progress')

    if SchedulerConfig().mode == 'sync':
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
        mydeffered.addErrback(parseInventoryError, myCommandOnHostID)
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

    # FIXME: we should add a new stae, then should be able to log the reboot operation
    # updateHistory(myCommandOnHostID, 'reboot_in_progress')

    if SchedulerConfig().mode == 'sync':
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
        mydeffered.addErrback(parseRebootError, myCommandOnHostID)
    else:
        return None
    return mydeffered

def runEndPhase(myCommandOnHostID):
    # Last step : end file
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: end phase" % myCommandOnHostID)
    myCoH.setDone()
    return None

def parseWOLResult(output, myCommandOnHostID):
    logging.getLogger().info("command_on_host #%s: WOL done" % myCommandOnHostID)
    return runUploadPhase(myCommandOnHostID)

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
        return runEndPhase(myCommandOnHostID)
    # failure: immediately give up (FIXME: should not care of this failure)
    logging.getLogger().info("command_on_host #%s: inventory failed (exitcode != 0)" % (myCommandOnHostID))
    myCoH.setInventoryFailed()
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'inventory_failed', exitcode, stdout, stderr)
    return None

def parseRebootResult((exitcode, stdout, stderr), myCommandOnHostID):
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    if exitcode == 0: # success
        logging.getLogger().info("command_on_host #%s: reboot done (exitcode == 0)" % (myCommandOnHostID))
        # updateHistory(myCommandOnHostID, 'reboot_done', exitcode, stdout, stderr)
        return runEndPhase(myCommandOnHostID)
    # failure: immediately give up (FIXME: should not care of this failure)
    logging.getLogger().info("command_on_host #%s: reboot failed (exitcode != 0)" % (myCommandOnHostID))
    # updateHistory(myCommandOnHostID, 'reboot_failed', exitcode, stdout, stderr)
    myCoH.reSchedule(myC.getNextConnectionDelay())
    return None

def parseWOLError(output, myCommandOnHostID):
    logging.getLogger().info("command_on_host #%s: WOL failed" % myCommandOnHostID)
    return runUploadPhase(myCommandOnHostID)

def parsePushError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: push failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parsePullError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: pull failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToUploadFailed(myC.getNextConnectionDelay())
    return None

def parseExecutionError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: execution failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'execution_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToExecutionFailed(myC.getNextConnectionDelay())
    # FIXME: should return a failure (but which one ?)
    return None

def parseDeleteError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logging.getLogger().info("command_on_host #%s: delete failed, unattented reason: %s" % (myCommandOnHostID, reason))
    updateHistory(myCommandOnHostID, 'delete_failed', 255, '', reason.getErrorMessage())
    myCoH.switchToDeleteFailed(myC.getNextConnectionDelay())
    # FIXME: should return a failure (but which one ?)
    return None

def parseInventoryError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: inventory failed, unattented reason: %s" % (myCommandOnHostID, reason))
    myCoH.setInventoryFailed()
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'inventory_failed', 255, '', reason.getErrorMessage())
    # FIXME: should return a failure (but which one ?)
    return None

def parseRebootError(reason, myCommandOnHostID):
    # something goes really wrong: immediately give up
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: reboot failed, unattented reason: %s" % (myCommandOnHostID, reason))
    myCoH.reSchedule(myC.getNextConnectionDelay())
    # updateHistory(myCommandOnHostID, 'reboot_failed', 255, '', reason.getErrorMessage())
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

def getClientCheck(myT):
    return getCheck(SchedulerConfig().client_check, myT);

def getServerCheck(myT):
    return getCheck(SchedulerConfig().server_check, myT);

def getAnnounceCheck(announce):
    if not announce:
        return '';
    if not announce in SchedulerConfig().announce_check:
        return '';
    return SchedulerConfig().announce_check[announce];

def getCheck(check, myT):
    ret = {}
    if not check:
        return ret;
    for key in check:
        if check[key] == 'ipaddr':
            ret.update({key: myT.target_ipaddr})
        if check[key] == 'name':
            ret.update({key: myT.target_name})
        if check[key] == 'uuid':
            ret.update({key: myT.target_uuid})
        if check[key] == 'macaddr':
            ret.update({key: myT.target_macaddr.split('||')[0]})
    return ret;

def getClientGroup(myT):
    return MGAssignAlgoManager().getMachineGroup(myT)

