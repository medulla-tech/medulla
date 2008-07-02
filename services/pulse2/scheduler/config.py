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

# MMC
import mmc.support.mmctools
from mmc.support.config import MMCConfigParser

class SchedulerConfig(mmc.support.mmctools.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
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

    scheduler_path = '/usr/local/sbin/pulse2-scheduler'
    prober_path = '/usr/local/sbin/pulse2-probe'
    ping_path = '/usr/local/sbin/pulse2-ping'
    wol_path = '/usr/local/sbin/pulse2-wol'

    wol_port = '40000'
    wol_bcast = '255.255.255.255'

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

    def setup(self, config_file):
        # Load configuration file
        cp = MMCConfigParser()
        cp.read(config_file)

        self.name = cp.get("scheduler", "id")

        if cp.has_option("scheduler", "port"):
            self.port = cp.getint("scheduler", "port")
        if cp.has_option("scheduler", "listen"):
            self.host = cp.get("scheduler", "listen")
        if cp.has_option("scheduler", "username"):
            self.username = cp.get("scheduler", "username")
        if cp.has_option("scheduler", "password"):
            self.password = cp.getpassword("scheduler", "password")
        if cp.has_option("scheduler", "enablessl"):
            self.enablessl = cp.getboolean("scheduler", "enablessl")
        if self.enablessl:
            if cp.has_option("scheduler", "privkey"):
                self.privkey = cp.get("scheduler", "privkey")
            if cp.has_option("scheduler", "certfile"):
                self.certfile = cp.get("scheduler", "certfile")

        if cp.has_option("scheduler", "awake_time"):
            self.awake_time = cp.getint("scheduler", "awake_time")
        if cp.has_option("scheduler", "dbencoding"):
            self.dbencoding = cp.get("scheduler", "dbencoding")
        if cp.has_option("scheduler", "mode"):
            self.mode = cp.get("scheduler", "mode")

        if cp.has_option("scheduler", "scheduler_path"):
            self.scheduler_path = cp.get("scheduler", "scheduler_path")
        if cp.has_option("scheduler", "prober_path"):
            self.prober_path = cp.get("scheduler", "prober_path")
        if cp.has_option("scheduler", "ping_path"):
            self.ping_path = cp.get("scheduler", "ping_path")
        if cp.has_option("scheduler", "wol_path"):
            self.wol_path = cp.get("scheduler", "wol_path")

        if cp.has_option("scheduler", "wol_port"):
            self.wol_port = cp.get("scheduler", "wol_port")
        if cp.has_option("scheduler", "wol_bcast"):
            self.wol_bcast = cp.get("scheduler", "wol_bcast")

        if cp.has_option("scheduler", "resolv_order"):
            # TODO: check resolvers availability !!!
            self.resolv_order = cp.get("scheduler", "resolv_order").split(' ')

        if cp.has_section("daemon"):
            if cp.has_option("daemon", "pid_path"):
                self.pid_path = cp.get("daemon", "pid_path")
            if cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(cp.get("daemon", "user"))[2]
            if cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(cp.get("daemon", "group"))[2]
            if cp.has_option("daemon", "umask"):
                self.umask = string.atoi(cp.get("daemon", "umask"), 8)

        for section in cp.sections():
            if re.compile("^launcher_[0-9]+$").match(section):
                self.launchers[section] = {
                        'port': cp.get(section, "port"),
                        'host': cp.get(section, "host"),
                        'username': cp.get(section, "username"),
                        'password': cp.getpassword(section, "password"),
                        'enablessl': cp.getboolean(section, "enablessl")
                    }
