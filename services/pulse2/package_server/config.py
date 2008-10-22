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
import logging

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
    cacert = '/etc/mmc/pulse2/pserver/keys/cacert.pem'
    localcert = '/etc/mmc/pulse2/pserver/keys/privkey.pem'
    

    # default values
    bind = ''
    port = 9990
    enablessl = True
    verifypeer = False
    username = ''
    password = ''

    tmp_input_dir = '/tmp/packages/default'

    if sys.platform != "win32":
        umask = 0077
        daemon_group = 0
        daemon_user = pwd.getpwnam('root')[2]
        umask = string.atoi('0077', 8)
        pidfile = '/var/run/pulse2-package-server.pid'

    package_detect_loop = 60
    package_detect_activate = False

    package_detect_tmp_activate = False

    real_package_deletion = False

    package_mirror_loop = 5
    package_mirror_activate = False
    package_mirror_target = ''
    package_mirror_status_file = '/var/data/mmc/status'
    package_mirror_command = '/usr/bin/rsync'
    package_mirror_command_options = ['-ar', '--delete']
    package_mirror_level0_command_options = ['-d', '--delete']
    package_mirror_command_options_ssh_options = None
    package_global_mirror_activate = True
    package_global_mirror_loop = 3600
    package_global_mirror_command_options = ['-ar', '--delete']

    parser = None
    mirrors = []
    package_api_get = []
    package_api_put = []
    proto = 'http'

    mm_assign_algo = 'default'
    up_assign_algo = 'default'

    mirror_api = {}
    user_package_api = {}
    scheduler_api = {}
    
    def setup(self, config_file):
        # Load configuration file
        if sys.platform != "win32":
            self.cp = MMCConfigParser()
        else:
            self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option("main", "bind"): # TODO remove in a future version
            logging.getLogger().warning("'bind' is obslete, please replace it in your config file by 'host'")
            self.bind = self.cp.get("main", 'bind')
        elif self.cp.has_option('main', 'host'):
            self.bind = self.cp.get("main", 'host')
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
                self.cacert = self.cp.get('ssl', 'certfile')
            if self.cp.has_option('ssl', 'cacert'):
                self.cacert = self.cp.get('ssl', 'cacert')
            if self.cp.has_option('ssl', 'privkey'):
                self.localcert = self.cp.get('ssl', 'privkey')
            if self.cp.has_option('ssl', 'localcert'):
                self.localcert = self.cp.get('ssl', 'localcert')
            if self.cp.has_option('ssl', 'verifypeer'):
                self.verifypeer = self.cp.getboolean('ssl', 'verifypeer')

        if self.cp.has_option('mirror_api', 'mount_point'):
            self.mirror_api['mount_point'] = self.cp.get('mirror_api', 'mount_point')

        if self.cp.has_option('user_packageapi_api', 'mount_point'):
            self.user_package_api['mount_point'] = self.cp.get('user_packageapi_api', 'mount_point')

        if self.cp.has_section('scheduler_api'):
            if self.cp.has_option('scheduler_api', 'mount_point'):
                self.scheduler_api['mount_point'] = self.cp.get('scheduler_api', 'mount_point')
            else:
                self.scheduler_api['mount_point'] = '/scheduler_api'
            if self.cp.has_option('scheduler_api', 'schedulers'):
                self.scheduler_api['schedulers'] = self.cp.get('scheduler_api', 'schedulers')

        if self.cp.has_option('main', 'tmp_input_dir'):
            self.tmp_input_dir = self.cp.get('main', 'tmp_input_dir')

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
                pap_tmp_input_dir = self.tmp_input_dir
                if self.cp.has_option(section, 'tmp_input_dir'):
                    self.package_detect_activate = True
                    self.package_detect_tmp_activate = True
                    pap_tmp_input_dir = self.cp.get(section, 'tmp_input_dir')

                self.package_api_put.append({'mount_point':mount_point, 'src':src, 'tmp_input_dir':pap_tmp_input_dir})
                
        if self.cp.has_option("main", "package_detect_activate"): 
            # WARN this must overide the previously defined activate if it is in the config file
            self.package_detect_activate = self.cp.getboolean("main", "package_detect_activate")
            if self.package_detect_activate and self.cp.has_option("main", "package_detect_loop"):
                self.package_detect_loop = self.cp.getint("main", "package_detect_loop")
                

        if self.cp.has_option("main", "package_mirror_target"):
            self.package_mirror_target = self.cp.get("main", "package_mirror_target").split(' ')
            if (type(self.package_mirror_target) == str and self.package_mirror_target != '') or \
                    (type(self.package_mirror_target) == list and len(self.package_mirror_target) == 1 and self.package_mirror_target[0] != '') or \
                    (type(self.package_mirror_target) == list and len(self.package_mirror_target) != 1):
                self.package_mirror_activate = True

                if self.cp.has_option("main", 'package_mirror_status_file'):
                    self.package_mirror_status_file = self.cp.getint("main", 'package_mirror_status_file')
                if self.cp.has_option("main", 'package_mirror_loop'):
                    self.package_mirror_loop = self.cp.getint("main", 'package_mirror_loop')

                if self.cp.has_option("main", 'package_mirror_command'):
                    self.package_mirror_command = self.cp.get("main", 'package_mirror_command')
                if self.cp.has_option("main", 'package_mirror_command_options'):
                    self.package_mirror_command_options = self.cp.get("main", 'package_mirror_command_options').split(' ')
                if self.cp.has_option("main", "package_mirror_command_options_ssh_options"):
                    self.package_mirror_command_options_ssh_options = self.cp.get("main", 'package_mirror_command_options_ssh_options').split(' ')
                if self.cp.has_option("main", 'package_mirror_level0_command_options'):
                    self.package_mirror_level0_command_options = self.cp.get("main", 'package_mirror_level0_command_options').split(' ')

            if self.cp.has_option("main", "package_global_mirror_activate"):
                self.package_global_mirror_activate = self.cp.getboolean("main", "package_global_mirror_activate")
                if self.cp.has_section("main", "package_global_mirror_loop"):
                    self.package_global_mirror_loop = self.cp.getint("main", "package_global_mirror_loop")
                if self.cp.has_section("main", "package_global_mirror_command_options"):
                    self.package_global_mirror_loop = self.cp.get("main", "package_global_mirror_command_options").split(' ')

        if self.cp.has_option("main", "real_package_deletion"):
            self.real_package_deletion = self.cp.getboolean("main", "real_package_deletion")
        if self.cp.has_option("main", "mm_assign_algo"):
            self.mm_assign_algo = self.cp.get("main", 'mm_assign_algo')
        if self.cp.has_option("main", "up_assign_algo"):
            self.up_assign_algo = self.cp.get("main", 'up_assign_algo')

def config_addons(conf):
    if len(conf.mirrors) > 0:
#        for mirror_params in conf.mirrors:
            map(lambda x: add_access(x, conf), conf.mirrors)
    if len(conf.package_api_get) > 0:
#        for mirror_params in conf.package_api_get:
            map(lambda x: add_server(x, conf), conf.package_api_get)            
    return conf

def add_access(mirror_params, conf):
    mirror_params['port'] = conf.port
    mirror_params['server'] = conf.bind
    mirror_params['file_access_path'] = "%s_files" % (mirror_params['mount_point'])
    mirror_params['file_access_uri'] = conf.bind
    mirror_params['file_access_port'] = conf.port
    return mirror_params

def add_server(mirror_params, conf):
    mirror_params['port'] = conf.port
    mirror_params['server'] = conf.bind
    return mirror_params




