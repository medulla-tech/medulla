# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

""" Class to map msc.commands_on_host to SA
"""

import logging
import time
import datetime
import sqlalchemy.orm

class CommandsOnHost(object):
    """ Mapping between msc.commands_on_host and SA
    """

    phases = []

    def getId(self):
        return self.id

    def getIdCommand(self):
        return self.fk_commands

    def getIdTarget(self):
        return self.fk_target

### Handle general states ###
    def setStateRunning(self):
        self.setCommandStatut('in_progress')
    def isStateRunning(self):
        result = self.getCommandStatut() == 'in_progress'
        logging.getLogger().debug("isStateRunning(#%s): %s" % (self.getId(), result))
        return result

    def setStateScheduled(self):
        self.setCommandStatut('scheduled')
    def isStateScheduled(self):
        result = (self.getCommandStatut() == 'scheduled' or self.getCommandStatut() == 're_scheduled')
        logging.getLogger().debug("isStateScheduled(#%s): %s" % (self.getId(), result))
        return result

    def setStateDone(self):
        self.setCommandStatut('done')
        self.setEndDate() # final state: we may write the date down
    def isStateDone(self):
        result = (self.getCommandStatut() == 'done')
        logging.getLogger().debug("isStateDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateFailed(self):
        self.setCommandStatut('failed')
        self.setEndDate() # final state: we may write the date down
    def isStateFailed(self):
        result = (self.getCommandStatut() == 'failed')
        logging.getLogger().debug("isStateFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateStopped(self):
        self.setCommandStatut('stopped')
    def isStateStopped(self):
        if self.getCommandStatut() == 'stop': # 'stop' deprecated a while ago, but may still be present, so we take the opportunity to fix it here
            logging.getLogger().warn("Detected command #%s in deprecated state 'stop', setting it to 'stopped'")
            self.setStateStopped()
        result = (self.getCommandStatut() == 'stop' or self.getCommandStatut() == 'stopped')
        logging.getLogger().debug("isStateStopped(#%s): %s" % (self.getId(), result))
        return result

    def setStatePaused(self):
        self.setCommandStatut('pause')
    def isStatePaused(self):
        result = (self.getCommandStatut() == 'pause' or self.getCommandStatut() == 'paused')
        logging.getLogger().debug("isStatePaused(#%s): %s" % (self.getId(), result))
        return result
    def toggleStatePaused(self):
        if self.isStatePaused():
            self.setStateScheduled()
        else:
            self.setStatePaused()

    def setStateOverTimed(self):
        self.setCommandStatut('over_timed')
    def isStateOverTimed(self):
        result = (self.getCommandStatut() == 'over_timed')
        logging.getLogger().debug("isStateOverTimed(#%s): %s" % (self.getId(), result))
        return result

    def setStateUnreachable(self):
        self.setCommandStatut('not_reachable')
    def isStateUnreachable(self):
        result = (self.getCommandStatut() == 'not_reachable')
        logging.getLogger().debug("isStateUnreachable(#%s): %s" % (self.getId(), result))
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
        result = (self.order_in_proxy != None and self.fk_use_as_proxy == self.id)
        logging.getLogger().debug("isProxyServer(#%s): %s" % (self.getId(), result))
        return result
    def isLocalProxy(self):
        # I'm a server if:
        # order_in_proxy is set (ie I have chance to become a server)
        # fk_use_as_proxy is equal to my id (ie the proxy server is me)
        result = (self.order_in_proxy != None)
        logging.getLogger().debug("isLocalProxy(#%s): %s" % (self.getId(), result))
        return result

    def setOrderInProxy(self, order_in_proxy):
        self.order_in_proxy = int(order_in_proxy)
        self.flush()
    def getOrderInProxy(self):
        return self.order_in_proxy

    def setMaxClientsPerProxy(self, max_clients_per_proxy):
        self.max_clients_per_proxy = int(max_clients_per_proxy)
        self.flush()
    def getMaxClientsPerProxy(self):
        return self.max_clients_per_proxy

    def setUsedProxy(self, coh_id):
        self.fk_use_as_proxy = int(coh_id)
        self.flush()
    def getUsedProxy(self):
        return self.fk_use_as_proxy

    def get_next_launch_timestamp(self):
        if isinstance(self.next_launch_date, datetime.datetime):
            return time.mktime(self.next_launch_date.timetuple())
        elif isinstance(self.next_launch_date, str):
            return int(datetime.datetime.strptime(self.next_launch_date,"%Y-%m-%d %H:%M:%S").strftime("%s"))

    def is_out_of_attempts(self):
        return self.attempts_failed == self.attempts_total

    @property
    def days_delta(self):
        """ number of days between start date and end_date"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def attempts_total(self):
        """ Total of attempts for all days """
        return self.days_delta * self.attempts_left


### Misc state changes handling  ###
    def reSchedule(self, launch_date, decrement):
        """ Reschedule when something went wrong
            return True if processing can continue
            else return False
        """
        if decrement:
            if self.attempts_total > self.attempts_failed :
                self.attempts_failed += 1
        self.next_launch_date = launch_date 
        self.flush()
        return True

    def setStateInProgress(self):
        self.setCommandStatut('in_progress')

    def setPhaseFailed(self):
        self.setCommandStatut('phase_failed')
### /Misc state changes handling  ###

    def extend(self, start_date, end_date, attempts):
        self.start_date = start_date
        self.next_launch_date = start_date
        self.end_date = end_date
        #self.attempts_left += attempts
        self.attempts_failed = 0
        self.flush()


    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.orm.create_session()
        session.add(self)
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
            'stage': self.stage,
            'awoken': self.awoken,
            'imgmenu_changed': self.imgmenu_changed,
            'uploaded': self.uploaded,
            'executed': self.executed,
            'deleted': self.deleted,
            'rebooted': self.rebooted,
            'inventoried': self.inventoried,
            'halted': self.halted,
            'next_launch_date': self.next_launch_date,
            'attempts_left': self.attempts_left,
            'next_attempt_date_time': self.next_attempt_date_time,
            'current_launcher': self.current_launcher,
            'scheduler': self.scheduler,
            'last_wol_attempt': self.last_wol_attempt,
            'order_in_proxy': self.order_in_proxy,
            'fk_use_as_proxy': self.fk_use_as_proxy,
            'max_clients_per_proxy': self.max_clients_per_proxy,
            'phases' : self.phases
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

    def setBalance(self, balance):#, failed_attempts_nbr):
        """
        Set balance value to calculate next_launch_date
        """
        self.balance = balance
        self.flush()

def startCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setStateScheduled()
    myCommandOnHost.next_launch_date = "0000-00-00 00:00:00"
    myCommandOnHost.flush()

def stopCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setStateStopped()
    myCommandOnHost.next_launch_date = "2031-12-31 23:59:59"
    myCommandOnHost.flush()

def togglePauseCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.toggleStatePaused()

class CoHManager :
    """ Manager class to encapsulate the methods bellow. """

    @classmethod
    def setBalances (cls, coh_balances):
        """
        Multiple update of balances.

        @param coh_balances: list of tuples (id, balance)
        @type coh_balances: list
        """
        session = sqlalchemy.orm.create_session()
        for coh_id, balance in coh_balances :
            myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
            if myCommandOnHost :
                myCommandOnHost.balance = balance
                session.add(myCommandOnHost)
                session.flush()
        session.close()

    @classmethod
    def setCoHsStates(cls, ids, state):
        """
        Multiple setting the current state to <state>.

        @param ids: list of ids to update
        @type ids: list
        """
        session = sqlalchemy.orm.create_session()
        for id in ids :
            myCommandOnHost = session.query(CommandsOnHost).get(id)
            if myCommandOnHost :
                myCommandOnHost.current_state = state
                session.add(myCommandOnHost)
                session.flush()
        session.close()

    @classmethod
    def setCoHsStateOverTimed(cls, ids):
        """
        Multiple setting the current state to 'overtimed'.

        @param ids: list of ids to update
        @type ids: list
        """
        CoHManager.setCoHsStates(ids, "over_timed")


    @classmethod
    def setCoHsStateStopped(cls, ids):
        """
        Multiple setting the current state to 'stopped'.

        @param ids: list of ids to update
        @type ids: list

        @return: number of stopped cohs per command
        @rtype: dict
        """
        cmd_groups = {}
        session = sqlalchemy.orm.create_session()
        for id in ids :
            coh = session.query(CommandsOnHost).get(id)
            if coh :
                if coh.isStateDone():
                    continue
                coh.current_state = "stopped"
                coh.next_launch_date = coh.end_date
                session.add(coh)
                session.flush()
                if coh.fk_commands in cmd_groups :
                    cmd_groups[coh.fk_commands] += 1
                else :
                    cmd_groups[coh.fk_commands] = 0
                
        session.close()
        return cmd_groups


    @classmethod
    def setCoHsStateFailed(cls, ids):
        """
        Multiple setting the current state to 'failed'.

        @param ids: list of ids to update
        @type ids: list
        """
        CoHManager.setCoHsStates(ids, "failed")


