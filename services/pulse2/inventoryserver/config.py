# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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
import pwd
import grp
import string

# MMC
import mmc.support.mmctools
from mmc.support.config import MMCConfigParser
from mmc.plugins.inventory.utilities import getInventoryNoms

class Pulse2OcsserverConfigParser(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives
    """
                
    # default values
    bind = ''
    port = 9999
    ocsmapping = '/etc/mmc/pulse2/OcsNGMap.xml'
    enablessl = False
    verifypeer = False
    cacert = '/etc/mmc/pulse2/inventory-server/keys/cacert.pem'
    localcert = '/etc/mmc/pulse2/inventory-server/keys/privkey.pem'

    pidfile = '/var/run/pulse2-inventory-server.pid'
    umask = 0007
    daemon_user = 0
    daemon_group = 0

    options = {}

    hostname = ['HARDWARE', 'NAME']
    

    def setup(self, config_file):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option('main', 'server'):
            self.bind = self.cp.get("main", 'server')
        if self.cp.has_option('main', 'port'):
            self.port = self.cp.get("main", 'port')
        if self.cp.has_option('main', 'ocsmapping'):
            self.ocsmapping = self.cp.get("main", 'ocsmapping')
        if self.cp.has_option('main', 'pidfile'):
            self.pidfile = self.cp.get("main", 'pidfile')

        if self.cp.has_option('main', 'enablessl'):
            self.enablessl = self.cp.getboolean('main', 'enablessl')
        if self.cp.has_option('main', 'verifypeer'):
            self.verifypeer = self.cp.getboolean('main', 'verifypeer')
        if self.cp.has_option('main', 'certfile'):
            self.cacert = self.cp.get('main', 'certfile')
        if self.cp.has_option('main', 'cacert'):
            self.cacert = self.cp.get('main', 'cacert')
        if self.cp.has_option('main', 'privkey'):
            self.localcert = self.cp.get('main', 'privkey')
        if self.cp.has_option('main', 'localcert'):
            self.localcert = self.cp.get('main', 'localcert')

                            
        if self.cp.has_option('main', 'hostname'):
            path = self.cp.get("main", "hostname").split('|')
            self.hostname = path[0].split('/')
            if len(path) == 2:
                self.hostname.append(path[1].split(':'))
                
            if len(self.hostname) == 3:
                nom = getInventoryNoms()
                if nom.has_key(self.hostname[0]):
                    self.hostname[2][0] = ('nom%s%s' % (self.hostname[0], self.hostname[2][0]), self.hostname[2][0])
        
        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "pid_path"):
                self.pid_path = self.cp.get("daemon", "pid_path")  
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)

        for section in self.cp.sections():
            if re.compile('^option_[0-9]+$').match(section):
                params = []
                for param in self.cp.options('option_01'):
                    if re.compile('^param_[0-9]+$').match(param):
                         attrs, value = self.cp.get(section, param).split('##')
                         params.append({'param':map(lambda x: x.split('::'), attrs.split('||')), 'value':value})
                self.options[section] = {
                    'name':self.cp.get(section, 'NAME'),
                    'param':params
                }

