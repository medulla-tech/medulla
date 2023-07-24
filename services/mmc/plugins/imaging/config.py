# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Configuration reader for imaging
"""

from mmc.support.config import PluginConfig
from pulse2.database.imaging.config import ImagingDatabaseConfig
from configparser import NoOptionError, NoSectionError


class ImagingConfig(PluginConfig, ImagingDatabaseConfig):

    """
    Read and hold MMC agent imaging plugin configuration
    """

    web_def_date_fmt = "%Y-%m-%d %H:%M:%S"
    web_def_default_menu_name = "Menu"
    web_def_default_timeout = "60"
    web_def_default_hidden_menu = False
    web_def_default_background_uri = ""
    web_def_default_message = (
        "Warning ! Your PC is being backed up or restored. Do not reboot !"
    )
    web_def_kernel_parameters = "quiet"
    web_def_image_parameters = ""
    web_def_image_hidden = 1
    web_def_image_default = 0
    web_def_service_hidden = 1
    web_def_service_default = 0
    # *_WOL must be lower case because of ini parsing of config file
    web_def_image_hidden_wol = 0
    web_def_image_default_wol = 0
    web_def_service_hidden_wol = 0
    web_def_service_default_wol = 0
    resolv_order = ["ip", "netbios", "dns", "fqdn", "hosts", "first"]
    preferred_network = ""
    purge_interval = "23 0 * * 0"

    def __init__(self, name="imaging", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            ImagingDatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        """
        Read web section of the imaging plugin configuration file
        """
        PluginConfig.readConf(self)
        if not self.disabled:
            ImagingDatabaseConfig.setup(self, self.conffile)
            if self.has_section("web"):
                for option in self.options("web"):
                    # option variable is lowercase
                    setattr(self, option, self.get("web", option))

        setattr(self, "network", "resolv_order")
        if not isinstance(self.resolv_order, type([])):
            self.resolv_order = self.resolv_order.split(" ")

        if self.has_option("network", "preferred_network"):
            self.preferred_network = self.get("network", "preferred_network")
        else:
            self.preferred_network = ""

        try:
            self.purge_interval = self.get("main", "purge_interval")
        except (NoOptionError, NoSectionError):
            self.purge_interval = "23 0 * * 0"
