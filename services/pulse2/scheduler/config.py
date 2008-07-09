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
import pwd
import grp
import string
import logging

# MMC
import mmc.support.mmctools
from mmc.support.config import MMCConfigParser

class SchedulerConfig(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
    cp = None

    port = 8000
    host = "127.0.0.1"
    enablessl = True
    certfile = "/etc/mmc/pulse2/scheduler/keys/cacert.pem"
    privkey = "/etc/mmc/pulse2/scheduler/keys/privkey.pem"
    username = 'username'
    password = 'password'

    awake_time = 600
    dbencoding = 'utf-8'
    mode = 'sync'

    scheduler_path = '/usr/sbin/pulse2-scheduler'
    prober_path = '/usr/sbin/pulse2-probe'
    ping_path = '/usr/sbin/pulse2-ping'

    daemon_user = 0
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077

    resolv_order = ['fqdn', 'netbios', 'hosts', 'ip']
    launchers = {
        'launcher_01': {
            'port': 8001,
            'host': '127.0.0.1',
            'username': 'username',
            'password': 'password',
            'enablessl': True
        }
    }

    def setoption(self, section, key, attrib):
        if self.cp.has_option(section, key):
            setattr(self, attrib, self.cp.get(section, key))
            logging.getLogger().info("scheduler %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
        else:
            logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))

    def setup(self, config_file):
        # Load configuration file
        self.cp = MMCConfigParser()
        self.cp.read(config_file)

        self.name = self.cp.get("scheduler", "id")

        self.setoption("scheduler", "port", "port")
        self.setoption("scheduler", "listen", "host")
        self.setoption("scheduler", "username", "username")
        if self.cp.has_option("scheduler", "password"):
            self.password =self.cp.getpassword("scheduler", "password")
        if self.cp.has_option("scheduler", "enablessl"):
            self.enablessl =self.cp.getboolean("scheduler", "enablessl")
        if self.enablessl:
            self.setoption("scheduler", "privkey", "privkey")
            self.setoption("scheduler", "certfile", "certfile")

        self.setoption("scheduler", "awake_time", "awake_time")
        self.setoption("scheduler", "dbencoding", "dbencoding")
        self.setoption("scheduler", "mode", "mode")
        self.awake_time = int(self.awake_time)

        self.setoption("scheduler", "scheduler_path", "scheduler_path")
        self.setoption("scheduler", "prober_path", "prober_path")
        self.setoption("scheduler", "ping_path", "ping_path")

        self.setoption("scheduler", "resolv_order", "resolv_order")
        if not type(self.resolv_order) == type([]):
            self.resolv_order = [self.resolv_order]

        self.setoption("daemon", "pid_path", "pid_path")
        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(cp.get("daemon", "user"))[2]
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(cp.get("daemon", "group"))[2]
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(cp.get("daemon", "umask"), 8)

        for section in self.cp.sections():
            if re.compile("^launcher_[0-9]+$").match(section):
                self.launchers[section] = {
                        'port':self.cp.get(section, "port"),
                        'host':self.cp.get(section, "host"),
                        'username':self.cp.get(section, "username"),
                        'password':self.cp.getpassword(section, "password"),
                        'enablessl':self.cp.getboolean(section, "enablessl")
                    }
