# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 58 2008-03-28 13:28:58Z nrueff $
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


# Misc
import ConfigParser
import re
import logging

# MMC
import mmc.support.mmctools

class P2PServerCP(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives
    """
                
    # default values
    bind = ''
    port = 9990
    enablessl = False
    username = ''
    password = ''

    pidfile = '/var/run/pulse2-package-server.pid'

    def setup(self, config_file):
        # Load configuration file
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option('main', 'bind'):
            self.bind = self.cp.get("main", 'bind')
        if self.cp.has_option('main', 'port'):
            self.port = self.cp.get("main", 'port')
        if self.cp.has_option('main', 'pidfile'):
            self.pidfile = self.cp.get("main", 'pidfile')
                            
