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
import time

# MSC modules
import mmc.plugins.msc.database
import mmc.plugins.msc.machines
from mmc.plugins.msc import blacklist

# ORM mappings
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost

# Pulse 2 stuff
import pulse2.time_intervals

class Commands(object):
    """ Mapping between msc.commands and SA
    """
    def getId(self):
        return self.id

    def getNextConnectionDelay(self):
        return self.next_connection_delay

    def hasToWOL(self):
        return self.wake_on_lan == 'enable'

    def hasToRunInventory(self):
        return self.start_inventory == 'enable'

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

    def inDeploymentInterval(self):
        # TODO: a quick action is not only an action with nothing to upload
        if not self.deployment_intervals: # no interval given => always perform
            result = True
        else:
            result = pulse2.time_intervals.intimeinterval(self.deployment_intervals, time.strftime("%H:%M:%S"))
        logging.getLogger().debug("inDeploymentInterval(%s): %s" % (self.id, result))
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
            'pre_command_hook': self.pre_command_hook,
            'post_command_hook': self.post_command_hook,
            'pre_run_hook': self.pre_run_hook,
            'post_run_hook': self.post_run_hook,
            'on_success_hook': self.on_success_hook,
            'on_failure_hook': self.on_failure_hook,
            'maxbw': self.maxbw,
            'deployment_intervals': self.deployment_intervals
        }

