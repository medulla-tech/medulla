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

# MMC
from mmc.support.config import MMCConfigParser

# Others Pulse2 Stuff
import pulse2.utils

class SchedulerConfig(pulse2.utils.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
    cp = None

    # [scheduler] section
    announce_check = dict()
    awake_time = 600
    client_check = None
    dbencoding = 'utf-8'
    enablessl = True
    verifypeer = False
    cacert = "/etc/mmc/pulse2/scheduler/keys/cacert.pem"
    localcert = "/etc/mmc/pulse2/scheduler/keys/privkey.pem"
    host = "127.0.0.1"
    max_slots = 300
    max_command_time = 3600
    max_upload_time = 21600
    max_wol_time = 300
    mode = 'async'
    password = 'password'
    port = 8000
    resolv_order = ['fqdn', 'netbios', 'hosts', 'ip']
    scheduler_path = '/usr/sbin/pulse2-scheduler'
    server_check = None
    username = 'username'

    mg_assign_algo = 'default'

    # [daemon] section
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0

    # [launcher_xxx] section
    launchers = {
    }

    launchers_uri = {}

    def setoption(self, section, key, attrib, type = 'str'):
        if type == 'str':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.get(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'bool':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getboolean(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        if type == 'int':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getint(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'pass':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getpassword(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, section, key))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value" % (self.name, section, key))

    def setup(self, config_file):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)

        # [scheduler] section parsing
        self.name = self.cp.get("scheduler", "id")

        self.setoption("scheduler", "awake_time", "awake_time", 'int')
        self.setoption("scheduler", "max_slots", "max_slots", 'int')
        self.setoption("scheduler", "max_command_time", "max_command_time", 'int')
        self.setoption("scheduler", "max_upload_time", "max_upload_time", 'int')
        self.setoption("scheduler", "max_wol_time", "max_wol_time", 'int')
        self.setoption("scheduler", "dbencoding", "dbencoding")
        self.setoption("scheduler", "enablessl", "enablessl", 'bool')

        if self.cp.has_option("scheduler", "mg_assign_algo"):
            self.mg_assign_algo = self.cp.get("scheduler", 'mg_assign_algo')

        if self.enablessl:
            if self.cp.has_option("scheduler", "privkey"):
                self.localcert = self.cp.get("scheduler", "privkey")
            if self.cp.has_option("scheduler", "localcert"):
                self.localcert = self.cp.get("scheduler", "localcert")
            if self.cp.has_option("scheduler", "certfile"):
                self.cacert = self.cp.get("scheduler", "certfile")
            if self.cp.has_option("scheduler", "cacert"):
                self.cacert = self.cp.get("scheduler", "cacert")
            if self.cp.has_option("scheduler", "verifypeer"):
                self.verifypeer = self.cp.get("scheduler", "verifypeer")
        if self.cp.has_option("scheduler", "listen"): # TODO remove in a future version
            logging.getLogger().warning("'listen' is obslete, please replace it in your config file by 'host'")
            self.setoption("scheduler", "listen", "host")
        else:
            self.setoption("scheduler", "host", "host")
        self.setoption("scheduler", "mode", "mode")
        self.setoption("scheduler", "password", "password", 'pass')
        self.setoption("scheduler", "port", "port")
        self.port = int(self.port)
        self.setoption("scheduler", "resolv_order", "resolv_order")
        if not type(self.resolv_order) == type([]):
            self.resolv_order = self.resolv_order.split(' ')
        self.setoption("scheduler", "scheduler_path", "scheduler_path")
        self.setoption("scheduler", "username", "username")

        if self.cp.has_option("scheduler", "client_check"):
            self.client_check = {}
            for token in self.cp.get("scheduler", "client_check").split(','):
                (key, val) = token.split('=')
                self.client_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'client_check', self.client_check))
        if self.cp.has_option("scheduler", "server_check"):
            self.server_check = {}
            for token in self.cp.get("scheduler", "server_check").split(','):
                (key, val) = token.split('=')
                self.server_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))
        if self.cp.has_option("scheduler", "announce_check"):
            self.announce_check = {}
            for token in self.cp.get("scheduler", "announce_check").split(','):
                (key, val) = token.split('=')
                self.announce_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))

        # [daemon] section parsing
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

        # [launcher_xxx] section parsing
        for section in self.cp.sections():
            if re.compile("^launcher_[0-9]+$").match(section):
                self.launchers[section] = {
                        'enablessl':self.cp.getboolean(section, "enablessl"),
                        'host':self.cp.get(section, "host"),
                        'username':self.cp.get(section, "username"),
                        'password':self.cp.getpassword(section, "password"),
                        'port':self.cp.get(section, "port")
                    }
                if self.launchers[section]["enablessl"]:
                    uri = "https://"
                else:
                    uri = 'http://'
                if self.launchers[section]['username'] != '':
                    uri += '%s:%s@' % (self.launchers[section]['username'], self.launchers[section]['password'])
                uri += '%s:%d' % (self.launchers[section]['host'], int(self.launchers[section]['port']))
                self.launchers_uri.update({section: uri})
