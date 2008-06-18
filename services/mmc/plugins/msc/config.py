# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# big modules
import logging
import re

from ConfigParser import NoOptionError
from mmc.support.config import PluginConfig

class MscConfig(PluginConfig):

    # default folder values
    qactionspath = "/tftpboot/revoboot/qactions"
    repopath = "/tftpboot/revoboot/msc"

    # default DB options
    db_driver = "mysql"
    db_host = "127.0.0.1"
    db_port = "3306"
    db_name = "msc"
    db_user = "msc"
    db_passwd = "msc"
    db_debug = "ERROR"
    dbpoolrecycle = 60

    # Mirror API stuff
    ma_server = "127.0.0.1"
    ma_port = "9990"
    ma_mountpoint = "/rpc"
    ma_username = ''
    ma_password = ''
    ma_enablessl = True

    # WEB interface stuff
    web_def_awake = 1
    web_def_inventory = 1
    web_def_mode = "push"
    web_def_maxbw = "0"
    web_def_delay = "60"
    web_def_attempts = "3"

    # IP blacklists settings
    # To filter out everything which is not a valid unicast address
    ignore_non_rfc2780 = True
    # To filter out everything which is not a valid private address
    ignore_non_rfc1918 = False
    # Always filtered IP addresses
    exclude_ipaddr = ""
    # Always accepted IP addresses
    include_ipaddr = ""

    # Hostname blacklists setting
    # To filter non FQDN computer host name
    ignore_non_fqdn = True
    # To filter invalid host name
    ignore_invalid_hostname = False
    # To filter with regexp
    exclude_hostname = ""
    # Whitelist using regexps
    include_hostname = ""

    # MAC address blacklist
    wol_macaddr_blacklist = ""

    schedulers = {
        'scheduler_01': {
            'port': 8000,
            'host': '127.0.0.1',
            'username': 'username',
            'password': 'password',
            'enablessl': True
        }
    }

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)

        # folders
        if self.has_option("msc", "qactionspath"):
            self.qactionspath = self.get("msc", "qactionspath")
        if self.has_option("msc", "repopath"):
            self.repopath = self.get("msc", "repopath")

        # DB connection
        if self.has_option("msc", "db_driver"):
            self.db_driver = self.get("msc", "db_driver")
        if self.has_option("msc", "db_host"):
            self.db_host = self.get("msc", "db_host")
        if self.has_option("msc", "db_port"):
            self.db_port = self.get("msc", "db_port")
        if self.has_option("msc", "db_name"):
            self.db_name = self.get("msc", "db_name")
        if self.has_option("msc", "db_user"):
            self.db_user = self.get("msc", "db_user")
        if self.has_option("msc", "db_passwd"):
            self.db_passwd = self.getpassword("msc", "db_passwd")
        if self.has_option("msc", "db_debug"):
            self.db_debug = self.get("msc", "db_debug")
        if self.has_option("msc", "db_pool_recycle"):
            self.dbpoolrecycle = self.get("msc", "db_pool_recycle")

        # IP address blacklists
        if self.has_option("msc", "ignore_non_rfc2780"):
            self.ignore_non_rfc2780 = self.getboolean("msc", "ignore_non_rfc2780")
        if self.has_option("msc", "ignore_non_rfc1918"):
            self.ignore_non_rfc1918 = self.getboolean("msc", "ignore_non_rfc1918")
        if self.has_option("msc", "exclude_ipaddr"):
            self.exclude_ipaddr = self.get("msc", "exclude_ipaddr")
        if self.has_option("msc", "include_ipaddr"):
            self.include_ipaddr = self.get("msc", "include_ipaddr")

        # Host name blacklists
        if self.has_option("msc", "ignore_non_fqdn"):
            self.ignore_non_fqdn = self.getboolean("msc", "ignore_non_fqdn")
        if self.has_option("msc", "ignore_invalid_hostname"):
            self.ignore_invalid_hostname = self.getboolean("msc", "ignore_invalid_hostname")
        if self.has_option("msc", "exclude_hostname"):
            self.exclude_hostname = self.get("msc", "exclude_hostname")
        if self.has_option("msc", "include_hostname"):
            self.include_hostname = self.get("msc", "include_hostname")

        # MAC address blacklist
        if self.has_option("msc", "wol_macaddr_blacklist"):
            self.wol_macaddr_blacklist = self.get("msc", "wol_macaddr_blacklist")

        # schedulers
        for section in self.sections():
            if re.compile("^scheduler_[0-9]+$").match(section):
                self.schedulers[section] = {
                        'port': self.get(section, "port"),
                        'host': self.get(section, "host"),
                        'username': self.get(section, "username"),
                        'password': self.getpassword(section, "password"),
                        'enablessl': self.getboolean(section, "enablessl")
                    }

        # some default web interface values
        if self.has_option("web", "web_def_awake"):
            self.web_def_awake = self.getint("web", "web_def_awake")
        if self.has_option("web", "web_def_inventory"):
            self.web_def_inventory = self.getint("web", "web_def_inventory")
        if self.has_option("web", "web_def_mode"):
            self.web_def_mode = self.get("web", "web_def_mode")
        if self.has_option("web", "web_def_maxbw"):
            self.web_def_maxbw = self.get("web", "web_def_maxbw")
        if self.has_option("web", "web_def_delay"):
            self.web_def_delay = self.get("web", "web_def_delay")
        if self.has_option("web", "web_def_attempts"):
            self.web_def_attempts = self.get("web", "web_def_attempts")

        # API Package
        if self.has_option("package_api", "mserver"):
            self.ma_server = self.get("package_api", "mserver")
        if self.has_option("package_api", "mport"):
            self.ma_port = self.get("package_api", "mport")
        if self.has_option("package_api", "mmountpoint"):
            self.ma_mountpoint = self.get("package_api", "mmountpoint")
        if self.has_option("package_api", "username"):
            self.ma_username = self.get("package_api", "username")
        if self.has_option("package_api", "password"):
            self.ma_password = self.get("package_api", "password")
        if self.has_option("package_api", "enablessl"):
            self.ma_enablessl = self.getboolean("package_api", "enablessl")


