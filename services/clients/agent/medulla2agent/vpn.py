# -*- test-case-name: medulla.msc.client.tests.vpn -*-
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from subprocess import Popen, PIPE

from .ptypes import CC, Component
from .connect import probe


class VPNLaunchControl(Component):
    __component_name__ = "vpn_launch_control"

    def start(self):
        # if not self.probe():
        #    self.logger.warn("VPN Server unreacheable")
        #    return CC.VPN | CC.REFUSED

        command = self.config.vpn.command
        command_args = self.config.vpn.command_args

        cmd = [command] + command_args

        self.logger.info(f"VPN Server command: {repr(cmd)}")

        process = Popen(
            cmd,
            stdout=PIPE,
            stderr=PIPE,
        )
        out, err = process.communicate()

        self.logger.debug(f"VPN Server stdout: {out}")
        self.logger.debug(f"VPN Server stderr: {err}")
        self.logger.debug(f"VPN Server start exitcode: {process.returncode}")

        # self.queue.put((out, err))

        # TODO - do not return directly - return something from CC
        return CC.VPN | CC.DONE if process.returncode == 0 else CC.VPN | CC.FAILED

    def probe(self):
        return probe(
            self.config.vpn.host,
            self.config.vpn.port,
        )
