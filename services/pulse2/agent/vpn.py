# -*- test-case-name: pulse2.msc.client.tests.vpn -*-
# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

from subprocess import Popen, PIPE

from ptypes import CC, Component
from connect import probe




class VPNLaunchControl(Component):

    __component_name__ = "vpn_launch_control"

    def start(self):

        if not self.probe():
            self.logger.warn("VPN Server unreacheable")
            return CC.VPN | CC.REFUSED

        command = self.config.vpn.command
        command_args = self.config.vpn.command_args

        cmd = [command, command_args]

        self.logger.info("VPN Server command: %s" % repr(cmd))

        process = Popen(cmd,
                        stdout=PIPE,
                        stderr=PIPE,
                        close_fds=True,
                        )
        out, err = process.communicate()

        self.logger.info("VPN Server stdout: %s" % out)
        self.logger.info("VPN Server stderr: %s" % err)

        self.queue.put((out, err))

        # TODO - do not return directly - return something from CC
        if process.returncode == 0:
            return CC.VPN | CC.DONE
        else:
            return CC.VPN | CC.FAILED


    def probe(self):
        return probe(self.config.vpn.host,
                     self.config.vpn.port,
                     )



