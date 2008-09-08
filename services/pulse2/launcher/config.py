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

# Others Pulse2 Stuff
import pulse2.utils

class LauncherConfig(pulse2.utils.Singleton):
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

    # SSH Proxy stuff
    tcp_sproxy_path = '/usr/sbin/pulse2-tcp-sproxy'

    # daemon stuff
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0

    # scheduler stuff
    first_scheduler = None
    schedulers = {
    }

    # wget stuff
    wget_options = ''
    wget_check_certs = False
    wget_resume = True

    # rsync stuff
    rsync_resume = True

    # launchers (empty for now)
    launchers = {
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
                logging.getLogger().info("launcher %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'int':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getint(section, key))
                logging.getLogger().info("launcher %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'pass':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getpassword(section, key))
                logging.getLogger().info("launcher %s: section %s, option %s set using given value" % (self.name, section, key))
            else:
                logging.getLogger().warn("launcher %s: section %s, option %s not set, using default value" % (self.name, section, key))

    def setup(self, config_file, name = None):
        # Load configuration file
        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        self.name = name

        # Parse "launchers" section
        self.setoption('launchers', 'inventory_command', 'inventory_command')
        self.setoption('launchers', 'launcher_path', 'launcher_path')
        self.setoption('launchers', 'max_command_age', 'max_command_age', 'int')
        self.setoption('launchers', 'max_ping_time', 'max_ping_time', 'int')
        self.setoption('launchers', 'max_probe_time', 'max_probe_time', 'int')
        self.setoption('launchers', 'ping_path', 'ping_path')
        self.setoption('launchers', 'source_path', 'source_path')
        self.setoption('launchers', 'target_path', 'target_path')
        self.setoption('launchers', 'temp_folder_prefix', 'temp_folder_prefix')

        # Parse "wrapper" section
        self.setoption('wrapper', 'max_log_size', 'wrapper_max_log_size', 'int')
        self.setoption('wrapper', 'max_exec_time', 'wrapper_max_exec_time', 'int')
        self.setoption('wrapper', 'path', 'wrapper_path')

        # Parse "ssh" sections
        self.setoption('ssh', 'default_key', 'ssh_defaultkey')
        self.setoption('ssh', 'forward_key', 'ssh_forward_key')
        self.setoption('ssh', 'scp_options', 'scp_options')
        if not type(self.scp_options) == type([]):
            self.scp_options = self.scp_options.split(' ')
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
        self.setoption('wget', 'check_certs', 'wget_check_certs', 'bool')
        self.setoption('wget', 'resume', 'wget_resume', 'bool')

        # Parse "rsync" section
        self.setoption('rsync', 'resume', 'rsync_resume', 'bool')

        # Parse "daemon" section
        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            if self.cp.has_option('daemon', 'pid_path'): # TODO remove in a future version
                logging.getLogger().warning("'pid_path' is obslete, please replace it in your config file by 'pidfile'")
                self.setoption('daemon', 'pid_path', 'pid_path')
            else:
                self.setoption('daemon', 'pidfile', 'pid_path')
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]

        # Parse "wol" section
        self.setoption('wol', 'wol_bcast', 'wol_bcast')
        self.setoption('wol', 'wol_path', 'wol_path')
        self.setoption('wol', 'wol_port', 'wol_port')

        # Parse "tcp_sproxy" section
        self.setoption('tcp_sproxy', 'tcp_sproxy_path', 'tcp_sproxy_path')

        # Parse "scheduler_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^scheduler_[0-9]+$').match(section):
                try:
                    self.schedulers[section] = {
                        'host' : self.getvaluedefaulted(section, 'host', '127.0.0.1'),
                        'port' : self.getvaluedefaulted(section, 'port', "8000"),
                        'username' : self.getvaluedefaulted(section, 'username', "username"),
                        'password' : self.getvaluedefaulted(section, 'password', "password", 'pass'),
                        'enablessl' : self.getvaluedefaulted(section, 'enablessl', True, 'bool'),
                        'awake_time' : self.getvaluedefaulted(section, 'awake_time', 600, 'int'),
                        'defer_results' : self.getvaluedefaulted(section, 'defer_results', False, 'bool')
                    }
                    if self.first_scheduler == None:
                        self.first_scheduler = section
                except ConfigParser.NoOptionError, e:
                    logging.getLogger().warn("launcher %s: section %s do not seems to be correct (%s), please fix the configuration file" % (self.name, section, e))

        # Parse "launcher_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^launcher_[0-9]+$').match(section):
                try:
                    self.launchers[section] = {
                            'bind': self.getvaluedefaulted(section, 'bind', '127.0.0.1'),
                            'enablessl': self.getvaluedefaulted(section, 'enablessl', True, 'bool'),
                            'password': self.getvaluedefaulted(section, 'password', "password", 'pass'),
                            'port': self.cp.get(section, 'port'),
                            'slots': self.getvaluedefaulted(section, 'slots', 300, 'int'),
                            'username': self.getvaluedefaulted(section, 'username', 'username'),
                            'scheduler': self.getvaluedefaulted(section, 'scheduler', self.first_scheduler),
                        }
                    if self.launchers[section]['enablessl']:
                        try:
                            self.launchers[section]['verifypeer'] = self.cp.getboolean(section, 'verifypeer')
                        except ConfigParser.NoOptionError:
                            self.launchers[section]['verifypeer'] = False
                        try:
                            self.launchers[section]['cacert'] = self.cp.get(section, 'cacert')
                        except ConfigParser.NoOptionError:
                            self.launchers[section]['cacert'] = self.cp.get(section, 'certfile')
                        if not os.path.exists(self.launchers[section]['cacert']):
                            raise Exception("Configuration error: path %s does not exists" % self.launchers[section]['cacert'])
                        try:
                            self.launchers[section]['localcert'] = self.cp.get(section, 'localcert')
                        except ConfigParser.NoOptionError:
                            self.launchers[section]['localcert'] = self.cp.get(section, 'privkey')
                        if not os.path.exists(self.launchers[section]['localcert']):
                            raise Exception("Configuration error: path %s does not exists" % self.launchers[section]['localcert'])
                except ConfigParser.NoOptionError, e:
                    logging.getLogger().warn("launcher %s: section %s do not seems to be correct (%s), please fix the configuration file" % (self.name, section, e))

    def getvaluedefaulted(self, section, option, default, type = 'str'):
        if self.cp.has_option(section, option):
            if type == 'str':
                return self.cp.get(section, option)
            elif type == 'bool':
                return self.cp.getboolean(section, option)
            elif type == 'int':
                return self.cp.getint(section, option)
            elif type == 'pass':
                return self.cp.getpassword(section, option)
        else:
            return default

    def check(self):
        """
        Raise an error if the configuration is bad
        """
        paths = [self.launcher_path, self.ping_path, self.wrapper_path, self.wol_path]
        paths.extend(self.ssh_keys.values())
        for path in paths:
            if not os.path.exists(path):
                raise Exception("Configuration error: path %s does not exists" % path)

