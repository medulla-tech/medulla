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

class LauncherConfig(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives

    """

    # default values
    name = None
    cp = None

    pid_path = "/var/run/pulse2"
    launcher_path = "/usr/sbin/pulse2-launcher"
    wrapper_path = "/usr/sbin/pulse2-output-wrapper"
    source_path = "/var/lib/pulse2/packages"
    target_path = "/tmp"
    ping_path = "/usr/sbin/pulse2-ping"

    # WOL stuff
    wol_path = '/usr/sbin/pulse2-wol'
    wol_port = '40000'
    wol_bcast = '255.255.255.255'

    wrapper_max_log_size = "0"
    wrapper_max_exec_time = 0

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

    # WGET stuff
    wget_options = ''
    wget_check_certs = True

    scheduler_host = "127.0.0.1"
    scheduler_port = "8000"
    scheduler_username = "username"
    scheduler_password = "password"
    scheduler_enablessl = True
    awake_time = 600
    defer_results = False

    daemon_user = 0
    daemon_group = 0
    umask = 0077

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

    def setoption(self, section, key, attrib):
        if self.cp.has_option(section, key):
            setattr(self, attrib, self.cp.get(section, key))
            logging.getLogger().info("launcher %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
        else:
            logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))

    def setup(self, config_file, name = None):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)

        self.name = name

        # Parse "launchers" section
        for key in ['pid_path', 'launcher_path', 'ping_path', 'wrapper_path', 'source_path', 'target_path', 'inventory_command', 'temp_folder_prefix']:
            self.setoption('launchers', key, key)
        self.setoption('launchers', 'wrapper_max_log_size', 'wrapper_max_log_size')
        self.setoption('launchers', 'wrapper_max_exec_time', 'wrapper_max_exec_time')

        # Parse "scheduler" section
        for key in ['awake_time', 'defer_results']:
            self.setoption('scheduler', key, key)
        self.setoption('scheduler', 'host', 'scheduler_host')
        self.setoption('scheduler', 'port', 'scheduler_port')
        self.setoption('scheduler', 'enablessl', 'scheduler_enablessl')
        self.setoption('scheduler', 'username', 'scheduler_username')
        self.setoption('scheduler', 'password', 'scheduler_password')
        self.awake_time=int(self.awake_time)

        # Parse "wol" section
        self.setoption('wol', 'wol_port', 'wol_port')
        self.setoption('wol', 'wol_bcast', 'wol_bcast')
        self.setoption('wol', 'wol_path', 'wol_path')

        # Parse "wget" section
        if self.cp.has_section("wget"):
            if self.cp.has_option("wget", "wget_options"):
                self.wget_options = self.cp.get("wget", "wget_options").split(' ')
            if self.cp.has_option("wget", "check_certs"):
                self.wget_check_certs = self.cp.getboolean("wget", "check_certs")

        # Parse "daemon" section
        self.setoption('daemon', 'pid_path', 'pid_path')
        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)

        # Parse "launcher_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^launcher_[0-9]+$').match(section):
                self.launchers[section] = {
                        'port': self.cp.get(section, 'port'),
                        'bind': self.cp.get(section, 'bind'),
                        'enablessl': self.cp.getboolean(section, 'enablessl'),
                        'slots': self.cp.getint(section, 'slots'),
                        'username': self.cp.get(section, 'username'),
                        'password': self.cp.getpassword(section, 'password')
                    }
                if self.launchers[section]['enablessl']:
                    self.launchers[section]['certfile'] = self.cp.get(section, 'certfile')
                    self.launchers[section]['privkey'] = self.cp.get(section, 'privkey')

        # Parse "ssh" sections
        self.setoption('ssh', 'default_key', 'ssh_defaultkey')
        self.setoption('ssh', 'forward_key', 'ssh_forward_key')
        if self.cp.has_section('ssh'):
            if self.cp.has_option('ssh', 'ssh_options'):
                self.ssh_options = self.cp.get('ssh', 'ssh_options').split(' ')
            if self.cp.has_option('ssh', 'scp_options'):
                self.scp_options = self.cp.get('ssh', 'scp_options').split(' ')
            for option in self.cp.options('ssh'):
                if re.compile('^sshkey_[0-9A-Za-z]+$').match(option):
                    keyname = re.compile('^sshkey_([0-9A-Za-z]+)$').match(option).group(1)
                    self.ssh_keys[keyname] = self.cp.get('ssh', option)



