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

# Pulse 2 stuff
import pulse2.time_intervals

class MscConfig(PluginConfig):

    # default folder values
    qactionspath = "/var/lib/pulse2/qactions"
    repopath = "/var/lib/pulse2/packages"

    # default DB options
    db_driver = "mysql"
    db_host = "127.0.0.1"
    db_port = "3306"
    db_name = "msc"
    db_user = "msc"
    db_passwd = "msc"
    db_debug = "ERROR"
    dbpoolrecycle = 60
    # SSL support
    db_ssl_enable = False
    db_ssl_ca = None
    db_ssl_cert = None
    db_ssl_key = None

    # Mirror API stuff
    ma_server = "127.0.0.1"
    ma_port = "9990"
    ma_mountpoint = "/rpc"
    ma_username = ''
    ma_password = ''
    ma_enablessl = True
    ma_verifypeer = False
    ma_cacert = ""
    ma_localcert = ""

    # Scheduler API stuff
    sa_enable = False
    sa_server = "127.0.0.1"
    sa_port = "9990"
    sa_mountpoint = "/scheduler_api"
    sa_username = ''
    sa_password = ''
    sa_enablessl = True
    sa_verifypeer = False
    sa_cacert = ""
    sa_localcert = ""

    # WEB interface stuff
    web_def_awake = 1
    web_def_inventory = 1
    web_def_mode = "push"
    web_def_maxbw = "0"
    web_def_delay = "60"
    web_def_attempts = "3"
    web_def_deployment_intervals = ""
    web_dlpath = []
    # Max bandwith to use to download a file
    web_def_dlmaxbw = 0

    # VNC applet behavior
    web_vnc_view_only = True
    web_vnc_network_connectivity = "lan"
    web_vnc_allow_user_control = False

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
    ignore_non_fqdn = False
    # To filter invalid host name
    ignore_invalid_hostname = False
    # To filter with regexp
    exclude_hostname = ""
    # Whitelist using regexps
    include_hostname = ""

    # MAC address blacklist
    wol_macaddr_blacklist = ""

    default_scheduler = ""

    schedulers = {
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
        # SSL connection support
        if self.has_option("msc", "db_ssl_enable"):
            self.db_ssl_enable = self.getboolean("msc", "db_ssl_enable")
            if self.db_ssl_enable:
                self.db_ssl_ca = self.get("msc", "db_ssl_ca")
                self.db_ssl_cert = self.get("msc", "db_ssl_cert")
                self.db_ssl_key = self.get("msc", "db_ssl_key")

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
        if self.has_option("msc", "default_scheduler"):
            self.default_scheduler = self.get("msc", "default_scheduler")
        for section in self.sections():
            if re.compile("^scheduler_[0-9]+$").match(section):
                if self.default_scheduler == "":
                    self.default_scheduler = section
                self.schedulers[section] = {
                        'port': self.get(section, "port"),
                        'host': self.get(section, "host"),
                        'username': self.get(section, "username"),
                        'password': self.getpassword(section, "password"),
                        'enablessl': self.getboolean(section, "enablessl"),
                        'verifypeer': False
                    }
                if self.has_option(section, "verifypeer"):
                    self.schedulers[section]["verifypeer"] = self.getboolean(section, "verifypeer")
                if self.schedulers[section]["verifypeer"]:
                    self.schedulers[section]["cacert"] = self.get(section, "cacert")
                    self.schedulers[section]["localcert"] = self.get(section, "localcert")


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
        if self.has_option("web", "web_dlpath"):
            dlpaths = self.get("web", "web_dlpath")
            for path in dlpaths.split(","):
                self.web_dlpath.append(path.strip())
        if self.has_option("web", "web_def_dlmaxbw"):
            self.web_def_dlmaxbw = self.getint("web", "web_def_dlmaxbw")
        if self.has_option("web", "web_def_deployment_intervals"):
            time_intervals = pulse2.time_intervals.normalizeinterval(self.get("web", "web_def_deployment_intervals"))
            if time_intervals:
                self.web_def_deployment_intervals = time_intervals
            else:
                self.web_def_deployment_intervals = ""
                logging.getLogger().warn("Plugin MSC: Error parsing option web_def_deployment_intervals !")

        # VNC stuff
        if self.has_option("web", "vnc_view_only"):
            self.web_vnc_view_only = self.getboolean("web", "vnc_view_only")
        if self.has_option("web", "vnc_network_connectivity"):
            self.web_vnc_network_connectivity = self.get("web", "vnc_network_connectivity")
        if self.has_option("web", "vnc_allow_user_control"):
            self.web_vnc_allow_user_control.getboolean("web", "vnc_allow_user_control")

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
        if self.has_option("package_api", "verifypeer"):
            self.ma_verifypeer = self.getboolean("package_api", "verifypeer")
        if self.has_option("package_api", "cacert"):
            self.ma_cacert = self.get("package_api", "cacert")
        if self.has_option("package_api", "localcert"):
            self.ma_localcert = self.get("package_api", "localcert")

        # Scheduler API
        if self.has_section("scheduler_api"):
            self.sa_enable = True
            if self.has_option("scheduler_api", "host"):
                self.sa_server = self.get("scheduler_api", "host")
            if self.has_option("scheduler_api", "port"):
                self.sa_port = self.get("scheduler_api", "port")
            if self.has_option("scheduler_api", "mountpoint"):
                self.sa_mountpoint = self.get("scheduler_api", "mountpoint")
            if self.has_option("scheduler_api", "username"):
                self.sa_username = self.get("scheduler_api", "username")
            if self.has_option("scheduler_api", "password"):
                self.sa_password = self.get("scheduler_api", "password")
            if self.has_option("scheduler_api", "enablessl"):
                self.sa_enablessl = self.getboolean("scheduler_api", "enablessl")
            if self.has_option("scheduler_api", "verifypeer"):
                self.sa_verifypeer = self.getboolean("scheduler_api", "verifypeer")
            if self.has_option("scheduler_api", "cacert"):
                self.sa_cacert = self.get("scheduler_api", "cacert")
            if self.has_option("scheduler_api", "localcert"):
                self.sa_localcert = self.get("scheduler_api", "localcert")

            self.scheduler_url2id = {}

            for id in self.schedulers:
                url = makeURL(self.schedulers[id])
                self.scheduler_url2id[url] = id


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

def makeURL(config):
    if config.has_key('proto') and not config.has_key('enablessl'):
        uri = "%s://" % config['proto']
    elif config.has_key('protocol') and not config.has_key('enablessl'):
        uri = "%s://" % config['protocol']
    else:
        if config['enablessl']:
            uri = 'https://'
        else:
            uri = 'http://'
    if config.has_key('username') and config['username'] != '':
        uri += '%s:%s@' % (config['username'], config['password'])
    if config.has_key('server') and not config.has_key('host'):
        config['host'] = config['server']
    uri += '%s:%d' % (config['host'], int(config['port']))
    return uri

