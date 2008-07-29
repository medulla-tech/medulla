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
import re           # fo re.compil
import pwd          # for getpwnam
import grp          # for getgrpnam
import string       # for atoi
import logging      # logging stuff
import os.path

# MMC
from mmc.support.config import MMCConfigParser

# our stuff
import pulse2.scheduler.utils

class LauncherConfig(pulse2.scheduler.utils.Singleton):
    """
    Singleton Class to hold configuration directives
    """

    # default values
    name = None
    cp = None

    inventory_command = "echo Doing inventory"
    launcher_path = "/usr/sbin/pulse2-launcher"
    max_command_age = 86400
    max_ping_time = 2
    max_probe_time = 5
    ping_path = "/usr/sbin/pulse2-ping"
    source_path = "/var/lib/pulse2/packages"
    target_path = "/tmp"
    temp_folder_prefix = "MDVPLS"

    # wrapper stuff
    wrapper_max_exec_time = 21600
    wrapper_max_log_size = 512000
    wrapper_path = "/usr/sbin/pulse2-output-wrapper"

    # ssh stuff
    ssh_defaultkey = 'default'
    ssh_forward_key = 'let'
    ssh_options = [ \
        'StrictHostKeyChecking=no',
        'Batchmode=yes',
        'PasswordAuthentication=no',
        'ServerAliveInterval=10',
        'CheckHostIP=no',
        'ConnectTimeout=10'
    ]
    scp_options = ssh_options
    ssh_keys = {
        'default': '/root/.ssh/id_dsa'
    }

    # WOL stuff
    wol_path = '/usr/sbin/pulse2-wol'
    wol_port = '40000'
    wol_bcast = '255.255.255.255'

    # daemon stuff
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0

    # scheduler stuff
    scheduler_host = "127.0.0.1"
    scheduler_port = "8000"
    scheduler_username = "username"
    scheduler_password = "password"
    scheduler_enablessl = True
    awake_time = 600
    defer_results = False

    # wget stuff
    wget_options = ''
    wget_check_certs = True
    wget_continue = True

    # rsync stuff
    rsync_partial = True

    # launchers
    launchers = {
        'launcher_01': {
            'port': 8001,
            'bind': '127.0.0.1',
            'username': 'username',
            'password': 'password',
            'enablessl': True,
            'verifypeer': False,            
            'cacert': '/etc/mmc/pulse2/launchers/keys/cacert.pem',
            'localcert': "/etc/mmc/pulse2/launchers/keys/privkey.pem",
            'slots': 300
        }
    }

    def setoption(self, section, key, attrib, type = 'str'):
        if type == 'str':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.get(section, key))
                logging.getLogger().info("launcher %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'bool':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getboolean(section, key))
                logging.getLogger().info("launcher %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))

    def setup(self, config_file, name = None):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)

        self.name = name

        # Parse "launchers" section
        self.setoption('launchers', 'inventory_command', 'inventory_command')
        self.setoption('launchers', 'launcher_path', 'launcher_path')
        self.setoption('launchers', 'max_command_age', 'max_command_age')
        self.max_command_age = int(self.max_command_age)
        self.setoption('launchers', 'max_ping_time', 'max_ping_time')
        self.max_ping_time = int(self.max_ping_time)
        self.setoption('launchers', 'max_probe_time', 'max_probe_time')
        self.max_probe_time = int(self.max_probe_time)
        self.setoption('launchers', 'ping_path', 'ping_path')
        self.setoption('launchers', 'source_path', 'source_path')
        self.setoption('launchers', 'target_path', 'target_path')
        self.setoption('launchers', 'temp_folder_prefix', 'temp_folder_prefix')

        # Parse "wrapper" section
        self.setoption('wrapper', 'max_log_size', 'wrapper_max_log_size')
        self.wrapper_max_log_size = int(self.wrapper_max_log_size)
        self.setoption('wrapper', 'max_exec_time', 'wrapper_max_exec_time')
        self.wrapper_max_exec_time = int(self.wrapper_max_exec_time)
        self.setoption('wrapper', 'path', 'wrapper_path')

        # Parse "ssh" sections
        self.setoption('ssh', 'default_key', 'ssh_defaultkey')
        self.setoption('ssh', 'forward_key', 'ssh_forward_key')
        self.setoption('ssh', 'scp_options', 'scp_options')
        if not type(self.scp_options) == type([]):
            self.scp_options = [self.scp_options]
        self.setoption('ssh', 'ssh_options', 'ssh_options')
        if not type(self.ssh_options) == type([]):
            self.ssh_options = self.ssh_options.split(' ')
        if self.cp.has_section('ssh'):
            for option in self.cp.options('ssh'):
                if re.compile('^sshkey_[0-9A-Za-z]+$').match(option):
                    keyname = re.compile('^sshkey_([0-9A-Za-z]+)$').match(option).group(1)
                    self.ssh_keys[keyname] = self.cp.get('ssh', option)

        # Parse "wget" section
        if self.cp.has_section("wget"):
            if self.cp.has_option("wget", "wget_options"):
                self.wget_options = self.cp.get("wget", "wget_options").split(' ')
            if self.cp.has_option("wget", "check_certs"):
                self.wget_check_certs = self.cp.getboolean("wget", "check_certs")
            if self.cp.has_option("wget", "continue"):
                self.wget_continue = self.cp.getboolean("wget", "continue")

        # Parse "rsync" section
        if self.cp.has_section("rsync"):
            if self.cp.has_option("rsync", "partial"):
                self.rsync_partial = self.cp.getboolean("rsync", "partial")

        # Parse "daemon" section
        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            self.setoption('daemon', 'pid_path', 'pid_path')
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]

        # Parse "wol" section
        self.setoption('wol', 'wol_bcast', 'wol_bcast')
        self.setoption('wol', 'wol_path', 'wol_path')
        self.setoption('wol', 'wol_port', 'wol_port')

        # Parse "scheduler" section
        self.setoption('scheduler', 'awake_time', 'awake_time')
        self.awake_time=int(self.awake_time)
        self.setoption('scheduler', 'defer_results', 'defer_results', 'bool')
        self.setoption('scheduler', 'enablessl', 'scheduler_enablessl', 'bool')
        self.setoption('scheduler', 'host', 'scheduler_host')
        self.setoption('scheduler', 'password', 'scheduler_password')
        self.setoption('scheduler', 'port', 'scheduler_port')
        self.setoption('scheduler', 'username', 'scheduler_username')

        # Parse "launcher_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^launcher_[0-9]+$').match(section):
                self.launchers[section] = {
                        'bind': self.cp.get(section, 'bind'),
                        'enablessl': self.cp.getboolean(section, 'enablessl'),
                        'verifypeer': self.cp.getboolean(section, 'verifypeer'),
                        'password': self.cp.getpassword(section, 'password'),
                        'port': self.cp.get(section, 'port'),
                        'slots': self.cp.getint(section, 'slots'),
                        'username': self.cp.get(section, 'username')
                    }
                if self.launchers[section]['enablessl']:
                    try:
                        self.launchers[section]['cacert'] = self.cp.get(section, 'cacert')
                    except ConfigParser.NoOptionError:
                        self.launchers[section]['cacert'] = self.cp.get(section, 'certfile')
                    try:
                        self.launchers[section]['localcert'] = self.cp.get(section, 'localcert')
                    except ConfigParser.NoOptionError:
                        self.launchers[section]['localcert'] = self.cp.get(section, 'privkey')

    def check(self):
        """
        Raise an error if the configuration is bad
        """
        paths = [self.launcher_path, self.ping_path, self.wrapper_path, self.wol_path]
        paths.extend(self.ssh_keys.values())
        for path in paths:
            if not os.path.exists(path):
                raise Exception("Configuration error: path %s does not exists" % path)