# static config ...
COMMAND_STATES_LIST = {
    "upload_in_progress":'',
    "upload_done":'',
    "upload_failed":'',
    "execution_in_progress":'',
    "execution_done":'',
    "execution_failed":'',
    "delete_in_progress":'',
    "delete_done":'',
    "delete_failed":'',
    "not_reachable":'',
    "done":'',
    "pause":'',
    "stop":'',
    "scheduled":''
}

UPLOADED_EXECUTED_DELETED_LIST = {
    "TODO":'',
    "IGNORED":'',
    "FAILED":'',
    "WORK_IN_PROGRESS":'',
    "DONE":''
}

COMMANDS_HISTORY_TABLE = 'commands_history'
COMMANDS_ON_HOST_TABLE = 'commands_on_host'
COMMANDS_TABLE = 'commands'
MAX_COMMAND_LAUNCHER_PROCESSUS = 50
CYGWIN_WINDOWS_ROOT_PATH = ''
MOUNT_EXPLORER = '/var/autofs/ssh/'
LINUX_SEPARATOR = '/'

MAX_LOG_SIZE = 15000

basedir = ''

config = { 'path_destination':'/', 'explorer':0 } # FIXME: to put in msc.ini

WINDOWS_SEPARATOR = "\\"
LINUX_SEPARATOR = "/"
S_IFDIR = 040000
MIME_UNKNOWN = "Unknown"
MIME_UNKNOWN_ICON = "unknown.png"
MIME_DIR = "Directory"
MIME_DIR_ICON = "folder.png"
DEFAULT_MIME = "application/octet-stream"

