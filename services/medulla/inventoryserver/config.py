# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# Misc
import re
import logging
import pwd
import grp
import string
import os.path

from mmc.site import mmcconfdir
from medulla.database.inventory.config import InventoryDatabaseConfig


class Medulla2OcsserverConfigParser(InventoryDatabaseConfig):
    """
    Singleton Class to hold configuration directives
    """

    # main section
    bind = ""
    port = 9999
    ocsmapping = mmcconfdir + "/medulla/inventory-server/OcsNGMap.xml"
    xmlfixplugindir = mmcconfdir + "/medulla/inventory-server/xml-fix"
    xmldumpdir = "/tmp/"
    xmldumpactive = 0
    enablessl = False
    verifypeer = False
    cacert = mmcconfdir + "/medulla/inventory-server/keys/cacert.pem"
    localcert = mmcconfdir + "/medulla/inventory-server/keys/privkey.pem"
    enable_forward = False
    enable_forward_ocsserver = False
    url_to_forward = "http://localhost/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php"
    inventory_periodicity = 24

    hostname = ["Hardware", "Host"]

    # The default assigned entity is the root entity
    default_entity = "."
    # By default there is no rules file for computer to entity mapping
    entities_rules_file = None

    # daemon section
    pidfile = "/var/run/medulla-inventory-server.pid"
    umask = 0o007
    daemon_user = 0
    daemon_group = 0

    # state section
    orange = 10
    red = 35

    options = {}

    def setup(self, config_file):
        InventoryDatabaseConfig.setup(self, config_file)
        self.rules_matching = []
        if self.dbname is None:
            self.dbname = "inventory"

        if self.cp.has_option("main", "server"):  # TODO remove in a future version
            logging.getLogger().warning(
                "'server' is obslete, please replace it in your config file by 'host'"
            )
            self.bind = self.cp.get("main", "server")
        elif self.cp.has_option("main", "host"):
            self.bind = self.cp.get("main", "host")
        if self.cp.has_option("main", "port"):
            self.port = self.cp.get("main", "port")
        if self.cp.has_option("main", "ocsmapping"):
            self.ocsmapping = self.cp.get("main", "ocsmapping")
        if self.cp.has_option("main", "xmlfixplugindir"):
            self.xmlfixplugindir = self.cp.get("main", "xmlfixplugindir")
        if self.cp.has_option("main", "xmldumpdir"):
            self.xmldumpdir = self.cp.get("main", "xmldumpdir")
        if self.cp.has_option("main", "xmldumpactive"):
            self.xmldumpactive = self.cp.get("main", "xmldumpactive")
        if self.cp.has_option("main", "xmlfixplugindir"):
            self.xmlfixplugindir = self.cp.get("main", "xmlfixplugindir")
        if self.cp.has_option("main", "pidfile"):
            self.pidfile = self.cp.get("main", "pidfile")

        if self.cp.has_option("main", "enablessl"):
            self.enablessl = self.cp.getboolean("main", "enablessl")
        if self.cp.has_option("main", "verifypeer"):
            self.verifypeer = self.cp.getboolean("main", "verifypeer")
        if self.cp.has_option("main", "certfile"):
            self.certfile = self.cp.get("main", "certfile")
        if self.cp.has_option("main", "cacert"):
            self.cacert = self.cp.get("main", "cacert")
        if self.cp.has_option("main", "privkey"):
            self.privkey = self.cp.get("main", "privkey")
        if self.cp.has_option("main", "localcert"):
            self.localcert = self.cp.get("main", "localcert")
        if self.cp.has_option("main", "enable_forward"):
            self.enable_forward = self.cp.getboolean("main", "enable_forward")
        if self.cp.has_option("main", "enable_forward_ocsserver"):
            self.enable_forward_ocsserver = self.cp.getboolean(
                "main", "enable_forward_ocsserver"
            )
        if self.cp.has_option("main", "url_to_forward"):
            self.url_to_forward = self.cp.get("main", "url_to_forward")
        if self.cp.has_option("main", "inventory_periodicity"):
            self.inventory_periodicity = self.cp.get("main", "inventory_periodicity")

        if not os.path.isfile(self.localcert):
            raise Exception('can\'t read SSL key "%s"' % (self.localcert))
            return False
        if not os.path.isfile(self.cacert):
            raise Exception('can\'t read SSL certificate "%s"' % (self.cacert))
            return False
        if (
            self.verifypeer
        ):  # we need twisted.internet.ssl.Certificate to activate certs
            import twisted.internet.ssl

            if not hasattr(twisted.internet.ssl, "Certificate"):
                raise Exception(
                    "I need at least Python Twisted 2.5 to handle peer checking"
                )
                return False

        if self.cp.has_option("main", "default_entity"):
            self.default_entity = self.cp.get("main", "default_entity")
        if self.cp.has_option("main", "entities_rules_file"):
            self.entities_rules_file = self.cp.get("main", "entities_rules_file")
        if self.cp.has_section("RulesMatching"):
            self.rules_matching = self.cp.items("RulesMatching")
        if self.cp.has_option("main", "hostname"):
            path = self.cp.get("main", "hostname").split("|")
            self.hostname = path[0].split("/")
            if len(path) == 2:
                self.hostname.append(path[1].split(":"))

            if len(self.hostname) == 3:
                nom = self.getInventoryNoms()
                if self.hostname[0] in nom:
                    self.hostname[2][0] = (
                        "nom%s%s" % (self.hostname[0], self.hostname[2][0]),
                        self.hostname[2][0],
                    )

        if self.cp.has_section("daemon"):
            if self.cp.has_option("daemon", "pid_path"):
                self.pid_path = self.cp.get("daemon", "pid_path")
            if self.cp.has_option("daemon", "user"):
                self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
            if self.cp.has_option("daemon", "group"):
                self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
            if self.cp.has_option("daemon", "umask"):
                self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)

        if self.cp.has_section("state"):
            if self.cp.has_option("state", "orange"):
                self.orange = self.cp.get("state", "orange")
            if self.cp.has_option("state", "red"):
                self.red = self.cp.get("state", "red")

        for section in self.cp.sections():
            if re.compile("^option_[0-9]+$").match(section):
                params = []
                for param in self.cp.options(section):
                    if re.compile("^param_[0-9]+$").match(param):
                        attrs, value = self.cp.get(section, param).split("##")
                        params.append(
                            {
                                "param": [x.split("::") for x in attrs.split("||")],
                                "value": value,
                            }
                        )
                self.options[section] = {
                    "name": self.cp.get(section, "NAME"),
                    "param": params,
                }
