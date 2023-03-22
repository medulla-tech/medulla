# -*- test-case-name: pulse2.msc.client.tests.vpn -*-
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from subprocess import Popen, PIPE

from ptypes import CC, Component
from connect import probe




class VPNLaunchControl(Component):

    __component_name__ = "vpn_launch_control"

    def start(self):

        #if not self.probe():
        #    self.logger.warn("VPN Server unreacheable")
        #    return CC.VPN | CC.REFUSED

        command = self.config.vpn.command
        command_args = self.config.vpn.command_args

        cmd = [command] + command_args

        self.logger.info("VPN Server command: %s" % repr(cmd))

        process = Popen(cmd,
                        stdout=PIPE,
                        stderr=PIPE,
                        )
        out, err = process.communicate()

        self.logger.debug("VPN Server stdout: %s" % out)
        self.logger.debug("VPN Server stderr: %s" % err)
        self.logger.debug("VPN Server start exitcode: %s" % process.returncode)

        #self.queue.put((out, err))

        # TODO - do not return directly - return something from CC
        if process.returncode == 0:
            return CC.VPN | CC.DONE
        else:
            return CC.VPN | CC.FAILED


    def probe(self):
        return probe(self.config.vpn.host,
                     self.config.vpn.port,
                     )
