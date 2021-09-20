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


class Extensions(object):

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getRule_order(self):
        if self.rule_order is not None:
            return self.rule_order
        else:
            return 0

    def getRule_name(self):
        if self.rule_name is not None:
            return self.rule_name
        else:
            return ""

    def getName(self):
        if self.name is not None:
            return self.name
        else:
            return ""

    def getExtension(self):
        if self.extension is not None:
            return self.extension
        else:
            return ""

    def getMagic_command(self):
        if self.magic_command is not None:
            return self.magic_command
        else:
            return ""

    def getBang(self):
        if self.bang is not None:
            return self.bang
        else:
            return ""

    def getFile(self):
        if self.file is not None:
            return self.file
        else:
            return ""

    def getStrings(self):
        if self.strings is not None:
            return self.strings
        else:
            return ""

    def getProposition(self):
        if self.proposition is not None:
            return self.proposition
        else:
            return ""

    def getDescription(self):
        if self.description is not None:
            return self.description
        else:
            return ""

    def to_array(self):
        return {
            'id': self.getId(),
            'rule_order': self.getRule_order(),
            'rule_name': self.getRule_name(),
            'name': self.getName(),
            'extension':self.getExtension(),
            'magic_command': self.getMagic_command(),
            'bang': self.getBang(),
            'file': self.getFile(),
            'strings': self.getStrings(),
            'proposition': self.getProposition(),
            'description': self.getDescription()
        }
