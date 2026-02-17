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

    def __init__(self, name="imaging", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="imaging_conf")
            ImagingDatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        """
        Read web section of the imaging plugin configuration file
        """
        PluginConfig.readConf(self)
        if not self.disabled:
            # Load database settings depending on the configured backend
            if self.backend == "database":
                # read DB settings from admin DB backend
                self._load_db_settings_from_backend()
            elif self.conffile and self.backend == "ini":
                # read DB settings from INI file
                ImagingDatabaseConfig.setup(self, self.conffile)

            # Explicitly map `web` options to typed attributes (fall back to
            # class defaults when the option is absent).
            if self.has_section("web"):
                if self.has_option("web", "web_def_date_fmt"):
                    self.web_def_date_fmt = self.get("web", "web_def_date_fmt")
                if self.has_option("web", "web_def_default_menu_name"):
                    self.web_def_default_menu_name = self.get(
                        "web", "web_def_default_menu_name"
                    )
                if self.has_option("web", "web_def_default_timeout"):
                    self.web_def_default_timeout = self.get(
                        "web", "web_def_default_timeout"
                    )
                if self.has_option("web", "web_def_default_hidden_menu"):
                    self.web_def_default_hidden_menu = self.getboolean(
                        "web", "web_def_default_hidden_menu"
                    )
                if self.has_option("web", "web_def_default_background_uri"):
                    self.web_def_default_background_uri = self.get(
                        "web", "web_def_default_background_uri"
                    )
                if self.has_option("web", "web_def_default_message"):
                    self.web_def_default_message = self.get(
                        "web", "web_def_default_message"
                    )
                if self.has_option("web", "web_def_kernel_parameters"):
                    self.web_def_kernel_parameters = self.get(
                        "web", "web_def_kernel_parameters"
                    )
                if self.has_option("web", "web_def_image_parameters"):
                    self.web_def_image_parameters = self.get(
                        "web", "web_def_image_parameters"
                    )

                # integer flags
                if self.has_option("web", "web_def_image_hidden"):
                    self.web_def_image_hidden = self.getint(
                        "web", "web_def_image_hidden"
                    )
                if self.has_option("web", "web_def_image_default"):
                    self.web_def_image_default = self.getint(
                        "web", "web_def_image_default"
                    )
                if self.has_option("web", "web_def_service_hidden"):
                    self.web_def_service_hidden = self.getint(
                        "web", "web_def_service_hidden"
                    )
                if self.has_option("web", "web_def_service_default"):
                    self.web_def_service_default = self.getint(
                        "web", "web_def_service_default"
                    )

                if self.has_option("web", "web_def_image_hidden_wol"):
                    self.web_def_image_hidden_wol = self.getint(
                        "web", "web_def_image_hidden_wol"
                    )
                if self.has_option("web", "web_def_image_default_wol"):
                    self.web_def_image_default_wol = self.getint(
                        "web", "web_def_image_default_wol"
                    )
                if self.has_option("web", "web_def_service_hidden_wol"):
                    self.web_def_service_hidden_wol = self.getint(
                        "web", "web_def_service_hidden_wol"
                    )
                if self.has_option("web", "web_def_service_default_wol"):
                    self.web_def_service_default_wol = self.getint(
                        "web", "web_def_service_default_wol"
                    )

                # Preserve any other web options (string fallback)
                for option in self.options("web"):
                    if not hasattr(self, option):
                        setattr(self, option, self.get("web", option))

        # network/resolution order can also be overridden from config
        if self.has_option("network", "resolv_order"):
            rr = self.get("network", "resolv_order")
            if isinstance(rr, list):
                self.resolv_order = rr
            else:
                # accept comma or whitespace separated lists
                if "," in rr:
                    self.resolv_order = [p.strip() for p in rr.split(",") if p.strip()]
                else:
                    self.resolv_order = rr.split()

        if not isinstance(self.resolv_order, list):
            self.resolv_order = self.resolv_order.split(" ")

        if self.has_option("network", "preferred_network"):
            self.preferred_network = self.get("network", "preferred_network")
        else:
            self.preferred_network = ""
        try:
            self.purge_interval = self.get("main", "purge_interval")
        except (NoOptionError, NoSectionError):
            self.purge_interval = "23 0 * * 0"
