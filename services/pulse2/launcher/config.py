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

# MMC
import mmc.support.mmctools

class LauncherConfig(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives

    """

    # default values
    name = None
    cp = None
    pid_path = "/var/run/pulse2"
    launcher_path = "/usr/local/sbin/pulse2-launcher"

    wrapper_path = "/usr/local/sbin/pulse2-output-wrapper"
    source_path = "/tftpboot/revoboot/msc"
    target_path = "/tmp"

    inventory_command = "echo Doing inventory"
    temp_folder_prefix = "MDVPLS"

    ssh_defaultkey = 'default'
    ssh_keys = { 'default': '/root/.ssh/id_dsa' }
    ssh_options = [ \
        'StrictHostKeyChecking=no',
        'Batchmode=yes',
        'PasswordAuthentication=no',
        'ServerAliveInterval=10',
        'CheckHostIP=no',
        'ConnectTimeout=10'
    ]
    ssh_forward_key = 'let'
    scp_options = ssh_options

    scheduler_host = "127.0.0.1"
    scheduler_port = "8000"
    scheduler_username = "username"
    scheduler_password = "password"
    scheduler_enablessl = True
    awake_time = 600
    defer_results = False

    launchers = {
        'launcher_01': {
            'port': 8001,
            'bind': '127.0.0.1',
            'username': 'username',
            'password': 'password',
            'enablessl': True,
            'certfile': '/etc/mmc/pulse2/launchers/keys/cacert.pem',
            'privkey': "/etc/mmc/pulse2/launchers/keys/privkey.pem",
            'slots': 300
        }
    }

    def setoption(self, section, key):
        if self.cp.has_option(section, key):
            setattr(self, key, self.cp.get(section, key))
            logging.getLogger().info("launcher %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, key)))
        else:
            logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, key)))

    def setup(self, config_file, name):
        # Load configuration file
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)

        self.name = name
        for key in ['pid_path', 'launcher_path', 'wrapper_path', 'source_path', 'target_path', 'inventory_command', 'temp_folder_prefix']:
            self.setoption('launchers', key)

        if self.cp.has_section('scheduler'):
            for key in ['launcher_path', 'awake_time', 'defer_results']:
                self.setoption('scheduler', key)
            if self.cp.has_option('scheduler', 'host'):
                self.scheduler_host = self.cp.get('scheduler', 'host')
            if self.cp.has_option('scheduler', 'port'):
                self.scheduler_port = self.cp.get('scheduler', 'port')
            if self.cp.has_option('scheduler', 'enablessl'):
                self.scheduler_enablessl = self.cp.getboolean('scheduler', 'enablessl')
            if self.cp.has_option('scheduler', 'username'):
                self.scheduler_username = self.cp.get('scheduler', 'username')
            if self.cp.has_option('scheduler', 'password'):
                self.scheduler_password = self.cp.get('scheduler', 'password')

        for section in self.cp.sections():
            if re.compile('^launcher_[0-9]+$').match(section):
                self.launchers[section] = {
                        'port': self.cp.get(section, 'port'),
                        'bind': self.cp.get(section, 'bind'),
                        'enablessl': self.cp.getboolean(section, 'enablessl'),
                        'slots': self.cp.get(section, 'slots'),
                        'username': self.cp.get(section, 'username'),
                        'password': self.cp.get(section, 'password')
                    }
                if self.launchers[section]['enablessl']:
                    self.launchers[section]['certfile'] = self.cp.get(section, 'certfile')
                    self.launchers[section]['privkey'] = self.cp.get(section, 'privkey')

        if self.cp.has_section('ssh'):
            if self.cp.has_option('ssh', 'default_key'):
                self.ssh_defaultkey = self.cp.get('ssh', 'default_key')
            if self.cp.has_option('ssh', 'ssh_options'):
                self.ssh_options = self.cp.get('ssh', 'ssh_options').split(' ')
            if self.cp.has_option('ssh', 'scp_options'):
                self.scp_options = self.cp.get('ssh', 'scp_options').split(' ')
            for option in self.cp.options('ssh'):
                if re.compile('^sshkey_[0-9A-Za-z]+$').match(option):
                    keyname = re.compile('^sshkey_([0-9A-Za-z]+)$').match(option).group(1)
                    self.ssh_keys[keyname] = self.cp.get('ssh', option)
            if self.cp.has_option('ssh', 'forward_key'):
                self.ssh_forward_key = self.cp.get('ssh', 'forward_key')

        self.awake_time=int(self.awake_time)


