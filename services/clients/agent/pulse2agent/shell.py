# -*- test-case-name: pulse2.msc.client.tests.shell -*-
# -*- coding: utf-8; -*-
#
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from subprocess import Popen, PIPE

from .ptypes import Component


class Shell(Component):
    __component_name__ = "shell"

    def call(self, command):
        self.logger.debug(f"Shell: command going to execute: {repr(command)}")
        process = Popen(
            command,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            # close_fds=True,
        )
        out, err = process.communicate()
        returncode = process.returncode

        self.logger.debug(f"Shell: stdout: {repr(out)}")
        if len(err) > 0:
            self.logger.warn(f"Shell: stderr: {repr(err)}")

        self.logger.debug(f"Shell: return code: {repr(returncode)}")

        return returncode
