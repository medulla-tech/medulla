# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MMC plugin for controlling systemd
"""

import logging
import dbus.mainloop.glib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

try:
    from mmc.plugins.services.manager import ServiceManager
except ImportError:
    pass
from mmc.plugins.services.config import ServicesConfig

logger = logging.getLogger()

VERSION = "5.4.6"
APIVERSION = "0:1:0"
REVISION = ""


def getVersion():
    return VERSION


def getApiVersion():
    return APIVERSION


def getRevision():
    return REVISION


def activate():
    config = ServicesConfig("services")
    if config.disabled:
        logger.warning("Plugin services: disabled by configuration.")
        return False
    logger.debug("Loading systemd units")
    try:
        ServiceManager().list()
    except NameError:
        logger.error("Failed to list systemd units. Is python-systemd-dbus installed ?")
        return False
    try:
        from mmc.plugins.dashboard.manager import DashboardManager
        from mmc.plugins.services.panel import ServicesPanel, SystemPanel

        DM = DashboardManager()
        DM.register_panel(ServicesPanel("services"))
        DM.register_panel(SystemPanel("system"))
    except ImportError:
        pass

    return True


# XML-RPC methods
def start(service):
    return ServiceManager().start(service)


def stop(service):
    return ServiceManager().stop(service)


def restart(service):
    return ServiceManager().restart(service)


def reload(service):
    return ServiceManager().reload(service)


def status(service):
    return ServiceManager().status(service)


def list():
    return ServiceManager().list()


def list_plugins_services():
    return ServiceManager().list_plugins_services()


def has_inactive_plugins_services():
    return ServiceManager().has_inactive_plugins_services()


def list_others_services(filter=None):
    return ServiceManager().list_others_services(filter)


def log(service="", filter=""):
    return ServiceManager().log(service, filter)


def server_power_off():
    return ServiceManager().m.power_off()


def server_reboot():
    return ServiceManager().m.reboot()
