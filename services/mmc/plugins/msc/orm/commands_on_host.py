# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" Class to map msc.commands_on_host to SA
"""

import logging
import time
import datetime
import sqlalchemy.orm

class CommandsOnHost(object):
    """ Mapping between msc.commands_on_host and SA
    """
    def getId(self):
        return self.id

    def getIdCommand(self):
        return self.fk_commands

    def getIdTarget(self):
        return self.fk_target

### Handle upload states ###
    def isUploadImminent(self):
        result = (self.isScheduled() and self.isInTimeSlot())
        logging.getLogger().debug("isUploadImminent(#%s): %s" % (self.getId(), result))
        return result

    def setUploadIgnored(self):
        self.setUploadStatut('IGNORED')
    def isUploadIgnored(self):
        result = (self.uploaded == 'IGNORED')
        logging.getLogger().debug("isUploadIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setUploadFailed(self):
        self.setUploadStatut('FAILED')
    def isUploadFailed(self):
        result = (self.uploaded == 'FAILED')
        logging.getLogger().debug("isUploadFailed(#%s): %s" % (self.getId(), result))
        return result

    def setUploadDone(self):
        self.setUploadStatut('DONE')
    def isUploadDone(self):
        result = (self.uploaded == 'DONE')
        logging.getLogger().debug("isUploadDone(#%s): %s" % (self.getId(), result))
        return result

    def setUploadInProgress(self):
        self.setUploadStatut('WORK_IN_PROGRESS')
    def isUploadRunning(self):
        result = (self.uploaded == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isUploadRunning(#%s): %s" % (self.getId(), result))
        return result

    def setUploadToDo(self):
        self.setUploadStatut('TODO')
    def isUploadToDo(self):
        result = (self.uploaded == 'TODO')
        logging.getLogger().debug("isUploadToDo(#%s): %s" % (self.getId(), result))
        return result

    def setUploadStatut(self, uploaded):
        self.uploaded = uploaded
        self.flush()
### /Handle upload states ###

### Handle execution states ###
    def isExecutionImminent(self):
        result = ((self.isScheduled() or self.getCommandStatut() == 'upload_done') and self.isInTimeSlot())
        logging.getLogger().debug("isExecutionImminent(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionIgnored(self):
        self.setExecutionStatut('IGNORED')
    def isExecutionIgnored(self):
        result = (self.executed == 'IGNORED')
        logging.getLogger().debug("isExecutionIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionFailed(self):
        self.setExecutionStatut('FAILED')
    def isExecutionFailed(self):
        result = (self.executed == 'FAILED')
        logging.getLogger().debug("isExecutionFailed(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionDone(self):
        self.setExecutionStatut('DONE')
    def isExecutionDone(self):
        result = (self.executed == 'DONE')
        logging.getLogger().debug("isExecutionDone(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionInProgress(self):
        self.setExecutionStatut('WORK_IN_PROGRESS')
    def isExecutionRunning(self):
        result = (self.executed == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isExecutionRunning(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionToDo(self):
        self.setExecutionStatut('TODO')
    def isExecutionToDo(self):
        result = (self.executed == 'TODO')
        logging.getLogger().debug("isExecutionToDo(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionStatut(self, executed):
        self.executed = executed
        self.flush()
### /Handle execution states ###

### Handle deletion states ###
    def isDeleteImminent(self):
        result = ((self.isScheduled() or self.getCommandStatut() == 'execution_done') and self.isInTimeSlot())
        logging.getLogger().debug("isDeleteImminent(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteIgnored(self):
        self.setDeleteStatut('IGNORED')
    def isDeleteIgnored(self):
        result = (self.deleted == 'IGNORED')
        logging.getLogger().debug("isDeleteIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteFailed(self):
        self.setDeleteStatut('FAILED')
    def isDeleteFailed(self):
        result = (self.deleted == 'FAILED')
        logging.getLogger().debug("isDeleteFailed(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteDone(self):
        self.setDeleteStatut('DONE')
    def isDeleteDone(self):
        result = (self.deleted == 'DONE')
        logging.getLogger().debug("isDeleteDone(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteInProgress(self):
        self.setDeleteStatut('WORK_IN_PROGRESS')
    def isDeleteRunning(self):
        result = (self.deleted == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isDeleteRunning(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteToDo(self):
        self.setDeleteStatut('TODO')
    def isDeleteToDo(self):
        result = (self.deleted == 'TODO')
        logging.getLogger().debug("isDeletePossible(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteStatut(self, deleted):
        self.deleted = deleted
        self.flush()
### /Handle deletion states ###

### Handle inventory states ###
    def setInventoryFailed(self):
        self.setCommandStatut('inventory_failed')
    def isInventoryFailed(self):
        result = (self.getCommandStatut() == 'inventory_failed')
        logging.getLogger().debug("isInventoryFailed(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryDone(self):
        self.setCommandStatut('inventory_done')
    def isInventoryDone(self):
        result = (self.getCommandStatut() == 'inventory_done')
        logging.getLogger().debug("isInventoryDone(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryInProgress(self):
        self.setCommandStatut('inventory_in_progress')
    def isInventoryRunning(self):
        result = (self.getCommandStatut() == 'inventory_in_progress')
        logging.getLogger().debug("isInventoryRunning(#%s): %s" % (self.getId(), result))
        return result
### /Handle inventory states ###


### Handle wol states ###
    def setLastWOLAttempt(self):
        self.last_wol_attempt = datetime.datetime.now()
        self.flush()
    def getLastWOLAttempt(self):
        return self.last_wol_attempt

    def isWOLImminent(self):
        result = (self.isScheduled() and self.isInTimeSlot())
        logging.getLogger().debug("isWOLImminent(#%s): %s" % (self.getId(), result))
        return result
    def wasWOLPreviouslyRan(self):
        result = (getLastWOLAttempt() != None) # should check if still in WOL delay
        logging.getLogger().debug("wasWOLPreviouslyRan(#%s): %s" % (self.getId(), result))
        return result

    def setWOLInProgress(self):
        self.setCommandStatut('wol_in_progress')
    def isWOLRunning(self):
        result = (self.getCommandStatut() == 'wol_in_progress')
        logging.getLogger().debug("isWOLRunning(#%s): %s" % (self.getId(), result))
        return result
### /Handle inventory states ###

### Handle general states ###
    def setScheduled(self):
        self.setCommandStatut('scheduled')
    def isScheduled(self):
        result = (self.getCommandStatut() == 'scheduled')
        logging.getLogger().debug("isScheduled(#%s): %s" % (self.getId(), result))
        return result

    def setDone(self):
        self.setCommandStatut('done')
        self.setEndDate() # final state: we may write the date down
    def isDone(self):
        result = (self.getCommandStatut() == 'done')
        logging.getLogger().debug("isDone(#%s): %s" % (self.getId(), result))
        return result

    def setFailed(self):
        self.setCommandStatut('failed')
        self.setEndDate() # final state: we may write the date down
    def isFailed(self):
        result = (self.getCommandStatut() == 'failed')
        logging.getLogger().debug("isFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStop(self):
        self.setCommandStatut('stop')
    def isStopped(self):
        result = (self.getCommandStatut() == 'stop')
        logging.getLogger().debug("isStopped(#%s): %s" % (self.getId(), result))
        return result

    def setPause(self):
        self.setCommandStatut('pause')
    def togglePause(self):
        if self.isPaused():
            self.setScheduled()
        else:
            self.setPause()
    def isPaused(self):
        result = (self.getCommandStatut() == 'pause')
        logging.getLogger().debug("isPaused(#%s): %s" % (self.getId(), result))
        return result

    def setCommandStatut(self, current_state):
        self.current_state = current_state
        self.flush()
    def getCommandStatut(self):
        return self.current_state

    def isInTimeSlot(self):
        if self.next_launch_date:
            return time.mktime(self.next_launch_date.timetuple()) <= time.time()
        else:
            return True
### /Handle general states ###

### Handle launcher ###
    def setCurrentLauncher(self, launcher):
        self.current_launcher = launcher
        self.flush()
    def getCurrentLauncher(self):
        return self.current_launcher
### /Handle launcher ###

### Handle local proxy stuff ###
    def isProxyClient(self):
        # I'm a client if:
        # fk_use_as_proxy is set (ie I found a proxy server)
        # fk_use_as_proxy is not equal to my id (ie the proxy server is not me)
        result = (self.fk_use_as_proxy != None and self.fk_use_as_proxy != self.id)
        logging.getLogger().debug("isProxyClient(#%s): %s" % (self.getId(), result))
        return result
    def isProxyServer(self):
        # I'm a server if:
        # order_in_proxy is set (ie I have chance to become a server)
        # fk_use_as_proxy is equal to my id (ie the proxy server is me)
        result = (self.order_in_proxy != None and self.id == self.fk_use_as_proxy)
        logging.getLogger().debug("isProxyServer(#%s): %s" % (self.getId(), result))
        return result

    def getOrderInProxy(self):
        return self.order_in_proxy

    def setUsedProxy(self, coh_id):
        self.fk_use_as_proxy = coh_id
    def getUsedProxy(self):
        return self.fk_use_as_proxy

### /Handle local proxy stuff ###

### Misc state changes handling  ###
    def reSchedule(self, delay):
        """ Reschedule when something went wrong """
        if self.attempts_left < 1: # no attempts left
            self.setFailed()
        elif self.attempts_left == 1: # was the last attempt: tag as done, no rescheduling
            self.attempts_left -= 1
            self.flush()
            self.setFailed()
        else: # reschedule in other cases
            self.attempts_left -= 1
            self.next_launch_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + delay * 60))
            self.flush()
            self.setScheduled()

    def switchToUploadFailed(self, delay = 0):
        """
            goes in "upload_failed" state only if we where in
            "upload_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay)                              # always reschedule
        self.setUploadFailed()                              # set task status
        if self.getCommandStatut() == 'upload_in_progress': # normal flow
            self.setCommandStatut('upload_failed')          # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToUploadDone(self):
        """
            goes in "upload_done" state only if we where in
            "upload_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setUploadDone()                                # set task status
        if self.getCommandStatut() == 'upload_in_progress': # normal flow
            self.setCommandStatut('upload_done')            # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToExecutionFailed(self, delay = 0):
        """
            goes in "execution_failed" state only if we where in
            "execution_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay)                              # always reschedule
        self.setExecutionFailed()                           # set task status
        if self.getCommandStatut() == 'execution_in_progress': # normal flow
            self.setCommandStatut('execution_failed')       # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToExecutionDone(self):
        """
            goes in "execution_done" state only if we where in
            "execution_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setExecutionDone()                             # set task status
        if self.getCommandStatut() == 'execution_in_progress': # normal flow
            self.setCommandStatut('execution_done')         # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToDeleteFailed(self, delay = 0):
        """
            goes in "delete_failed" state only if we where in
            "delete_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay)                              # always reschedule
        self.setDeleteFailed()                              # set task status
        if self.getCommandStatut() == 'delete_in_progress': # normal flow
            self.setCommandStatut('delete_failed')          # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToDeleteDone(self):
        """
            goes in "delete_done" state only if we where in
            "delete_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setDeleteDone()                                # set task status
        if self.getCommandStatut() == 'delete_in_progress': # normal flow
            self.setCommandStatut('delete_done')            # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

### /Misc state changes handling  ###

    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.orm.create_session()
        session.save_or_update(self)
        session.flush()
        session.close()

    def toH(self):
        return {
            'id': self.id,
            'fk_commands': self.fk_commands,
            'host': self.host,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'current_state': self.current_state,
            'uploaded': self.uploaded,
            'executed': self.executed,
            'deleted': self.deleted,
            'next_launch_date': self.next_launch_date,
            'attempts_left': self.attempts_left,
            'next_attempt_date_time': self.next_attempt_date_time,
            'current_launcher': self.current_launcher,
            'scheduler': self.scheduler,
            'last_wol_attempt': self.last_wol_attempt,
            'order_in_proxy': self.order_in_proxy,
            'fk_use_as_proxy': self.fk_use_as_proxy
        }

    def setStartDate(self):
        """
        Set start_date field to current time, only if the field has not been
        already set.
        """
        if not self.start_date:
            self.start_date = datetime.datetime.now()
        self.flush()

    def setEndDate(self):
        """
        Set end_date field to current time
        """
        self.end_date = datetime.datetime.now()
        self.flush()

def startCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setScheduled()
    myCommandOnHost.next_launch_date = "0000-00-00 00:00:00"
    myCommandOnHost.flush()

def stopCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setStop()
    if myCommandOnHost.isUploadRunning():
        myCommandOnHost.setUploadFailed()
    if myCommandOnHost.isExecutionRunning():
        myCommandOnHost.setExecutionFailed()
    if myCommandOnHost.isDeleteRunning():
        myCommandOnHost.setDeleteFailed()
    myCommandOnHost.next_launch_date = "2031-12-31 23:59:59"
    myCommandOnHost.flush()

def togglePauseCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.togglePause()

