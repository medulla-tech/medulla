# -*- coding: utf-8; -*-
#
# (c) 2021-2022 Siveo, http://www.siveo.net
#
# $Id$
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

# uses SA to handle sessions

""" Class to map pkgs.pkgs_rules_algos to SA
"""


class Pkgs_rules_algos(object):
    """Mapping between pkgs.pkgs_rules_algos and SA
    colunm table: ' id,name,description,level'
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getName(self):
        if self.name is not None:
            return self.name

        return -1

    def getDescription(self):
        if self.description is not None:
            return self.description

        return ""

    def getLevel(self):
        if self.level is not None:
            return self.level

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "name": self.getName(),
            "description": self.getDescription(),
            "level": self.getLevel(),
        }

    def toH(self):
        return {
            "id": self.id,
            "name": self.ars_share_id,
            "description": self.packages_id,
            "level": self.level,
        }
