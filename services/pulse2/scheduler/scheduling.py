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

# Twisted modules
import twisted.web.xmlrpc
import twisted.internet

# MMC plugins
from mmc.plugins.msc.database import MscDatabase
import mmc.plugins.msc.mirror_api

# ORM mappings
from mmc.plugins.msc.orm.commands import Commands
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost
from mmc.plugins.msc.orm.commands_history import CommandsHistory
from mmc.plugins.msc.orm.target import Target

import pulse2.scheduler.config
import pulse2.scheduler.network

class Scheduler(object):
    """
    This is our main class. A scheduler object can virtualy handle
    every stage of a deployment.

    It automagicaly activate a SQL connection to the MSC database at
    init time.

    Deployment funcs are always build on the same model:
      - the command_on_host ID as main arg
      - using gatherDetails:
        - get a SQL session object
        - get a MSC database object
        - get the CommandOnHost object
        - get the corresponding Command object
        - get the corresponding Target object
        - get a logger object
      - prepare stuff
      - run stuff async-style, attaching to the returning deffered:
        - a cb to handle "normal" behavior
        - a eb to handle 'erratic" behavior"
    """

    def __init__(self):
        MscDatabase().activate()

    def gatherStuff(self):
        """ handy function to gather wdely used objects """
        session = sqlalchemy.create_session()
        database = MscDatabase()
        logger = logging.getLogger()
        return (session, database, logger)

    def gatherCoHStuff(self, idCommandOnHost):
        """ same as gatherStuff(), this time for a particular CommandOnHost """
        session = sqlalchemy.create_session()
        database = MscDatabase()
        myCommandOnHost = session.query(CommandsOnHost).get(idCommandOnHost)
        myCommand = session.query(Commands).get(myCommandOnHost.getIdCommand())
        myTarget = session.query(Target).filter(database.target.c.id_command == myCommandOnHost.getIdCommand()).limit(1)[0]
        session.close()
        return (myCommandOnHost, myCommand, myTarget)

    def startAllCommands(self):
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
            filter(database.commands_on_host.c.current_pid == -1).\
            filter(database.commands_on_host.c.next_launch_date <= time.strftime("%Y-%m-%d %H:%M:%S")).\
            all():
            # enter the maze: run command
            deffered = self.runCommand(q.id_command_on_host)
            if deffered:
                deffereds.append(deffered)
        session.close()
        return deffereds

    def runCommand(self, myCommandOnHostID):
        """ Just a simple start point, chain-load on Upload Pahse
        """
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("going to do command_on_host #%s from command #%s" % (myCoH.getId(), myCoH.getIdCommand()))
        logger.debug("command_on_host state is %s" % myCoH.toH())
        logger.debug("command state is %s" % myC.toH())
        return self.runWOLPhase(myCommandOnHostID)

    def runWOLPhase(self, myCommandOnHostID):
        """ Attempt do see if a wake-on-lan should be done
        """
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if not myC.hasToWOL(): # do not perform wake on lan
            logger.info("command_on_host #%s: WOL ignored" % myCommandOnHostID)
            return self.runUploadPhase(myCommandOnHostID)
        logger.info("command_on_host #%s: WOL phase" % myCommandOnHostID)
        mydeffered = pulse2.scheduler.network.wolClient(myT.target_macaddr.split('||'))
        mydeffered.\
            addCallback(self.parseWOLResult, myCommandOnHostID).\
            addErrback(self.parseWOLError, myCommandOnHostID)
        return mydeffered

    def runUploadPhase(self, myCommandOnHostID):
        """ Handle first Phase: upload time
        """
        # First step : copy files
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: copy phase" % myCommandOnHostID)
        if myCoH.isUploadRunning(): # upload still running, immediately returns
            logger.info("command_on_host #%s: still running" % myCoH.getId())
            return None
        if myCoH.isUploadDone(): # upload already done, jump to next stage
            logger.info("command_on_host #%s: upload done" % myCoH.getId())
            return self.runExecutionPhase(myCommandOnHostID)
        if myCoH.isUploadIgnored(): # upload has been ignored, jump to next stage
            logger.info("command_on_host #%s: upload ignored" % myCoH.getId())
            return self.runExecutionPhase(myCommandOnHostID)
        if not myC.hasSomethingToUpload(): # nothing to upload here, jump to next stage
            logger.info("command_on_host #%s: nothing to upload" % myCoH.getId())
            myCoH.setUploadIgnored()
            return self.runExecutionPhase(myCommandOnHostID)
        # if we are here, upload has either previously failed or never be done
        # do copy here
        # first attempt to guess is mirror is local (push) or remove (pull)
        # local mirror starts by "file://"
        if re.compile('^file://').match(myT.mirrors): # prepare a remote_push
            source_path = re.compile('^file://(.*)$').search(myT.mirrors).group(1)
            files_list = map(lambda(a): os.path.join(myC.path_source, a), myC.files.split("\n"))
            launcher = chooseLauncher()
            target_host = pulse2.scheduler.network.chooseClientIP(myT)
            myCoH.setUploadInProgress()
            updateHistory(myCommandOnHostID, 'upload_in_progress')
            mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                'sync_remote_push',
                myCommandOnHostID,
                {'host': target_host, 'protocol': 'scp'},
                files_list
            )
            mydeffered.\
                addCallback(self.parsePushResult, myCommandOnHostID).\
                addErrback(self.parsePushError, myCommandOnHostID)
            return mydeffered
        else: # remote pull
            mirrors = myT.mirrors.split('||')
            mirror = mirrors[0] # TODO: handle when several mirrors are available
            if re.compile('^http://').match(mirror): # HTTP download
                m1 = mmc.plugins.msc.mirror_api.Mirror(mirror)
                files = myC.files.split("\n")
                files_list = []
                for file in files:
                    fid = file.split('##')[0]
                    files_list.append(m1.getFilePath(fid))
                launcher = chooseLauncher()
                target_host = pulse2.scheduler.network.chooseClientIP(myT)
                myCoH.setUploadInProgress()
                updateHistory(myCommandOnHostID, 'upload_in_progress')
                mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                    'sync_remote_pull',
                    myCommandOnHostID,
                    {'host': target_host, 'protocol': 'wget'},
                    files_list
                )
                mydeffered.\
                    addCallback(self.parsePullResult, myCommandOnHostID).\
                    addErrback(self.parsePullError, myCommandOnHostID)
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
        return self.runExecutionPhase(myCommandOnHostID)

    def runExecutionPhase(self, myCommandOnHostID):
        # Second step : execute file
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: execution phase" % myCommandOnHostID)
        if myCoH.isExecutionRunning(): # execution still running, immediately returns
            logger.info("command_on_host #%s: still running" % myCommandOnHostID)
            return None
        if myCoH.isExecutionDone(): # execution already done, jump to next stage
            logger.info("command_on_host #%s: upload done" % myCommandOnHostID)
            return self.runDeletePhase(myCommandOnHostID)
        if myCoH.isExecutionIgnored(): # execution previously ignored, jump to next stage
            logger.info("command_on_host #%s: upload ignored" % myCommandOnHostID)
            return self.runDeletePhase(myCommandOnHostID)
        if not myC.hasSomethingToExecute(): # nothing to execute here, jump to next stage
            logger.info("command_on_host #%s: nothing to execute" % myCommandOnHostID)
            myCoH.setExecutionIgnored()
            return self.runDeletePhase(myCommandOnHostID)
        # if we are here, execution has either previously failed or never be done
        launcher = chooseLauncher()
        target_host = pulse2.scheduler.network.chooseClientIP(myT)
        myCoH.setExecutionInProgress()
        updateHistory(myCommandOnHostID, 'execution_in_progress')
        if myC.isQuickAction(): # should be a standard script
            mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                'async_remote_quickaction',
                myCommandOnHostID,
                {'host': target_host, 'protocol': 'ssh'},
                myC.start_file
            )
            mydeffered.\
                addCallback(self.parseExecutionResult, myCommandOnHostID).\
                addErrback(self.parseExecutionError, myCommandOnHostID)
            return mydeffered
        else:
            mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                'sync_remote_exec',
                myCommandOnHostID,
                {'host': target_host, 'protocol': 'ssh'},
                myC.start_file
            )
            mydeffered.\
                addCallback(self.parseExecutionResult, myCommandOnHostID).\
                addErrback(self.parseExecutionError, myCommandOnHostID)
            return mydeffered

    def runDeletePhase(self, myCommandOnHostID):
        # Third step : delete file
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: delete phase" % myCommandOnHostID)
        if myCoH.isDeleteRunning(): # delete still running, immediately returns
            logging.getLogger().info("command_on_host #%s: still deleting" % myCommandOnHostID)
            return None
        if myCoH.isDeleteDone(): # delete has already be done, jump to next stage
            logger.info("command_on_host #%s: delete done" % myCommandOnHostID)
            return self.runEndPhase(myCommandOnHostID)
        if myCoH.isDeleteIgnored(): # delete ignored, jump to next stage
            logger.info("command_on_host #%s: delete ignored" % myCommandOnHostID)
            return self.runEndPhase(myCommandOnHostID)
        if not myC.hasSomethingToDelete(): # nothing to delete here, jump to next stage
            logger.info("command_on_host #%s: nothing to delete" % myCommandOnHostID)
            myCoH.setDeleteIgnored()
            return self.runEndPhase(myCommandOnHostID)
        # if we are here, deletion has either previously failed or never be done
        if re.compile('^file://').match(myT.mirrors): # delete from remote push
            files_list = myC.files.split("\n")
            target_path = myC.path_destination
            launcher = chooseLauncher()
            target_host = pulse2.scheduler.network.chooseClientIP(myT)
            myCoH.setDeleteInProgress()
            updateHistory(myCommandOnHostID, 'deletion_in_progress')
            mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                'sync_remote_delete',
                myCommandOnHostID,
                {'host': myT.target_name, 'protocol': 'ssh'},
                files_list
            )
            mydeffered.\
                addCallback(self.parseDeleteResult, myCommandOnHostID).\
                addErrback(self.parseDeleteError, myCommandOnHostID)
            return mydeffered
        else: # delete from remote pull
            mirrors = myT.mirrors.split('||')
            mirror = mirrors[0] # TODO: handle when several mirrors are available
            if re.compile('^http://').match(mirror): # HTTP download
                files_list = map(lambda(a): a.split('/').pop(), myC.files.split("\n"))
                launcher = chooseLauncher()
                target_host = pulse2.scheduler.network.chooseClientIP(myT)
                myCoH.setDeleteInProgress()
                updateHistory(myCommandOnHostID, 'deletion_in_progress')
                mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
                    'sync_remote_delete',
                    myCommandOnHostID,
                    {'host': target_host, 'protocol': 'ssh'},
                    files_list
                )
                mydeffered.\
                    addCallback(self.parseDeleteResult, myCommandOnHostID).\
                    addErrback(self.parseDeleteError, myCommandOnHostID)
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
        return self.runEndPhase(myCommandOnHostID)

    def runInventoryPhase(self, myCommandOnHostID):
        # Run inventory if needed
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: inventory phase" % myCommandOnHostID)
        if myCoH.isInventoryRunning(): # inventory still running, immediately returns
            logger.info("command_on_host #%s: still inventoring" % myCommandOnHostID)
            return None
        if myCoH.isInventoryDone(): # inventory has already be done, jump to next stage
            logger.info("command_on_host #%s: inventory done" % myCommandOnHostID)
            return self.runEndPhase(myCommandOnHostID)
        # if we are here, inventory has either previously failed or never be done
        launcher = chooseLauncher()
        target_host = pulse2.scheduler.network.chooseClientIP(myT)
        myCoH.setInventoryInProgress()
        updateHistory(myCommandOnHostID, 'inventory_in_progress')
        mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
            'sync_remote_inventory',
            myCommandOnHostID,
            {'host': target_host, 'protocol': 'ssh'},
        )
        mydeffered.\
            addCallback(self.parseInventoryResult, myCommandOnHostID).\
            addErrback(self.parseInventoryError, myCommandOnHostID)
        return mydeffered

    def runEndPhase(self, myCommandOnHostID):
        # Last step : end file
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logging.getLogger().info("command_on_host #%s: end phase" % myCommandOnHostID)
        myCoH.setDone()
        return None

    def parseWOLResult(self, output, myCommandOnHostID):
        logging.getLogger().info("command_on_host #%s: WOL done" % myCommandOnHostID)
        return self.runUploadPhase(myCommandOnHostID)

    def parsePushResult(self, (exitcode, stdout, stderr), myCommandOnHostID):
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if exitcode == 0: # success
            logger.info("command_on_host #%s: push done (exitcode == 0)" % myCommandOnHostID)
            myCoH.setUploadDone()
            updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
            return self.runExecutionPhase(myCommandOnHostID)
        # failure: immediately give up
        logger.info("command_on_host #%s: push failed (exitcode != 0)" % myCommandOnHostID)
        updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
        myCoH.setUploadFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        return None

    def parsePullResult(self, (exitcode, stdout, stderr), myCommandOnHostID):
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if exitcode == 0: # success
            logger.info("command_on_host #%s: pull done (exitcode == 0)" % myCommandOnHostID)
            myCoH.setUploadDone()
            updateHistory(myCommandOnHostID, 'upload_done', exitcode, stdout, stderr)
            return self.runExecutionPhase(myCommandOnHostID)
        # failure: immediately give up
        logger.info("command_on_host #%s: pull failed (exitcode != 0)" % myCommandOnHostID)
        myCoH.setUploadFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'upload_failed', exitcode, stdout, stderr)
        return None

    def parseExecutionResult(self, (exitcode, stdout, stderr), myCommandOnHostID):
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if exitcode == 0: # success
            logger.info("command_on_host #%s: execution done (exitcode == 0)" % (myCommandOnHostID))
            myCoH.setExecutionDone()
            updateHistory(myCommandOnHostID, 'execution_done', exitcode, stdout, stderr)
            return self.runDeletePhase(myCommandOnHostID)
        # failure: immediately give up
        logger.info("command_on_host #%s: execution failed (exitcode != 0)" % (myCommandOnHostID))
        myCoH.setExecutionFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'execution_failed', exitcode, stdout, stderr)
        return None

    def parseDeleteResult(self, (exitcode, stdout, stderr), myCommandOnHostID):
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if exitcode == 0: # success
            logger.info("command_on_host #%s: delete done (exitcode == 0)" % (myCommandOnHostID))
            myCoH.setDeleteDone()
            updateHistory(myCommandOnHostID, 'delete_done', exitcode, stdout, stderr)
            return self.runInventoryPhase(myCommandOnHostID)
        # failure: immediately give up
        logger.info("command_on_host #%s: delete failed (exitcode != 0)" % (myCommandOnHostID))
        myCoH.setDeleteFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'delete_failed', exitcode, stdout, stderr)
        return None

    def parseInventoryResult(self, (exitcode, stdout, stderr), myCommandOnHostID):
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        if exitcode == 0: # success
            logging.getLogger().info("command_on_host #%s: inventory done (exitcode == 0)" % (myCommandOnHostID))
            myCoH.setInventoryDone()
            updateHistory(myCommandOnHostID, 'inventory_done', exitcode, stdout, stderr)
            return self.runEndPhase(myCommandOnHostID)
        # failure: immediately give up (FIXME: should not care of this failure)
        logging.getLogger().info("command_on_host #%s: delete failed (exitcode != 0)" % (myCommandOnHostID))
        myCoH.setInventoryFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'inventory_failed', exitcode, stdout, stderr)
        return None

    def parseWOLError(self, output, myCommandOnHostID):
        logging.getLogger().info("command_on_host #%s: WOL failed" % myCommandOnHostID)
        return self.runUploadPhase(myCommandOnHostID)

    def parsePushError(self, reason, myCommandOnHostID):
        # something goes really wrong: immediately give up
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: push failed, unattented reason: %s" % (myCommandOnHostID, reason))
        myCoH.setUploadFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
        # FIXME: should return a failure (but which one ?)
        return None

    def parsePullError(self, reason, myCommandOnHostID):
        # something goes really wrong: immediately give up
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: pull failed, unattented reason: %s" % (myCommandOnHostID, reason))
        myCoH.setUploadFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'upload_failed', 255, '', reason.getErrorMessage())
        # FIXME: should return a failure (but which one ?)
        return None

    def parseExecutionError(self, reason, myCommandOnHostID):
        # something goes really wrong: immediately give up
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: execution failed, unattented reason: %s" % (myCommandOnHostID, reason))
        myCoH.setExecutionFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'execution_failed', 255, '', reason.getErrorMessage())
        # FIXME: should return a failure (but which one ?)
        return None

    def parseDeleteError(self, reason, myCommandOnHostID):
        # something goes really wrong: immediately give up
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: delete failed, unattented reason: %s" % (myCommandOnHostID, reason))
        myCoH.setDeleteFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'delete_failed', 255, '', reason.getErrorMessage())
        # FIXME: should return a failure (but which one ?)
        return None

    def parseInventoryError(self, reason, myCommandOnHostID):
        # something goes really wrong: immediately give up
        (myCoH, myC, myT) = self.gatherCoHStuff(myCommandOnHostID)
        logger = logging.getLogger()
        logger.info("command_on_host #%s: inventory failed, unattented reason: %s" % (myCommandOnHostID, reason))
        myCoH.setInventoryFailed()
        myCoH.reSchedule(myC.getNextConnectionDelay())
        updateHistory(myCommandOnHostID, 'inventory_failed', 255, '', reason.getErrorMessage())
        # FIXME: should return a failure (but which one ?)
        return None

def updateHistory(id_command_on_host, state, error_code=0, stdout='', stderr=''):
    encoding = pulse2.scheduler.config.SchedulerConfig().dbencoding
    history = CommandsHistory()
    history.id_command_on_host = id_command_on_host
    history.date = time.time()
    history.error_code = error_code
    history.stdout = stdout.encode(encoding, 'replace')
    history.stderr = stderr.encode(encoding, 'replace')
    history.state = state
    history.flush()

def chooseLauncher():
    """ Select a launcher """
    import random
    launchers = pulse2.scheduler.config.SchedulerConfig().launchers
    launcher = random.sample(launchers.keys(), 1).pop()
    return 'http://%s:%s' % (launchers[launcher]['host'], launchers[launcher]['port'])
