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

"""
Config module for the msc mmc plugin.
Get all possible option like how to connect to the database, ....

"""

# big modules
import logging
import re
import os.path

from mmc.support import mmctools
from pulse2.database.msc.config import MscDatabaseConfig
from pulse2.xmlrpc import isTwistedEnoughForLoginPass
from pulse2.apis import makeURL

# Pulse 2 stuff
import pulse2.time_intervals

class MscConfig(MscDatabaseConfig):
    disable = True

    # default folder values
    qactionspath = "/var/lib/pulse2/qactions"
    repopath = "/var/lib/pulse2/packages"
    download_directory_path = "/var/lib/pulse2/downloads"

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
    web_def_date_fmt = "%Y-%m-%d %H:%M:%S"
    web_def_inventory = 1
    web_def_mode = "push"
    web_force_mode = True
    web_def_maxbw = "0"
    web_def_delay = "60"
    web_def_attempts = "3"
    web_def_deployment_intervals = ""
    web_def_issue_halt_to = []
    web_show_reboot = False
    web_dlpath = []
    # Default life time of command (in hours)
    web_def_coh_life_time = 24
    # Attempts per day average
    web_def_attempts_per_day = 4
    # Max bandwith to use to download a file
    web_def_dlmaxbw = 0
    # Refresh time
    web_def_refresh_time = 30000

    # local proxy
    web_allow_local_proxy = True
    web_def_local_proxy_mode = "multiple"
    web_def_max_clients_per_proxy = 10
    web_def_proxy_number = 2
    web_def_proxy_selection_mode = "semi_auto"

    # VNC applet behavior
    web_vnc_show_icon = True
    web_vnc_view_only = True
    web_vnc_network_connectivity = "lan"
    web_vnc_allow_user_control = True
    web_vnc_port = "5900"

    # Probe behavior
    web_probe_order =  ""

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

    check_db_enable = False
    check_db_interval = 300

    def init(self, name, conffile = None):
        self.name = name
        if not conffile: self.conffile = mmctools.getConfigFile(name)
        else: self.conffile = conffile

        MscDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        """
        Read the module configuration
        """
        self.disable = self.cp.getboolean("main", "disable")

        if self.cp.has_option("main", "check_db_enable"):
            self.check_db_enable = self.cp.getboolean("main", "check_db_enable")
        if self.cp.has_option("main", "check_db_interval"):
            self.check_db_interval = self.cp.getint("main", "check_db_interval")

        is_login_and_pass = isTwistedEnoughForLoginPass()

        # folders
        if self.cp.has_option("msc", "qactionspath"):
            self.qactionspath = self.cp.get("msc", "qactionspath")
        if self.cp.has_option("msc", "repopath"):
            self.repopath = self.cp.get("msc", "repopath")

        # IP address blacklists
        if self.cp.has_option("msc", "ignore_non_rfc2780"):
            self.ignore_non_rfc2780 = self.cp.getboolean("msc", "ignore_non_rfc2780")
        if self.cp.has_option("msc", "ignore_non_rfc1918"):
            self.ignore_non_rfc1918 = self.cp.getboolean("msc", "ignore_non_rfc1918")
        if self.cp.has_option("msc", "exclude_ipaddr"):
            self.exclude_ipaddr = self.cp.get("msc", "exclude_ipaddr")
        if self.cp.has_option("msc", "include_ipaddr"):
            self.include_ipaddr = self.cp.get("msc", "include_ipaddr")

        # Host name blacklists
        if self.cp.has_option("msc", "ignore_non_fqdn"):
            self.ignore_non_fqdn = self.cp.getboolean("msc", "ignore_non_fqdn")
        if self.cp.has_option("msc", "ignore_invalid_hostname"):
            self.ignore_invalid_hostname = self.cp.getboolean("msc", "ignore_invalid_hostname")
        if self.cp.has_option("msc", "exclude_hostname"):
            self.exclude_hostname = self.cp.get("msc", "exclude_hostname")
        if self.cp.has_option("msc", "include_hostname"):
            self.include_hostname = self.cp.get("msc", "include_hostname")

        # MAC address blacklist
        if self.cp.has_option("msc", "wol_macaddr_blacklist"):
            self.wol_macaddr_blacklist = self.cp.get("msc", "wol_macaddr_blacklist")

        # schedulers
        if self.cp.has_option("msc", "default_scheduler"):
            self.default_scheduler = self.cp.get("msc", "default_scheduler")

        for section in self.cp.sections():
            if re.compile("^scheduler_[0-9]+$").match(section):
                if self.default_scheduler == "":
                    self.default_scheduler = section
                username = self.cp.get(section, "username")
                password = self.cp.getpassword(section, "password")
                if not is_login_and_pass:
                    if username != '':
                        if username != 'username':
                            logging.getLogger().warning("your version of twisted is not high enough to use login (%s/username)"%(section))
                        username = ''
                    if password != '':
                        if password != 'password':
                            logging.getLogger().warning("your version of twisted is not high enough to use password (%s/password)"%(section))
                        password = ''

                self.schedulers[section] = {
                        'port': self.cp.get(section, "port"),
                        'host': self.cp.get(section, "host"),
                        'username': username,
                        'password': password,
                        'enablessl': self.cp.getboolean(section, "enablessl"),
                        'verifypeer': False
                    }
                if self.schedulers[section]["enablessl"]:
                    if self.cp.has_option(section, "verifypeer"):
                        self.schedulers[section]["verifypeer"] = self.cp.getboolean(section, "verifypeer")
                    if self.cp.has_option(section, "cacert"):
                        self.schedulers[section]["cacert"] = self.cp.get(section, "cacert")
                    if self.cp.has_option(section, "localcert"):
                        self.schedulers[section]["localcert"] = self.cp.get(section, "localcert")
                    if "localcert" in self.schedulers[section] and not os.path.isfile(self.schedulers[section]["localcert"]):
                        raise Exception('can\'t read SSL key "%s"' % (self.schedulers[section]["localcert"]))
                    if "cacert" in self.schedulers[section] and not os.path.isfile(self.schedulers[section]["cacert"]):
                        raise Exception('can\'t read SSL certificate "%s"' % (self.schedulers[section]["cacert"]))
                    if "verifypeer" in self.schedulers[section] and self.schedulers[section]["verifypeer"]:
                        import twisted.internet.ssl
                        if not hasattr(twisted.internet.ssl, "Certificate"):
                            raise Exception('I need at least Python Twisted 2.5 to handle peer checking')

        # some default web interface values
        if self.cp.has_option("web", "web_def_awake"):
            self.web_def_awake = self.cp.getint("web", "web_def_awake")
        if self.cp.has_option("web", "web_def_date_fmt"):
            self.web_def_date_fmt = self.cp.get("web", "web_def_date_fmt")
        if self.cp.has_option("web", "web_def_inventory"):
            self.web_def_inventory = self.cp.getint("web", "web_def_inventory")
        if self.cp.has_option("web", "web_def_mode"):
            self.web_def_mode = self.cp.get("web", "web_def_mode")
        if self.cp.has_option("web", "web_force_mode"):
            self.web_force_mode = self.cp.getboolean("web", "web_force_mode")
        if self.cp.has_option("web", "web_def_maxbw"):
            self.web_def_maxbw = self.cp.get("web", "web_def_maxbw")
        if self.cp.has_option("web", "web_def_delay"):
            self.web_def_delay = self.cp.get("web", "web_def_delay")
        if self.cp.has_option("web", "web_def_attempts"):
            self.web_def_attempts = self.cp.get("web", "web_def_attempts")
        if self.cp.has_option("web", "web_def_issue_halt_to"):
            self.web_def_issue_halt_to = []
            #p_wdiht = ['done', 'failed', 'over_time', 'out_of_interval']
            p_wdiht = ['done']
            for wdiht in self.cp.get("web", "web_def_issue_halt_to").split(','):
                if wdiht in p_wdiht:
                    self.web_def_issue_halt_to.append(wdiht)
                else:
                    logging.getLogger().warn("Plugin MSC: web_def_issue_halt_to cannot be '%s' (possible choices : %s)"%(wdiht, str(p_wdiht)))
        if self.cp.has_option("web", "web_show_reboot"):
            self.web_show_reboot = self.cp.getboolean("web", "web_show_reboot")
        if self.cp.has_option("web", "web_dlpath"):
            self.web_dlpath = []
            dlpaths = self.cp.get("web", "web_dlpath")
            for path in dlpaths.split(","):
                self.web_dlpath.append(path.strip())
            if not os.path.exists(self.download_directory_path):
                logging.getLogger().warn("Plugin MSC: directory %s does not exist, please create it" % self.download_directory_path)

        if self.cp.has_option("web", "web_def_dlmaxbw"):
            self.web_def_dlmaxbw = self.cp.getint("web", "web_def_dlmaxbw")
        if self.cp.has_option("web", "web_def_deployment_intervals"):
            time_intervals = pulse2.time_intervals.normalizeinterval(self.cp.get("web", "web_def_deployment_intervals"))
            if time_intervals:
                self.web_def_deployment_intervals = time_intervals
            else:
                self.web_def_deployment_intervals = ""
                logging.getLogger().warn("Plugin MSC: Error parsing option web_def_deployment_intervals !")
        if self.cp.has_option("web", "web_allow_local_proxy"):
            self.web_allow_local_proxy = self.cp.get("web", "web_allow_local_proxy")
        if self.cp.has_option("web", "web_def_local_proxy_mode"):
            self.web_def_local_proxy_mode = self.cp.get("web", "web_def_local_proxy_mode")
        if self.cp.has_option("web", "web_def_max_clients_per_proxy"):
            self.web_def_max_clients_per_proxy = self.cp.getint("web", "web_def_max_clients_per_proxy")
        if self.cp.has_option("web", "web_def_proxy_number"):
            self.web_def_proxy_number = self.cp.getint("web", "web_def_proxy_number")
        if self.cp.has_option("web", "web_def_proxy_selection_mode"):
            self.web_def_proxy_selection_mode = self.cp.get("web", "web_def_proxy_selection_mode")
        if self.cp.has_option("web", "web_def_refresh_time"):
            self.web_def_refresh_time = self.cp.getint("web", "web_def_refresh_time") * 1000
        if self.cp.has_option("web", "web_def_coh_life_time"):
            self.web_def_proxy_selection_mode = self.cp.get("web", "web_def_coh_life_time")
        if self.cp.has_option("web", "web_def_attempts_per_day"):
            self.web_def_proxy_selection_mode = self.cp.get("web", "web_def_attempts_per_day")
 
        # VNC stuff
        if self.cp.has_option("web", "vnc_show_icon"):
            self.web_vnc_show_icon = self.cp.getboolean("web", "vnc_show_icon")
        if self.cp.has_option("web", "vnc_view_only"):
            self.web_vnc_view_only = self.cp.getboolean("web", "vnc_view_only")
        if self.cp.has_option("web", "vnc_network_connectivity"):
            self.web_vnc_network_connectivity = self.cp.get("web", "vnc_network_connectivity")
        if self.cp.has_option("web", "vnc_allow_user_control"):
            self.web_vnc_allow_user_control = self.cp.getboolean("web", "vnc_allow_user_control")
        if self.cp.has_option("web", "vnc_port"):
            self.web_vnc_port = self.cp.get("web", "vnc_port")

        if self.cp.has_option("web", "probe_order"):
            self.web_probe_order = self.cp.get("web", "probe_order")

        # API Package
        if self.cp.has_option("package_api", "mserver"):
            self.ma_server = self.cp.get("package_api", "mserver")
        if self.cp.has_option("package_api", "mport"):
            self.ma_port = self.cp.get("package_api", "mport")
        if self.cp.has_option("package_api", "mmountpoint"):
            self.ma_mountpoint = self.cp.get("package_api", "mmountpoint")
        if self.cp.has_option("package_api", "username"):
            if not is_login_and_pass:
                logging.getLogger().warning("your version of twisted is not high enough to use login (package_api/username)")
                self.ma_username = ""
            else:
                self.ma_username = self.cp.get("package_api", "username")
        if self.cp.has_option("package_api", "password"):
            if not is_login_and_pass:
                logging.getLogger().warning("your version of twisted is not high enough to use password (package_api/password)")
                self.ma_password = ""
            else:
                self.ma_password = self.cp.get("package_api", "password")
        if self.cp.has_option("package_api", "enablessl"):
            self.ma_enablessl = self.cp.getboolean("package_api", "enablessl")
        if self.ma_enablessl:
            if self.cp.has_option("package_api", "verifypeer"):
                self.ma_verifypeer = self.cp.getboolean("package_api", "verifypeer")
            if self.ma_verifypeer: # we need twisted.internet.ssl.Certificate to activate certs
                if self.cp.has_option("package_api", "cacert"):
                    self.ma_cacert = self.cp.get("package_api", "cacert")
                if self.cp.has_option("package_api", "localcert"):
                    self.ma_localcert = self.cp.get("package_api", "localcert")
                if not os.path.isfile(self.ma_localcert):
                    raise Exception('can\'t read SSL key "%s"' % (self.ma_localcert))
                if not os.path.isfile(self.ma_cacert):
                    raise Exception('can\'t read SSL certificate "%s"' % (self.ma_cacert))
                import twisted.internet.ssl
                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception('I need at least Python Twisted 2.5 to handle peer checking')

        # Scheduler API
        if self.cp.has_section("scheduler_api"):
            self.sa_enable = True
            if self.cp.has_option("scheduler_api", "host"):
                self.sa_server = self.cp.get("scheduler_api", "host")
            if self.cp.has_option("scheduler_api", "port"):
                self.sa_port = self.cp.get("scheduler_api", "port")
            if self.cp.has_option("scheduler_api", "mountpoint"):
                self.sa_mountpoint = self.cp.get("scheduler_api", "mountpoint")
            if self.cp.has_option("scheduler_api", "username"):
                if not is_login_and_pass:
                    logging.getLogger().warning("your version of twisted is not high enough to use login (scheduler_api/username)")
                    self.sa_username = ""
                else:
                    self.sa_username = self.cp.get("scheduler_api", "username")
            if self.cp.has_option("scheduler_api", "password"):
                if not is_login_and_pass:
                    logging.getLogger().warning("your version of twisted is not high enough to use password (scheduler_api/password)")
                    self.sa_password = ""
                else:
                    self.sa_password = self.cp.get("scheduler_api", "password")
            if self.cp.has_option("scheduler_api", "enablessl"):
                self.sa_enablessl = self.cp.getboolean("scheduler_api", "enablessl")
            if self.sa_enablessl:
                if self.cp.has_option("scheduler_api", "verifypeer"):
                    self.sa_verifypeer = self.cp.getboolean("scheduler_api", "verifypeer")
                if self.sa_verifypeer: # we need twisted.internet.ssl.Certificate to activate certs
                    if self.cp.has_option("scheduler_api", "cacert"):
                        self.sa_cacert = self.cp.get("scheduler_api", "cacert")
                    if self.cp.has_option("scheduler_api", "localcert"):
                        self.sa_localcert = self.cp.get("scheduler_api", "localcert")
                    if not os.path.isfile(self.sa_localcert):
                        raise Exception('can\'t read SSL key "%s"' % (self.sa_localcert))
                    if not os.path.isfile(self.sa_cacert):
                        raise Exception('can\'t read SSL certificate "%s"' % (self.sa_cacert))
                    import twisted.internet.ssl
                    if not hasattr(twisted.internet.ssl, "Certificate"):
                        raise Exception('I need at least Python Twisted 2.5 to handle peer checking')

            self.scheduler_url2id = {}

            for id in self.schedulers:
                (url, credentials) = makeURL(self.schedulers[id])
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


