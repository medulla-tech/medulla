# -*- test-case-name: pulse2.msc.client.tests._config -*-
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

""" Declaration of config defaults """

from pulse2agent._config import ConfigReader


class Config(object, metaclass=ConfigReader):
    class main(object):
        serializer = "json"
        check_period = 60

    class server(type):
        host = "pulse2-server"
        port = 8443
        keyfile = None
        crtfile = None
        timeout = 60
        enablessl = True

    class vpn(object):
        enabled = True
        host = "vpnhost"
        port = 443
        command = "/opt/vpnclient/cpncmd"
        command_args = [
            "localhost",
            "/CLIENT",
            "/CMD:AccountConnect",
            "pulse2connection",
        ]
        startup_delay = 5
        common_connection_for_all = False

    class inventory(object):
        windows_reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        windows_software_required = [
            "Mandriva OpenSSH Agent",
        ]
        debian_software_required = [
            "pulse2-agents-installer",
        ]
        debian_server_software_required = ["pulse2-agents-installer-nordp"]
        redhat_software_required = [
            "pulse2-agents-installer",
        ]
        redhat_server_software_required = ["pulse2-agents-installer-nordp"]
        osx_software_required = [
            "org.pulse2-agents-installer",
        ]

    class paths(object):
        package_tmp_dir_win = "C:\\Temp"
        package_tmp_dir_posix = "/tmp"

    class loggers(object):
        keys = "root"

    class handlers(object):
        keys = "hand01"

    class formatters(object):
        keys = "form01"

    class logger_root(object):
        level = "NOTSET"
        handlers = "hand01"

    class handler_hand01(object):
        class_ = "handlers.TimedRotatingFileHandler"
        level = "INFO"
        formatter = "form01"
        args = ("/var/log/pulse2-agent.log", "midnight", 1, 7)

    class formatter_form01(object):
        format = "%(asctime)s %(levelname)s %(message)s"


NAME = "%s"
DISPLAY_NAME = "Pulse2 Agent (%s)"
MODULE_NAME = "service"
CLASS_NAME = "Handler"
DESCRIPTION = "Pulse2 client service for deployment"
AUTO_START = True
