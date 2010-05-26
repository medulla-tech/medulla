# -*- coding: utf-8; -*-
#
# (c) 2010 Nicolas Rueff / Mandriva, http://www.mandriva.com/
#
# $Id: config.py 4167 2009-05-19 10:15:00Z oroussy $
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

"""
Configuration class for the Pulse 2 Imaging Service.
"""

# Misc
import pulse2.utils
import os.path      # for os.path.join()
import pwd          # for getpwnam
import grp          # for getgrpnam
import string       # for atoi

class ImagingConfig(pulse2.utils.Singleton):
    """
        Class which hold an imaging service configuration.
    """

    # [main] section
    host = "0.0.0.0"
    port = 1001
    adminpass = ""

    # [daemon] section
    daemon_user = 0
    daemon_group = 0
    umask = 0077
    pidfile = "/var/run/pulse2-imaging-server.pid"

    # [package-server] section
    pserver_host = "127.0.0.1"
    pserver_port = 9990
    pserver_mount_point = "/imaging_api"
    pserver_enablessl = True
    pserver_username = "username"
    pserver_password = "password"
    pserver_cacert = "/etc/mmc/pulse2/imaging-server/keys/cacert.pem"
    pserver_localcert = "/etc/mmc/pulse2/imaging-server/keys/privkey.pem"
    pserver_verifypeer = False

    # [hooks] section
    hooks_dir = "/usr/local/lib/pulse2/imaging-server/hooks"
    create_client_path = os.path.join(hooks_dir, "create_client")
    client_update_path = os.path.join(hooks_dir, "update_client")
    process_inventory_path = os.path.join(hooks_dir, "process_inventory")
    create_image_path = os.path.join(hooks_dir, "create_image")
    update_image_path = os.path.join(hooks_dir, "update_image")
    log_action_path = os.path.join(hooks_dir, "log_action")
    get_uuid_path = os.path.join(hooks_dir, "get_uuid")
    get_hostname_path = os.path.join(hooks_dir, "get_hostname")
    mtftp_sync_path = os.path.join(hooks_dir, "mtftp_sync")

    def setup(self, config_file):
        """
           Setup config object according to config_file content.
        """

        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_section("main"):
            if self.cp.has_option("main", "host"):
                self.host = self.cp.get("main", "host")
            if self.cp.has_option("main", "port"):
                self.port = self.cp.getint("main", "port")
            if self.cp.has_option("main", "adminpass"):
                self.adminpass = self.cp.get("main", "adminpass")

        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
            if self.cp.has_option("daemon", "pidfile"):
                self.pidfile = self.cp.get("daemon", "pidfile")

        if self.cp.has_section("package-server"):
            if self.cp.has_option("package-server", "host"):
                self.pserver_host = self.cp.get("package-server", "host")
            if self.cp.has_option("package-server", "port"):
                self.pserver_port = self.cp.getint("package-server", "port")
            if self.cp.has_option("package-server", "mount_point"):
                self.pserver_mount_point = self.cp.get("package-server", "mount_point")
            if self.cp.has_option("package-server", "enablessl"):
                self.pserver_enablessl = self.cp.getboolean("package-server", "enablessl")
            if self.cp.has_option("package-server", "password"):
                self.pserver_password = self.cp.get("package-server", "password")
            if self.cp.has_option("package-server", "cacert"):
                self.pserver_cacert = self.cp.get("package-server", "cacert")
            if self.cp.has_option("package-server", "localcert"):
                self.pserver_localcert = self.cp.get("package-server", "localcert")
            if self.cp.has_option("package-server", "verifypeer"):
                self.pserver_verifypeer = self.cp.getboolean("package-server", "verifypeer")

        if self.cp.has_section("hooks"):
            if self.cp.has_option("hooks", "hooks_dir"):
                self.hooks_dir = self.cp.get("hooks", "hooks_dir")
            if self.cp.has_option("hooks", "create_client_path"):
                self.create_client_path = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "create_client_path")
                )
            if self.cp.has_option("hooks", "update_client_path"):
                self.update_client = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "update_client_path")
                )
            if self.cp.has_option("hooks", "process_inventory_path"):
                self.process_inventory = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "process_inventory_path")
                )
            if self.cp.has_option("hooks", "create_image_path"):
                self.create_image = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "create_image_path")
                )
            if self.cp.has_option("hooks", "update_image_path"):
                self.update_image = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "update_image_path")
                )
            if self.cp.has_option("hooks", "log_action_path"):
                self.log_action = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "log_action_path")
                )
            if self.cp.has_option("hooks", "get_uuid_path"):
                self.get_uuid = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "get_uuid_path")
                )
            if self.cp.has_option("hooks", "get_hostname_path"):
                self.get_hostname = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "get_hostname_path")
                )
            if self.cp.has_option("hooks", "mtftp_sync_path"):
                self.mtftp_sync = os.path.join(
                    self.hooks_dir,
                    self.cp.get("hooks", "mtftp_sync_path")
                )
