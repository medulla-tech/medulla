# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Configuration class for MMC agent inventory plugin
"""

from mmc.database.config import DatabaseConfig


class InventoryDatabaseConfigSkel(DatabaseConfig):
    dbname = "inventory"
    list = {}
    double = {}
    halfstatic = {}
    extended = {}

    def getInventoryParts(self):
        """
        @return: Return all available inventory parts
        @rtype: list
        """
        return [
            "Bios",
            "BootDisk",
            "BootGeneral",
            "BootMem",
            "BootPart",
            "BootPCI",
            "Controller",
            "Custom",
            "Drive",
            "Hardware",
            "Input",
            "Memory",
            "Modem",
            "Monitor",
            "Network",
            "Port",
            "Printer",
            "Slot",
            "Software",
            "Sound",
            "Storage",
            "VideoCard",
            "Registry",
            "Entity",
            "InventoryDebugLog",
        ]

    def getInventoryNoms(self, table=None):
        """
        @return: Return all available nomenclatures tables
        @rtype: dict
        """
        noms = {"Registry": ["Path"]}

        if table is None:
            return noms
        if table in noms:
            return noms[table]
        return None


class InventoryDatabaseConfig(InventoryDatabaseConfigSkel):
    list = {
        "Software/ProductName": ["string"],
        "Software/Company": ["string"],
        "Hardware/ProcessorType": ["string"],
        "Hardware/OperatingSystem": ["string"],
        "Entity/Label": ["string"],
        "Drive/TotalSpace": ["int"],
    }
    double = {
        "Software/ProductName:ProductVersion": [
            ["Software/ProductName", "string"],
            ["Software/ProductVersion", "string"],
        ],
        "Software/Company:ProductName": [
            ["Software/Company", "string"],
            ["Software/ProductName", "string"],
        ],
    }
    triple = {
        "Software/Company:ProductName:ProductVersion": [
            ["Software/Company", "string"],
            ["Software/ProductName", "string"],
            ["Software/ProductVersion", "string"],
        ]
    }
    doubledetail = {"Software/ProductVersion": "string"}
    halfstatic = {
        "Registry/Value/display name": ["string", "Path", "DisplayName"],
        "Registry/Value/nomRegistryPath codePDV": ["string", "Path", "codePDV"],
        "Registry/Value/nomRegistryPath hardwareSerial": [
            "string",
            "Path",
            "hardwareSerial",
        ],
    }
    expert_mode = {}
    graph = {}
    display = [["cn", "Computer Name"], ["displayName", "Description"]]
    content = {}

    def setup(self, config_file):
        # read the database configuration
        DatabaseConfig.setup(self, config_file)

        # read the other inventory default parameters
        if self.cp.has_section("graph"):
            for i in self.getInventoryParts():
                if self.cp.has_option("graph", i):
                    self.graph[i] = self.cp.get("graph", i).split("|")
                else:
                    self.graph[i] = []
                if self.cp.has_option("expert_mode", i):
                    self.expert_mode[i] = self.cp.get("expert_mode", i).split("|")
                else:
                    self.expert_mode[i] = []

        if self.cp.has_section("computers"):
            if self.cp.has_option("computers", "display"):
                self.display = [
                    x.split("::")
                    for x in self.cp.get("computers", "display").split("||")
                ]

            # Registry::Path::path||Registry::Value::srvcomment::Path==srvcomment
            if (
                self.cp.has_option("computers", "content")
                and not self.cp.get("computers", "content") == ""
            ):
                for c in [
                    x.split("::")
                    for x in self.cp.get("computers", "content").split("||")
                ]:
                    if not c[0] in self.content:
                        self.content[c[0]] = []
                    self.content[c[0]].append(
                        [desArrayIfUnic(x.split("==")) for x in c[1:]]
                    )

        if self.cp.has_section("querymanager"):
            if self.cp.has_option("querymanager", "list"):
                simple = self.cp.get("querymanager", "list")
                self.list = {}
                if simple != "":
                    # Software/ProductName||Hardware/ProcessorType||Hardware/OperatingSystem||Drive/TotalSpace
                    for l in simple.split("||"):
                        self.list[l] = ["string"]  # TODO also int...

            if self.cp.has_option("querymanager", "double"):
                double = self.cp.get("querymanager", "double")
                self.double = {}
                if double != "":
                    # Software/Products::Software/ProductName##Software/ProductVersion
                    for l in double.split("||"):
                        name, vals = l.split("::")
                        val1, val2 = vals.split("##")
                        self.double[name] = [[val1, "string"], [val2, "string"]]

            if self.cp.has_option("querymanager", "halfstatic"):
                halfstatic = self.cp.get("querymanager", "halfstatic")
                self.halfstatic = {}
                if halfstatic != "":
                    # Registry/Value::Path##DisplayName
                    for l in halfstatic.split("||"):
                        name, vals = l.split("::")
                        k, v = vals.split("##")
                        self.halfstatic[name] = ["string", k, v]

            if self.cp.has_option("querymanager", "extended"):
                extended = self.cp.get("querymanager", "extended")
                self.extended = {}
                if extended != "":
                    for l in extended.split("||"):
                        self.extended[l] = ["string"]


def desArrayIfUnic(x):
    if len(x) == 1:
        return x[0]
    return x
