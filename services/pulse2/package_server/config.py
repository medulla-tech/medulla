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

    parser = None
    mirrors = []
    package_api_get = []
    package_api_put = []
    proto = 'http'

    mirror_api = {}
    user_package_api = {}

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
                            

        if self.cp.has_option('ssl', 'enablessl'):
            self.enablessl = (self.cp.get('ssl', 'enablessl') == 1)
            if self.enablessl:
                self.proto = 'https'
                self.username = self.cp.get('ssl', 'username')
                self.password = self.cp.get('ssl', 'password')

                self.certfile = self.cp.get('ssl', 'certfile')
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
    print config
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




