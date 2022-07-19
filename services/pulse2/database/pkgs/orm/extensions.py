# -*- coding: utf-8; -*-
#
# (c) 2019-2012 Siveo, http://www.siveo.net/
#
# This file is part of Pulse 2, http://www.siveo.net/
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

class Extensions(object):
    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getRule_order(self):
        if self.rule_order is not None:
            return self.rule_order

        return 0

    def getRule_name(self):
        if self.rule_name is not None:
            return self.rule_name

        return ""

    def getName(self):
        if self.name is not None:
            return self.name

        return ""

    def getExtension(self):
        if self.extension is not None:
            return self.extension

        return ""

    def getMagic_command(self):
        if self.magic_command is not None:
            return self.magic_command

        return ""

    def getBang(self):
        if self.bang is not None:
            return self.bang

        return ""

    def getFile(self):
        if self.file is not None:
            return self.file

        return ""

    def getStrings(self):
        if self.strings is not None:
            return self.strings

        return ""

    def getProposition(self):
        if self.proposition is not None:
            return self.proposition

        return ""

    def getDescription(self):
        if self.description is not None:
            return self.description

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "rule_order": self.getRule_order(),
            "rule_name": self.getRule_name(),
            "name": self.getName(),
            "extension": self.getExtension(),
            "magic_command": self.getMagic_command(),
            "bang": self.getBang(),
            "file": self.getFile(),
            "strings": self.getStrings(),
            "proposition": self.getProposition(),
            "description": self.getDescription(),
        }

