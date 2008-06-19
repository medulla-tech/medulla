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
import sys
from pulse2.package_server.utilities import Singleton

if sys.platform != "win32":
    import pwd
    import grp
    import string
    # MMC
    from mmc.support.config import MMCConfigParser


class P2PServerCP(Singleton):
    """
    Class to hold configuration directives
    """
    certfile = '/etc/mmc/pulse2/pserver/keys/cacert.pem'
    privkey = '/etc/mmc/pulse2/pserver/keys/privkey.pem'
    

    # default values
    bind = ''
    port = 9990
    enablessl = True
    username = ''
    password = ''

    if sys.platform != "win32":
        umask = 0077
        daemon_group = 0
        pidfile = '/var/run/pulse2-package-server.pid'

    parser = None
    mirrors = []
    package_api_get = []
    package_api_put = []
    proto = 'http'

    mirror_api = {}
    user_package_api = {}
    def setup(self, config_file):
        # Load configuration file
        if sys.platform != "win32":
            self.cp = MMCConfigParser()
        else:
            self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option('main', 'bind'):
            self.bind = self.cp.get("main", 'bind')
        if self.cp.has_option('main', 'port'):
            self.port = self.cp.get("main", 'port')

        if sys.platform != "win32":
            if self.cp.has_section('daemon'):
                if self.cp.has_option('daemon', 'pidfile'):
                    self.pid_path = self.cp.get('daemon', 'pidfile')
                if self.cp.has_option("daemon", "user"):
                    self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
                if self.cp.has_option("daemon", "group"):
                    self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
                if self.cp.has_option("daemon", "umask"):
                    self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
    
        if self.cp.has_option('ssl', 'enablessl'):
            self.enablessl = self.cp.getboolean('ssl', 'enablessl')
        if self.enablessl:
            self.proto = 'https'
            if self.cp.has_option('ssl', 'username'):
                self.username = self.cp.get('ssl', 'username')
                if sys.platform != "win32":
                    self.password = self.cp.getpassword('ssl', 'password')
                else:
                    self.password = self.cp.get('ssl', 'password')
            if self.cp.has_option('ssl', 'certfile'):
                self.certfile = self.cp.get('ssl', 'certfile')
            if self.cp.has_option('ssl', 'privkey'):
                self.privkey = self.cp.get('ssl', 'privkey')

        if self.cp.has_option('mirror_api', 'mount_point'):
            self.mirror_api['mount_point'] = self.cp.get('mirror_api', 'mount_point')

        if self.cp.has_option('user_packageapi_api', 'mount_point'):
            self.user_package_api['mount_point'] = self.cp.get('user_packageapi_api', 'mount_point')

        for section in self.cp.sections():
            if re.compile('^mirror:[0-9]+$').match(section):                
                mount_point = self.cp.get(section, 'mount_point')
                src = self.cp.get(section, 'src')
                mirror = {'mount_point':mount_point, 'src':src}
                if self.cp.has_option(section, 'mirror'):
                    mirror['mirror'] = self.cp.get(section, 'mirror')
                self.mirrors.append(mirror)
            if re.compile('^package_api_get:[0-9]+$').match(section):
                mount_point = self.cp.get(section, 'mount_point')
                src = self.cp.get(section, 'src')
                self.package_api_get.append({'mount_point':mount_point, 'src':src})
            if re.compile('^package_api_put:[0-9]+$').match(section):
                mount_point = self.cp.get(section, 'mount_point')
                src = self.cp.get(section, 'src')
                self.package_api_put.append({'mount_point':mount_point, 'src':src})
                

def config_addons(config):
    if len(config.mirrors) > 0:
#        for mirror_params in config.mirrors:
            map(lambda x: add_access(x, config), config.mirrors)
    if len(config.package_api_get) > 0:
#        for mirror_params in config.package_api_get:
            map(lambda x: add_server(x, config), config.package_api_get)            
    return config

def add_access(mirror_params, config):
    mirror_params['port'] = config.port
    mirror_params['server'] = config.bind
    mirror_params['file_access_path'] = "%s_files" % (mirror_params['mount_point'])
    mirror_params['file_access_uri'] = config.bind
    mirror_params['file_access_port'] = config.port
    return mirror_params

def add_server(mirror_params, config):
    mirror_params['port'] = config.port
    mirror_params['server'] = config.bind
    return mirror_params




