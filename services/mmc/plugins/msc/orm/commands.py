# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id: database.py 426 2008-01-11 13:45:00Z nrueff $
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
        return self.id_command

    def getNextConnectionDelay(self):
        return self.next_connection_delay

    def dispatch(self, ctx):
        """ Inject as many lines in CommandsOnHost as required (i.e. one per target)
        """

        # gather usefull stuff ...
        database = mmc.plugins.msc.database.MscDatabase()
        machines = mmc.plugins.msc.machines.Machines()
        session = sqlalchemy.create_session()
        logger = logging.getLogger()

        if self.isDispatched():
            return None

        logger.debug('Start dispatch...')
        # iterate over available target
        for myTarget in database.getTargets(self.id_command):
            host = machines.getMachine(ctx, {'uuid': myTarget.target_uuid})
            if host == None:
                logging.getLogger().warning("Cannot find hostname '%s'" % (myTarget.target_name))
                continue

            # Create (and save) a new commands_on_host row
            logging.getLogger().debug("Create new command on host : %s" % (host.hostname))
            myCommandOnHost = CommandsOnHost()
            myCommandOnHost.id_command = self.id_command
            myCommandOnHost.host = host.hostname[0] # maybe uuid ...
            myCommandOnHost.start_date = self.start_date or "0000-00-00 00:00:00"
            myCommandOnHost.end_date = self.end_date or "0000-00-00 00:00:00"
            myCommandOnHost.next_launch_date = self.start_date or "0000-00-00 00:00:00"
            myCommandOnHost.current_state = 'scheduled'
            myCommandOnHost.uploaded = 'TODO'
            myCommandOnHost.executed = 'TODO'
            myCommandOnHost.deleted = 'TODO'
            myCommandOnHost.current_pid = -1
            myCommandOnHost.number_attempt_connection_remains = self.max_connection_attempt
            myCommandOnHost.next_attempt_date_time = 0
            session.save(myCommandOnHost)
            session.flush()
            session.refresh(myCommandOnHost)
            logging.getLogger().debug("New command on host are created, its id is : %s" % myCommandOnHost.getId())

            # update our target with the new command_on_host
            myTarget.id_command_on_host = myCommandOnHost.getId()
            session.update(myTarget) # not session.save as myTarget was attached to another session
            session.flush()

        self.setDispatched()
        logging.getLogger().debug('End dispatch...')
        session.update(self)
        session.flush()
        session.close()

    def isDispatched(self):
        if self.id_command != -1:
            return self.dispatched == 'YES'
        else:
            logging.getLogger().debug("id_command = -1 then dispatched = false")
            return False

    def setDispatched(self, dispatched = True):
        logging.getLogger().debug("Set dispatched to %s" % (dispatched))

        if dispatched:
            self.dispatched = 'YES'
        else:
            self.dispatched = 'NO'

        if self.id_command != -1:
            return 0
        else:
            logging.getLogger().debug("id_command = -1 then dispatched = false")
            return -1

    def hasToWOL(self):
        return self.wake_on_lan == 'enable'

    def hasSomethingToUpload(self):
        result = (len(self.files) != 0)
        logging.getLogger().debug("hasSomethingToUpload(%s): %s" % (self.id_command, result))
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
        logging.getLogger().debug("isQuickAction(%s): %s" % (self.id_command, result))
        return result

    def toH(self):
        return {
            'id_command': self.id_command,
            'date_created': self.date_created,
            'start_file': self.start_file,
            'parameters': self.parameters,
            'path_destination': self.path_destination,
            'path_source': self.path_source,
            'create_directory': self.create_directory,
            'start_script': self.start_script,
            'delete_file_after_execute_successful': self.delete_file_after_execute_successful,
            'files': self.files,
            'start_date': self.start_date,
            'end_date': self.end_date,
#            'target': map(lambda t: t.toH(), MscDatabase().getTargets(self.id_command)),
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
            'on_failure_hook': self.on_failure_hook
        }

