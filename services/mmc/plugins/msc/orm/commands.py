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

""" Class to map msc.commands to SA
"""

# big modules
import logging
import sqlalchemy

# MSC modules
import mmc.plugins.msc.database
import mmc.plugins.msc.machines

# ORM mappings
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost

class Commands(object):
    """ Mapping between msc.commands and SA
    """
    def getId(self):
        return self.id

    def getNextConnectionDelay(self):
        return self.next_connection_delay

    def dispatch(self, ctx):
        """
        According to the current command (self), inject as many lines in
        CommandsOnHost as required (i.e. one per target)
        """
        if self.isDispatched():
            return None

        # gather usefull stuff ...
        database = mmc.plugins.msc.database.MscDatabase()
        machines = mmc.plugins.msc.machines.Machines()

        logger = logging.getLogger()
        logger.debug('Start dispatch of command %s' % self.id)

        session = sqlalchemy.create_session()        
        # iterate over available target
        for myTarget in database.getTargets(self.id):
            logger.debug("Create new command on host : %s" % (myTarget.target_name))
            myCommandOnHost = CommandsOnHost()
            myCommandOnHost.fk_commands = self.id
            myCommandOnHost.host = myTarget.target_name # maybe uuid ...
            myCommandOnHost.start_date = self.start_date or "0000-00-00 00:00:00"
            myCommandOnHost.end_date = self.end_date or "0000-00-00 00:00:00"
            myCommandOnHost.next_launch_date = self.start_date or "0000-00-00 00:00:00"
            myCommandOnHost.current_state = 'scheduled'
            myCommandOnHost.uploaded = 'TODO'
            myCommandOnHost.executed = 'TODO'
            myCommandOnHost.deleted = 'TODO'
            myCommandOnHost.number_attempt_connection_remains = self.max_connection_attempt
            myCommandOnHost.next_attempt_date_time = 0
            session.save(myCommandOnHost)
            session.flush()
            session.refresh(myCommandOnHost)
            logger.debug("New command on host are created, its id is : %s" % myCommandOnHost.getId())

            # update our target with the new command_on_host
            myTarget.fk_commands_on_host = myCommandOnHost.getId()
            session.update(myTarget) # not session.save as myTarget was attached to another session
            session.flush()

        self.setDispatched()
        logger.debug('End dispatch...')
        session.update(self)
        session.flush()
        session.close()

    def isDispatched(self):
        if self.id != -1:
            return self.dispatched == 'YES'
        else:
            logging.getLogger().debug("id = -1 then dispatched = false")
            return False

    def setDispatched(self, dispatched = True):
        logging.getLogger().debug("Set dispatched to %s" % (dispatched))

        if dispatched:
            self.dispatched = 'YES'
        else:
            self.dispatched = 'NO'

        if self.id != -1:
            return 0
        else:
            logging.getLogger().debug("id = -1 then dispatched = false")
            return -1

    def hasToWOL(self):
        return self.wake_on_lan == 'enable'

    def hasSomethingToUpload(self):
        result = (len(self.files) != 0)
        logging.getLogger().debug("hasSomethingToUpload(%s): %s" % (self.id, result))
        return result

    def hasSomethingToExecute(self):
        result = (self.start_script == 'enable' and len(self.start_file) != 0)
        logging.getLogger().debug("hasSomethingToExecute(%s): %s" % (self.getId(), result))
        return result

    def hasSomethingToDelete(self):
        result = (self.delete_file_after_execute_successful == 'enable' and len(self.files) != 0)
        logging.getLogger().debug("hasSomethingToDelete(%s): %s" % (self.getId(), result))
        return result

    def isQuickAction(self):
        # TODO: a quick action is not only an action with nothing to upload
        result = (len(self.files) == 0)
        logging.getLogger().debug("isQuickAction(%s): %s" % (self.id, result))
        return result

    def toH(self):
        return {
            'id': self.id,
            'date_created': self.date_created,
            'start_file': self.start_file,
            'parameters': self.parameters,
            'start_script': self.start_script,
            'delete_file_after_execute_successful': self.delete_file_after_execute_successful,
            'files': self.files,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'target': '',
            'username': self.username,
            'webmin_username': self.webmin_username,
            'dispatched': self.dispatched,
            'title': self.title,
            'start_inventory': self.start_inventory,
            'wake_on_lan': self.wake_on_lan,
            'next_connection_delay': self.next_connection_delay,
            'max_connection_attempt': self.max_connection_attempt,
            'repeat': self.repeat,
            'scheduler': self.scheduler,
            'pre_command_hook': self.pre_command_hook,
            'post_command_hook': self.post_command_hook,
            'pre_run_hook': self.pre_run_hook,
            'post_run_hook': self.post_run_hook,
            'on_success_hook': self.on_success_hook,
            'on_failure_hook': self.on_failure_hook,
            'maxbw': self.maxbw
        }

