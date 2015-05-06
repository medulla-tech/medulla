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
from pulse2.scheduler.api.mmc_client import RPCClient
from pulse2.scheduler.queries import get_available_commands
from pulse2.scheduler.queries import pull_target_update
from pulse2.scheduler.queries import machine_has_commands, verify_target

def get_dlp_method(phase):
    methods = {"wol": "pull_completed_wol",
               "upload": "pull_completed_pull",
               "execute": "pull_completed_exec",
               "delete": "pull_completed_delete",
               "inventory": "pull_completed_inventory",
               "reboot": "pull_completed_reboot",
               "halt": "pull_completed_halt",
              }
    return methods[phase]


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
             start_date,
             end_date,
             attempts_left,
             phases,
             todo,
             package_id) = rec

            urls = target_mirrors.split('||')
            if len(files.strip()) > 0:
                files = files.split("\n")
                for index, file in enumerate(files):
                    files[index] = file.split("##")[1]
            else:
                files = []
                package_id = False

            cont.append({"id": coh_id,
                         "created": int(creation_date),
                         "start_date": int(start_date),
                         "end_date": int(end_date),
                         "max_failures": attempts_left,
                         "steps" : phases,
                         "todo": todo,
                         "params" : parameters,
                         "start_file" : start_file,
                         "non_fatal_steps": self.config.non_fatal_steps,
                         "package_uuid": package_id,
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
        d = RPCClient().rpc_execute("msc.pull_target_awake", hostname, macs)
        d.addCallback(self._cb_pull_target_awake, hostname)
        d.addErrback(self._eb_pull_target_awake, hostname)

        return d

    def _cb_pull_target_awake(self, uuid, hostname):
        if uuid :
            pull_target_update(self.config.name, uuid)
            return uuid
        else :
            self.logger.warn("Cannot detect the UUID of %s" % hostname)
            return False

    def _eb_pull_target_awake(self, failure, hostname):
        self.logger.warn("An error occurred when detect the UUID of %s: %s" % (hostname, str(failure)))
        return False

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

