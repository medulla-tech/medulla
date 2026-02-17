# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Config module for the msc mmc plugin.
Get all possible option like how to connect to the database, ....

"""

# big modules
import logging
import re
import os.path

from mmc.support import mmctools
from mmc.support.config import PluginConfig
from pulse2.database.msc.config import MscDatabaseConfig
from pulse2.xmlrpc import isTwistedEnoughForLoginPass
from pulse2.apis import makeURL


class MscConfig(PluginConfig, MscDatabaseConfig):
    disable = True

    # default folder values
    qactionspath = "/var/lib/pulse2/qactions"
    repopath = "/var/lib/pulse2/packages"
    download_directory_path = "/var/lib/pulse2/downloads"

    # Mirror API stuff
    ma_server = "127.0.0.1"
    ma_port = "9990"
    ma_mountpoint = "/rpc"
    ma_username = ""
    ma_password = ""
    ma_enablessl = True
    ma_verifypeer = False
    ma_cacert = ""
    ma_localcert = ""

    # Scheduler API stuff
    sa_enable = False
    sa_server = "127.0.0.1"
    sa_port = "9990"
    sa_mountpoint = "/scheduler_api"
    sa_username = ""
    sa_password = ""
    sa_enablessl = True
    sa_verifypeer = False
    sa_cacert = ""
    sa_localcert = ""

    # WEB interface stuff
    web_def_awake = 0
    web_def_date_fmt = "%Y-%m-%d %H:%M:%S"
    web_def_inventory = 1
    web_def_reboot = 0
    web_def_mode = "push"
    web_force_mode = True
    web_def_maxbw = "0"
    web_def_delay = "60"
    web_def_attempts = "3"
    web_def_deployment_intervals = ""
    web_def_issue_halt_to = []
    web_show_reboot = True
    web_dlpath = []
    # Default life time of command (in hours)
    web_def_coh_life_time = 1
    # Attempts per day average
    web_def_attempts_per_day = 4
    # Max bandwith to use to download a file
    web_def_dlmaxbw = 0
    # Refresh time
    web_def_refresh_time = 30000
    # Use noVNC instead of TightVNC java applet
    web_def_use_no_vnc = 1

    # local proxy
    web_allow_local_proxy = True
    web_def_local_proxy_mode = "multiple"
    web_def_max_clients_per_proxy = 10
    web_def_proxy_number = 2
    web_def_proxy_selection_mode = "semi_auto"

    # Allow to delete commands and bundles from audit
    web_def_allow_delete = False

    # VNC applet behavior
    web_vnc_show_icon = True
    web_vnc_view_only = True
    web_vnc_network_connectivity = "lan"
    web_vnc_allow_user_control = True
    web_vnc_port = "5900"

    # Probe behavior
    web_probe_order = ""
    web_probe_order_on_demand = "ssh"

    # Display root commands (or not)
    show_root_commands = 1

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
    convergence_reschedule = "42 * * * *"

    schedulers = {}

    check_db_enable = False
    check_db_interval = 300

    # Windows Update command
    wu_command = "/usr/share/medulla-update-manager/medulla-update-manager"

    def __init__(self, name="msc", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="msc_conf")
            MscDatabaseConfig.__init__(self)
            self.initdone = True

        # follow previous behaviour: setup DB-backed values or ini fallback
        if self.backend == "database":
            # shared loader provided by PluginConfig
            self._load_db_settings_from_backend()
        elif self.conffile and self.backend == "ini":
            MscDatabaseConfig.setup(self, self.conffile)

        # call setup to populate remaining options
        self.setup(self.conffile)

    def setup(self, conf_file):
        """
        Read the module configuration
        """
        self.disable = self.getboolean("main", "disable")

        if self.has_option("main", "check_db_enable"):
            self.check_db_enable = self.getboolean("main", "check_db_enable")
        if self.has_option("main", "check_db_interval"):
            self.check_db_interval = self.getint("main", "check_db_interval")

        is_login_and_pass = isTwistedEnoughForLoginPass()

        # folders
        if self.has_option("msc", "qactionspath"):
            self.qactionspath = self.get("msc", "qactionspath")
        if self.has_option("msc", "repopath"):
            self.repopath = self.get("msc", "repopath")

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
            self.ignore_invalid_hostname = self.getboolean(
                "msc", "ignore_invalid_hostname"
            )
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

        # convergence_reschedule
        if self.has_option("msc", "convergence_reschedule"):
            self.convergence_reschedule = self.get("msc", "convergence_reschedule")

        if self.has_option("msc", "wu_command"):
            self.wu_command = self.get("msc", "wu_command")

        for section in self.sections():
            if re.compile("^scheduler_[0-9]+$").match(section):
                if self.default_scheduler == "":
                    self.default_scheduler = section
                username = self.get(section, "username")
                password = self.getpassword(section, "password")
                if not is_login_and_pass:
                    if username != "":
                        if username != "username":
                            logging.getLogger().warning(
                                "your version of twisted is not high enough to use login (%s/username)"
                                % (section)
                            )
                        username = ""
                    if password != "":
                        if password != "password":
                            logging.getLogger().warning(
                                "your version of twisted is not high enough to use password (%s/password)"
                                % (section)
                            )
                        password = ""

                self.schedulers[section] = {
                    "port": self.get(section, "port"),
                    "host": self.get(section, "host"),
                    "username": username,
                    "password": password,
                    "enablessl": self.getboolean(section, "enablessl"),
                    "verifypeer": False,
                }
                if self.schedulers[section]["enablessl"]:
                    if self.has_option(section, "verifypeer"):
                        self.schedulers[section]["verifypeer"] = self.getboolean(
                            section, "verifypeer"
                        )
                    if self.has_option(section, "cacert"):
                        self.schedulers[section]["cacert"] = self.get(
                            section, "cacert"
                        )
                    if self.has_option(section, "localcert"):
                        self.schedulers[section]["localcert"] = self.get(
                            section, "localcert"
                        )
                    if "localcert" in self.schedulers[section] and not os.path.isfile(
                        self.schedulers[section]["localcert"]
                    ):
                        raise Exception(
                            'can\'t read SSL key "%s"'
                            % (self.schedulers[section]["localcert"])
                        )
                    if "cacert" in self.schedulers[section] and not os.path.isfile(
                        self.schedulers[section]["cacert"]
                    ):
                        raise Exception(
                            'can\'t read SSL certificate "%s"'
                            % (self.schedulers[section]["cacert"])
                        )
                    if (
                        "verifypeer" in self.schedulers[section]
                        and self.schedulers[section]["verifypeer"]
                    ):
                        import twisted.internet.ssl

                        if not hasattr(twisted.internet.ssl, "Certificate"):
                            raise Exception(
                                "I need at least Python Twisted 2.5 to handle peer checking"
                            )

        # some default web interface values
        if self.has_option("web", "web_def_awake"):
            self.web_def_awake = self.getint("web", "web_def_awake")
        if self.has_option("web", "web_def_date_fmt"):
            self.web_def_date_fmt = self.get("web", "web_def_date_fmt")
        if self.has_option("web", "web_def_inventory"):
            self.web_def_inventory = self.getint("web", "web_def_inventory")
        if self.has_option("web", "web_def_reboot"):
            self.web_def_reboot = self.getint("web", "web_def_reboot")
        if self.has_option("web", "web_def_mode"):
            self.web_def_mode = self.get("web", "web_def_mode")
        if self.has_option("web", "web_force_mode"):
            self.web_force_mode = self.getboolean("web", "web_force_mode")
        if self.has_option("web", "web_def_maxbw"):
            self.web_def_maxbw = self.get("web", "web_def_maxbw")
        if self.has_option("web", "web_def_delay"):
            self.web_def_delay = self.get("web", "web_def_delay")
        if self.has_option("web", "web_def_attempts"):
            self.web_def_attempts = self.get("web", "web_def_attempts")
        if self.has_option("web", "web_show_reboot"):
            self.web_show_reboot = self.getboolean("web", "web_show_reboot")
        if self.has_option("web", "web_dlpath"):
            self.web_dlpath = []
            dlpaths = self.get("web", "web_dlpath")
            for path in dlpaths.split(","):
                self.web_dlpath.append(path.strip())
            if not os.path.exists(self.download_directory_path):
                logging.getLogger().warn(
                    "Plugin MSC: directory %s does not exist, please create it"
                    % self.download_directory_path
                )

        if self.has_option("web", "web_def_dlmaxbw"):
            self.web_def_dlmaxbw = self.getint("web", "web_def_dlmaxbw")
        if self.has_option("web", "web_def_deployment_intervals"):
            time_intervals = self.get("web", "web_def_deployment_intervals")
            if time_intervals:
                self.web_def_deployment_intervals = time_intervals
            else:
                self.web_def_deployment_intervals = ""
                logging.getLogger().warn(
                    "Plugin MSC: Error parsing option web_def_deployment_intervals !"
                )
        if self.has_option("web", "web_allow_local_proxy"):
            self.web_allow_local_proxy = self.get("web", "web_allow_local_proxy")
        if self.has_option("web", "web_def_local_proxy_mode"):
            self.web_def_local_proxy_mode = self.get(
                "web", "web_def_local_proxy_mode"
            )
        if self.has_option("web", "web_def_max_clients_per_proxy"):
            self.web_def_max_clients_per_proxy = self.getint(
                "web", "web_def_max_clients_per_proxy"
            )
        if self.has_option("web", "web_def_proxy_number"):
            self.web_def_proxy_number = self.getint("web", "web_def_proxy_number")
        if self.has_option("web", "web_def_proxy_selection_mode"):
            self.web_def_proxy_selection_mode = self.get(
                "web", "web_def_proxy_selection_mode"
            )
        if self.has_option("web", "web_def_refresh_time"):
            self.web_def_refresh_time = (
                self.getint("web", "web_def_refresh_time") * 1000
            )
        if self.has_option("web", "web_def_use_no_vnc"):
            self.web_def_use_no_vnc = self.getint("web", "web_def_use_no_vnc")
        if self.has_option("web", "web_def_coh_life_time"):
            self.web_def_coh_life_time = self.getint("web", "web_def_coh_life_time")
        if self.has_option("web", "web_def_attempts_per_day"):
            self.web_def_proxy_selection_mode = self.get(
                "web", "web_def_attempts_per_day"
            )

        # Allow to delete commands and bundles from audit
        if self.has_option("web", "web_def_allow_delete"):
            self.web_def_allow_delete = self.get("web", "web_def_allow_delete")

        # VNC stuff
        if self.has_option("web", "vnc_show_icon"):
            self.web_vnc_show_icon = self.getboolean("web", "vnc_show_icon")
        if self.has_option("web", "vnc_view_only"):
            self.web_vnc_view_only = self.getboolean("web", "vnc_view_only")
        if self.has_option("web", "vnc_network_connectivity"):
            self.web_vnc_network_connectivity = self.get(
                "web", "vnc_network_connectivity"
            )
        if self.has_option("web", "vnc_allow_user_control"):
            self.web_vnc_allow_user_control = self.getboolean(
                "web", "vnc_allow_user_control"
            )
        if self.has_option("web", "vnc_port"):
            self.web_vnc_port = self.get("web", "vnc_port")

        if self.has_option("web", "probe_order"):
            self.web_probe_order = self.get("web", "probe_order")
        if self.has_option("web", "probe_order_on_demand"):
            self.web_probe_order_on_demand = self.get("web", "probe_order_on_demand")
        if self.has_option("web", "show_root_commands"):
            self.show_root_commands = self.get("web", "show_root_commands")

        # API Package
        if self.has_option("package_api", "mserver"):
            self.ma_server = self.get("package_api", "mserver")
        if self.has_option("package_api", "mport"):
            self.ma_port = self.get("package_api", "mport")
        if self.has_option("package_api", "mmountpoint"):
            self.ma_mountpoint = self.get("package_api", "mmountpoint")
        if self.has_option("package_api", "username"):
            if not is_login_and_pass:
                logging.getLogger().warning(
                    "your version of twisted is not high enough to use login (package_api/username)"
                )
                self.ma_username = ""
            else:
                self.ma_username = self.get("package_api", "username")
        if self.has_option("package_api", "password"):
            if not is_login_and_pass:
                logging.getLogger().warning(
                    "your version of twisted is not high enough to use password (package_api/password)"
                )
                self.ma_password = ""
            else:
                self.ma_password = self.get("package_api", "password")
        if self.has_option("package_api", "enablessl"):
            self.ma_enablessl = self.getboolean("package_api", "enablessl")
        if self.ma_enablessl:
            if self.has_option("package_api", "verifypeer"):
                self.ma_verifypeer = self.getboolean("package_api", "verifypeer")
            if (
                self.ma_verifypeer
            ):  # we need twisted.internet.ssl.Certificate to activate certs
                if self.has_option("package_api", "cacert"):
                    self.ma_cacert = self.get("package_api", "cacert")
                if self.has_option("package_api", "localcert"):
                    self.ma_localcert = self.get("package_api", "localcert")
                if not os.path.isfile(self.ma_localcert):
                    raise Exception('can\'t read SSL key "%s"' % (self.ma_localcert))
                if not os.path.isfile(self.ma_cacert):
                    raise Exception(
                        'can\'t read SSL certificate "%s"' % (self.ma_cacert)
                    )
                import twisted.internet.ssl

                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception(
                        "I need at least Python Twisted 2.5 to handle peer checking"
                    )

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
                if not is_login_and_pass:
                    logging.getLogger().warning(
                        "your version of twisted is not high enough to use login (scheduler_api/username)"
                    )
                    self.sa_username = ""
                else:
                    self.sa_username = self.get("scheduler_api", "username")
            if self.has_option("scheduler_api", "password"):
                if not is_login_and_pass:
                    logging.getLogger().warning(
                        "your version of twisted is not high enough to use password (scheduler_api/password)"
                    )
                    self.sa_password = ""
                else:
                    self.sa_password = self.get("scheduler_api", "password")
            if self.has_option("scheduler_api", "enablessl"):
                self.sa_enablessl = self.getboolean("scheduler_api", "enablessl")
            if self.sa_enablessl:
                if self.has_option("scheduler_api", "verifypeer"):
                    self.sa_verifypeer = self.getboolean(
                        "scheduler_api", "verifypeer"
                    )
                if (
                    self.sa_verifypeer
                ):  # we need twisted.internet.ssl.Certificate to activate certs
                    if self.has_option("scheduler_api", "cacert"):
                        self.sa_cacert = self.get("scheduler_api", "cacert")
                    if self.has_option("scheduler_api", "localcert"):
                        self.sa_localcert = self.get("scheduler_api", "localcert")
                    if not os.path.isfile(self.sa_localcert):
                        raise Exception(
                            'can\'t read SSL key "%s"' % (self.sa_localcert)
                        )
                    if not os.path.isfile(self.sa_cacert):
                        raise Exception(
                            'can\'t read SSL certificate "%s"' % (self.sa_cacert)
                        )
                    import twisted.internet.ssl

                    if not hasattr(twisted.internet.ssl, "Certificate"):
                        raise Exception(
                            "I need at least Python Twisted 2.5 to handle peer checking"
                        )

            self.scheduler_url2id = {}

            for id in self.schedulers:
                (url, credentials) = makeURL(self.schedulers[id])
                self.scheduler_url2id[url] = id


# static config ...
COMMAND_STATES_LIST = {
    "upload_in_progress": "",
    "upload_done": "",
    "upload_failed": "",
    "execution_in_progress": "",
    "execution_done": "",
    "execution_failed": "",
    "delete_in_progress": "",
    "delete_done": "",
    "delete_failed": "",
    "not_reachable": "",
    "done": "",
    "pause": "",
    "stop": "",
    "scheduled": "",
}

UPLOADED_EXECUTED_DELETED_LIST = {
    "TODO": "",
    "IGNORED": "",
    "FAILED": "",
    "WORK_IN_PROGRESS": "",
    "DONE": "",
}

COMMANDS_HISTORY_TABLE = "commands_history"
COMMANDS_ON_HOST_TABLE = "commands_on_host"
COMMANDS_TABLE = "commands"
MAX_COMMAND_LAUNCHER_PROCESSUS = 50
CYGWIN_WINDOWS_ROOT_PATH = ""
MOUNT_EXPLORER = "/var/autofs/ssh/"

MAX_LOG_SIZE = 15000

basedir = ""

config = {"path_destination": "/", "explorer": 0}  # FIXME: to put in msc.ini

WINDOWS_SEPARATOR = "\\"
LINUX_SEPARATOR = "/"
S_IFDIR = 0o40000
MIME_UNKNOWN = "Unknown"
MIME_UNKNOWN_ICON = "unknown.png"
MIME_DIR = "Directory"
MIME_DIR_ICON = "folder.png"
DEFAULT_MIME = "application/octet-stream"
