# -*- coding: utf-8; -*-
#
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id: pulse2-launcher 22 2008-01-14 14:52:22Z nrueff $
#
# This file is part of Pulse2.
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Misc
import ConfigParser

# MMC
import mmc.support.mmctools

class SchedulerConfig(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
    port = 8000
    host = "127.0.0.1"
    login = ""
    password = ""
    start_commands_modulo = 600
    prober_path = '/usr/sbin/pulse2-probe'

    def setup(self, config_file):
        # Load configuration file
        cp = ConfigParser.ConfigParser()
        cp.read(config_file)

        self.name = cp.get("scheduler", "id")
        if cp.has_option("scheduler", "port"):
            self.port = cp.getint("scheduler", "port")

        if cp.has_option("scheduler", "listen"):
            self.host = cp.get("scheduler", "listen")

        if cp.has_option("scheduler", "login"):
            self.login = cp.get("scheduler", "login")

        if cp.has_option("scheduler", "password"):
            self.password = cp.get("scheduler", "password")

        if cp.has_option("scheduler", "start_commands_modulo"):
            self.start_commands_modulo = cp.getint("scheduler", "start_commands_modulo")

        if cp.has_option("scheduler", "prober_path"):
            self.prober_path = cp.get("scheduler", "prober_path")
