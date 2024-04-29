# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


class Packages(object):
    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getLabel(self):
        if self.label is not None:
            return self.label

        return ""

    def getDescription(self):
        if self.description is not None:
            return self.description

        return ""

    def getUuid(self):
        if self.uuid is not None:
            return self.uuid

        return ""

    def getVersion(self):
        if self.version is not None:
            return self.version

        return ""

    def getOs(self):
        if self.os is not None:
            return self.os

        return ""

    def getMetaGenerator(self):
        if self.metagenerator is not None:
            return self.metagenerator

        return "expert"

    def getEntity_id(self):
        if self.entity_id is not None:
            return self.entity_id

        return "0"

    def getSub_packages(self):
        if self.sub_packages is not None:
            return self.sub_packages

        return ""

    def getReboot(self):
        if self.reboot is not None:
            return self.getReboot

        return ""

    def getInventory_associateinventory(self):
        if self.inventory_associateinventory is not None:
            return self.inventory_associateinventory

        return ""

    def getInventory_licenses(self):
        if self.inventory_licenses is not None:
            return self.inventory_licenses

        return ""

    def getQversion(self):
        if self.Qversion is not None:
            return self.Qversion

        return ""

    def getQvendor(self):
        if self.Qvendor is not None:
            return self.Qvendor

        return ""

    def getQsoftware(self):
        if self.Qsoftware is not None:
            return self.Qsoftware

        return ""

    def getBoolcnd(self):
        if self.boolcnd is not None:
            return self.boolcnd

        return 0

    def getPostCommandSuccess_command(self):
        if self.postCommandSuccess_command is not None:
            return self.postCommandSuccess_command

        return ""

    def getPostCommandSuccess_name(self):
        if self.postCommandSuccess_name is not None:
            return self.postCommandSuccess_name

        return ""

    def getInstallInit_command(self):
        if self.installInit_command is not None:
            return self.installInit_command

        return ""

    def getInstallInit_name(self):
        if self.installInit_name is not None:
            return self.installInit_name

        return ""

    def getPostCommandFailure_command(self):
        if self.postCommandFailure_command is not None:
            return self.postCommandFailure_command

        return ""

    def getPostCommandFailure_name(self):
        if self.postCommandFailure_name is not None:
            return self.postCommandFailure_name

        return ""

    def getCommand_command(self):
        if self.command_command is not None:
            return self.command_command

        return ""

    def getCommand_name(self):
        if self.command_name is not None:
            return self.command_name

        return ""

    def getPreCommand_command(self):
        if self.preCommand_command is not None:
            return self.preCommand_command

        return ""

    def getPreCommand_name(self):
        if self.preCommand_name is not None:
            return self.preCommand_name

        return ""

    def getpkgs_share_id(self):
        if self.pkgs_share_id is not None:
            return self.pkgs_share_id

        return None

    def getedition_status(self):
        if self.edition_status is not None:
            return self.edition_status

        return ""

    def getconf_json(self):
        if self.conf_json is not None:
            return self.conf_json

        return ""

    def getsize(self):
        if self.size is not None:
            return self.size

        return "0"

    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            "entity_id": self.getEntity_id(),
            "description": self.getDescription(),
            "sub_packages": self.getSub_packages(),
            "id": self.getUuid(),
            "pk_id": self.getId(),
            "commands": {
                "postCommandSuccess": {
                    "command": self.getPostCommandSuccess_command(),
                    "name": self.getPostCommandSuccess_name(),
                },
                "installInit": {
                    "command": self.getInstallInit_command(),
                    "name": self.getInstallInit_name(),
                },
                "postCommandFailure": {
                    "command": self.getPostCommandFailure_command(),
                    "name": self.getPostCommandFailure_name(),
                },
                "command": {
                    "command": self.getCommand_command(),
                    "name": self.getCommand_name(),
                },
                "preCommand": {
                    "command": self.getPreCommand_command(),
                    "name": self.getPreCommand_name(),
                },
            },
            "name": self.getLabel(),
            "targetos": self.getOs(),
            "reboot": self.getReboot(),
            "version": self.getVersion(),
            "inventory": {
                "associateinventory": self.getInventory_associateinventory(),
                "licenses": self.getInventory_licenses(),
                "queries": {
                    "Qversion": self.getQversion(),
                    "Qvendor": self.getQvendor(),
                    "boolcnd": self.getBoolcnd(),
                    "Qsoftware": self.getQsoftware(),
                },
                "metagenerator": self.getMetaGenerator(),
            },
            "pkgs_share_id": self.getpkgs_share_id(),
            "edition_status": self.getedition_status(),
            "conf_json": self.getconf_json(),
            "size": self.getsize(),
        }
