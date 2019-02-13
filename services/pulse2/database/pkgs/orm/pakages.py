# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging
from sqlalchemy.orm import create_session


class Packages(object):

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getLabel(self):
        if self.label != None:
            return self.label
        else:
            return ""

    def getDescription(self):
        if self.description is not None:
            return self.description
        else:
            return ""

    def getUuid(self):
        if self.uuid is not None:
            return self.uuid
        else:
            return ""

    def getVersion(self):
        if self.version is not None:
            return self.version
        else:
            return ""

    def getOs(self):
        if self.os is not None:
            return self.os
        else:
            return ""

    def getMetaGenerator(self):
        if self.metagenerator is not None:
            return self.metagenerator
        else:
            return "expert"

    def getEntity_id(self):
        if self.entity_id is not None:
            return self.entity_id
        else:
            return "0"

    def getSub_packages(self):
        if self.sub_packages is not None:
            return self.sub_packages
        else:
            return []

    def getReboot(self):
        if self.reboot is not None:
            return self.getReboot
        else:
            return ""

    def getInventory_associateinventory(self):
        if self.inventory_associateinventory is not None:
            return self.inventory_associateinventory
        else:
            return ""

    def getInventory_licenses(self):
        if self.inventory_licenses is not None:
            return self.inventory_licenses
        else:
            return ""

    def getQversion(self):
        if self.Qversion is not None:
            return self.Qversion
        else:
            return ""

    def getQvendor(self):
        if self.Qvendor is not None:
            return self.Qvendor
        else:
            return ""

    def getQsoftware(self):
        if self.Qsoftware is not None:
            return self.Qsoftware
        else:
            return ""

    def getBoolcnd(self):
        if self.boolcnd is not None:
            return self.boolcnd
        else:
            return 0

    def getPostCommandSuccess_command(self):
        if self.postCommandSuccess_command is not None:
            return self.postCommandSuccess_command
        else:
            return ""

    def getPostCommandSuccess_name(self):
        if self.postCommandSuccess_name is not None:
            return self.postCommandSuccess_name
        else:
            return ""
    def getInstallInit_command(self):
        if self.installInit_command is not None:
            return self.installInit_command
        else:
            return ""

    def getInstallInit_name(self):
        if self.installInit_name is not None:
            return self.installInit_name
        else:
            return ""

    def getPostCommandFailure_command(self):
        if self.postCommandFailure_command is not None:
            return self.postCommandFailure_command
        else:
            return ""

    def getPostCommandFailure_name(self):
        if self.postCommandFailure_name is not None:
            return self.postCommandFailure_name
        else:
            return ""

    def getCommand_command(self):
        if self.postCommandFailure_command is not None:
            return self.postCommandFailure_command
        else:
            return ""

    def getCommand_name(self):
        if self.command_name is not None:
            return self.command_name
        else:
            return ""

    def getPreCommand_command(self):
        if self.preCommand_command is not None:
            return self.preCommand_command
        else:
            return ""

    def getPreCommand_name(self):
        if self.preCommand_name is not None:
            return self.preCommand_name
        else:
            return ""


    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            'entity_id' : self.getEntity_id(),
            'description' : self.getDescription(),
            'sub_packages' : self.getSub_packages(),
            'id': self.getUuid(),
            'pk_id': self.getId(),
            'commands':{
                'postCommandSuccess': {
                    'command': self.getPostCommandSuccess_command(),
                    'name': self.getPostCommandSuccess_name()
                },
                'installInit':{
                    'command': self.getInstallInit_command(),
                    'name': self.getInstallInit_name()
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
                    "name": self.getPreCommand_name()
                }
            },
            'name': self.getLabel(),
            'targetos': self.getOs(),
            'reboot': self.getReboot(),
            'version': self.getVersion(),
            'inventory': {
                'associateinventory': self.getInventory_associateinventory(),
                'licenses': self.getInventory_licenses(),
                "queries": {
                    "Qversion": self.getQversion(),
                    "Qvendor": self.getQvendor(),
                    "boolcnd": self.getBoolcnd(),
                    "Qsoftware": self.getQsoftware()
                },
                "metagenerator": self.getMetaGenerator()
            }
        }
