# -*- test-case-name: pulse2.msc.client.tests.shell -*-
# -*- coding: utf-8; -*-
#
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from subprocess import Popen, PIPE

from .ptypes import Component


class Shell(Component):

    __component_name__ = "shell"

    def call(self, command):

        self.logger.debug("Shell: command going to execute: %s" % repr(command))
        process = Popen(
            command,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            # close_fds=True,
        )
        out, err = process.communicate()
        returncode = process.returncode

        self.logger.debug("Shell: stdout: %s" % repr(out))
        if len(err) > 0:
            self.logger.warn("Shell: stderr: %s" % repr(err))

        self.logger.debug("Shell: return code: %s" % repr(returncode))

        return returncode
