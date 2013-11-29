# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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

import logging

from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.queries import get_available_commands
from pulse2.scheduler.queries import machine_has_commands, verify_target


class DownloadQuery :
    """ Provides the remote queries from a DLP to the msc database """

    def __init__(self):
        self.logger = logging.getLogger()
        self.config = SchedulerConfig()

    def get_available_commands(self, uuid):
        """
        Checks for available packages to deploy.

        @param uuid: UUID computer
        @type uuid: str

        @param mac: MAC address of computer
        @type mac: str

        @return: list of available download URLs
        @rtype: 
        """
        cont = []
        for rec in get_available_commands(self.config.name, uuid):
            (coh_id, 
             target_mirrors,
             start_file,
             files,
             parameters,
             creation_date,
             phases,
             package_id) = rec

            urls = target_mirrors.split('||')


            cont.append({"id": coh_id, 
                         "created": creation_date,
                         "steps" : phases,
                         "params" : parameters,
                         "start_file" : start_file,
                         "non_fatal_steps": self.config.non_fatal_steps,
                         "urls": urls,
                         "files": files,
                         })
        return cont


    def machine_has_commands(self, uuid):
        """
        Checks the downloads for requested machine.

        @param uuid: UUID of computer
        @type uuid: str

        @param macs: MAC addresses of computer
        @type macs: list

        @return: True if at least one download 
        @rtype: bool
        """
        return machine_has_commands(self.config.name, uuid)

    def pull_target_awake(self, hostname, macs):
        """
        Checks requested machine exists in pull targets.

        @param hostname: hostname of computer
        @type hostname: str

        @param macs: MAC addresses of computer
        @type macs: list

        @return: UUID 
        @rtype: str
        """
        pass

    def verify_target(self, id, hostname, mac):
        """
        @param id: commands_on_host id 
        @type id: int

        @param hostname: hostname of computer
        @type hostname: str

        @param mac: MAC address of computer
        @type mac: str

        @return: True if at least one dowload disponible
        @rtype: bool
        """
        return verify_target(id, hostname, mac)
 
