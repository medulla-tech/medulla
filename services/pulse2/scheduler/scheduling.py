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
from pulse2.scheduler.launchers_driving import chooseLauncher
from pulse2.scheduler.xmlrpc import getProxy
import pulse2.scheduler.network

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

def startAllCommands(scheduler_name):
    # we return a list of deferred
    deffereds = [] # will hold all deferred
    session = sqlalchemy.create_session()
    database = MscDatabase()
    logger = logging.getLogger()
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
    for q in session.query(CommandsOnHost).\
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
        filter(sqlalchemy.or_(database.commands.c.scheduler == '', database.commands.c.scheduler == scheduler_name, database.commands.c.scheduler == None)).\
        all():
        # enter the maze: run command
        deffered = runCommand(q.id)
        if deffered:
            deffereds.append(deffered)
    session.close()
    logging.getLogger().info("Scheduler: %d tasks to perform" % len(deffereds))
    return deffereds

def runCommand(myCommandOnHostID):
    """
        Just a simple start point, chain-load on Upload Pahse
    """
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
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

    # choose launcher
    launcher = chooseLauncher()

    # perform call
    mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
        'wol',
        myT.target_macaddr.split('||')
    )
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
    if myCoH.isUploadRunning(): # upload still running, immediately returns
        logger.info("command_on_host #%s: still running" % myCoH.getId())
        return None
    if not myCoH.isUploadImminent(): # nothing to do right now, give out
        logger.info("command_on_host #%s: nothing to upload right now" % myCommandOnHostID)
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
    # if we are here, upload has either previously failed or never be done
    # do copy here
    # first attempt to guess is mirror is local (push) or remove (pull)
    # local mirror starts by "file://"
    if re.compile('^file://').match(myT.mirrors): # prepare a remote_push
        source_path = re.compile('^file://(.*)$').search(myT.mirrors).group(1)
        files = myC.files.split("\n")
        files_list = []
        for file in files:
            fname = file.split('##')[1]
            if re.compile('^/').search(fname):
                fname = re.compile('^/(.*)$').search(fname).group(1)
            files_list.append(os.path.join(source_path, fname))
        launcher = chooseLauncher()

        target_host = chooseClientIP(myT)
        if target_host == None:
            # We couldn't get an IP address for the target host
            return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parsePushError, myCommandOnHostID)

        target_uuid = myT.getUUID()
        myCoH.setUploadInProgress()
        myCoH.setCommandStatut('upload_in_progress')
        updateHistory(myCommandOnHostID, 'upload_in_progress')
        proxy = getProxy(launcher)
        if SchedulerConfig().mode == 'sync':
            mydeffered = proxy.callRemote(
                'sync_remote_push',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'rsyncssh', 'maxbw': myC.maxbw},
                files_list
            )
            mydeffered.\
                addCallback(parsePushResult, myCommandOnHostID).\
                addErrback(parsePushError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = proxy.callRemote(
                'async_remote_push',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'rsyncssh', 'maxbw': myC.maxbw},
                files_list
            )
            mydeffered.addErrback(parsePushError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else: # remote pull
        mirrors = myT.mirrors.split('||')
        mirror = mirrors[0] # TODO: handle when several mirrors are available
        if re.compile('^http://').match(mirror) or re.compile('^https://').match(mirror): # HTTP download
            m1 = mmc.plugins.msc.mirror_api.Mirror(mirror)
            files = myC.files.split("\n")
            files_list = []
            for file in files:
                fid = file.split('##')[0]
                files_list.append(m1.getFilePath(fid))
            launcher = chooseLauncher()

            target_host = chooseClientIP(myT)
            if target_host == None:
                # We couldn't get an IP address for the target host
                return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parsePushError, myCommandOnHostID)

            target_uuid = myT.getUUID()
            myCoH.setUploadInProgress()
            myCoH.setCommandStatut('upload_in_progress')
            updateHistory(myCommandOnHostID, 'upload_in_progress')
            proxy = getProxy(launcher)            
            if SchedulerConfig().mode == 'sync':
                mydeffered = proxy.callRemote(
                    'sync_remote_pull',
                    myCommandOnHostID,
                    {'host': target_host, 'uuid': target_uuid, 'protocol': 'wget', 'maxbw': myC.maxbw},
                    files_list
                )
                mydeffered.\
                    addCallback(parsePullResult, myCommandOnHostID).\
                    addErrback(parsePullError, myCommandOnHostID)
            elif SchedulerConfig().mode == 'async':
                mydeffered = proxy.callRemote(
                    'async_remote_pull',
                    myCommandOnHostID,
                    {'host': target_host, 'uuid': target_uuid, 'protocol': 'wget', 'maxbw': myC.maxbw},
                    files_list
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
    launcher = chooseLauncher()

    target_host = chooseClientIP(myT)
    if target_host == None:
        # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseExecutionError, myCommandOnHostID)

    target_uuid = myT.getUUID()
    myCoH.setExecutionInProgress()
    myCoH.setCommandStatut('execution_in_progress')
    updateHistory(myCommandOnHostID, 'execution_in_progress')
    if myC.isQuickAction(): # should be a standard script
        proxy = getProxy(launcher)            
        if SchedulerConfig().mode == 'sync':
            logger.info(myC.start_file)
            logger.info(str(target_host))
            logger.info(str(target_uuid))
            mydeffered = proxy.callRemote(
                'sync_remote_quickaction',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                myC.start_file
            )
            mydeffered.\
                addCallback(parseExecutionResult, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = proxy.callRemote(
                'async_remote_quickaction',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                myC.start_file
            )
            mydeffered.addErrback(parseExecutionError, myCommandOnHostID)
        else:
            return None
        return mydeffered
    else:
        proxy = getProxy(launcher)
        if SchedulerConfig().mode == 'sync':
            mydeffered = proxy.callRemote(
                'sync_remote_exec',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                myC.start_file
            )
            mydeffered.\
                addCallback(parseExecutionResult, myCommandOnHostID).\
                addErrback(parseExecutionError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = proxy.callRemote(
                'async_remote_exec',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                myC.start_file
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
        return runEndPhase(myCommandOnHostID)
    if myCoH.isDeleteIgnored(): # delete ignored, jump to next stage
        logger.info("command_on_host #%s: delete ignored" % myCommandOnHostID)
        return runEndPhase(myCommandOnHostID)
    if not myC.hasSomethingToDelete(): # nothing to delete here, jump to next stage
        logger.info("command_on_host #%s: nothing to delete" % myCommandOnHostID)
        myCoH.setDeleteIgnored()
        return runEndPhase(myCommandOnHostID)
    # if we are here, deletion has either previously failed or never be done
    if re.compile('^file://').match(myT.mirrors): # delete from remote push
        files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))
        launcher = chooseLauncher()

        target_host = chooseClientIP(myT)
        if target_host == None:
            # We couldn't get an IP address for the target host
            return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseDeleteError, myCommandOnHostID)

        target_uuid = myT.getUUID()
        myCoH.setDeleteInProgress()
        myCoH.setCommandStatut('delete_in_progress')
        updateHistory(myCommandOnHostID, 'delete_in_progress')
        proxy = getProxy(launcher)        
        if SchedulerConfig().mode == 'sync':
            mydeffered = proxy.callRemote(
                'sync_remote_delete',
                myCommandOnHostID,
                {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                files_list
            )
            mydeffered.\
                addCallback(parseDeleteResult, myCommandOnHostID).\
                addErrback(parseDeleteError, myCommandOnHostID)
        elif SchedulerConfig().mode == 'async':
            mydeffered = proxy.callRemote(
                'async_remote_delete',
                myCommandOnHostID,
                {'host': myT.target_name, 'uuid': target_uuid, 'protocol': 'ssh'},
                files_list
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
            launcher = chooseLauncher()

            target_host = chooseClientIP(myT)
            if target_host == None:
                # We couldn't get an IP address for the target host
                return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseDeleteError, myCommandOnHostID)

            target_uuid = myT.getUUID()
            myCoH.setDeleteInProgress()
            myCoH.setCommandStatut('delete_in_progress')
            updateHistory(myCommandOnHostID, 'delete_in_progress')
            proxy = getProxy(launcher)            
            if SchedulerConfig().mode == 'sync':
                mydeffered = proxy.callRemote(
                    'sync_remote_delete',
                    myCommandOnHostID,
                    {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                    files_list
                )
                mydeffered.\
                    addCallback(parseDeleteResult, myCommandOnHostID).\
                    addErrback(parseDeleteError, myCommandOnHostID)
            elif SchedulerConfig().mode == 'async':
                mydeffered = proxy.callRemote(
                    'async_remote_delete',
                    myCommandOnHostID,
                    {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'},
                    files_list
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
    return runEndPhase(myCommandOnHostID)

def runInventoryPhase(myCommandOnHostID):
    # Run inventory if needed
    (myCoH, myC, myT) = gatherCoHStuff(myCommandOnHostID)
    logger = logging.getLogger()
    logger.info("command_on_host #%s: inventory phase" % myCommandOnHostID)
    if myCoH.isInventoryRunning(): # inventory still running, immediately returns
        logger.info("command_on_host #%s: still inventoring" % myCommandOnHostID)
        return None
    if myCoH.isInventoryDone(): # inventory has already be done, jump to next stage
        logger.info("command_on_host #%s: inventory done" % myCommandOnHostID)
        return runEndPhase(myCommandOnHostID)
    # if we are here, inventory has either previously failed or never be done
    launcher = chooseLauncher()

    target_host = chooseClientIP(myT)
    if target_host == None:
        # We couldn't get an IP address for the target host
        return twisted.internet.defer.fail(Exception("Can't get target IP address")).addErrback(parseInventoryError, myCommandOnHostID)

    target_uuid = myT.getUUID()
    myCoH.setInventoryInProgress()
    updateHistory(myCommandOnHostID, 'inventory_in_progress')

    proxy = getProxy(launcher)
    if SchedulerConfig().mode == 'sync':
        mydeffered = proxy.callRemote(
            'sync_remote_inventory',
            myCommandOnHostID,
            {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'}
        )
        mydeffered.\
            addCallback(parseInventoryResult, myCommandOnHostID).\
            addErrback(parseInventoryError, myCommandOnHostID)
    elif SchedulerConfig().mode == 'async':
        mydeffered = proxy.callRemote(
            'async_remote_inventory',
            myCommandOnHostID,
            {'host': target_host, 'uuid': target_uuid, 'protocol': 'ssh'}
        )
        mydeffered.addErrback(parseInventoryError, myCommandOnHostID)
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
    logging.getLogger().info("command_on_host #%s: delete failed (exitcode != 0)" % (myCommandOnHostID))
    myCoH.setInventoryFailed()
    myCoH.reSchedule(myC.getNextConnectionDelay())
    updateHistory(myCommandOnHostID, 'inventory_failed', exitcode, stdout, stderr)
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
