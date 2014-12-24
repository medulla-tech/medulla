# -*- test-case-name: pulse2.msc.client.tests.shell -*-
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

from ptypes import Component

class Shell(Component):

    __component_name__ = "shell"


    def call(self, command):

        self.logger.debug("Shell: command going to execute: %s" % repr(command))
        process = Popen(command,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=True,
                        #close_fds=True,
                       )
        out, err = process.communicate()
        returncode = process.returncode

        self.logger.debug("Shell: stdout: %s" % repr(out))
        if len(err) > 0:
            self.logger.warn("Shell: stderr: %s" % repr(err))


        self.logger.debug("Shell: return code: %s" % repr(returncode))

        return returncode



