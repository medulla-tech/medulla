# -*- coding: utf-8; -*-
#
# (c) 2021-2022 Siveo, http://www.siveo.net/
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

""" Class to map pkgs.pkgs_rules_local to SA
"""


class Pkgs_rules_local(object):
    """Mapping between pkgs.pkgs_rules_local and SA
    colunm table: 'id,pkgs_rules_algos_id,order,subject,pkgs_shares_id'
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getRules_algos_id(self):
        if self.pkgs_rules_algos_id is not None:
            return self.pkgs_rules_algos_id

        return -1

    def getShares_id(self):
        if self.pkgs_shares_id is not None:
            return self.pkgs_shares_id

        return ""

    def getOrder(self):
        if self.order is not None:
            return self.order

        return ""

    def getSuject(self):
        if self.subject is not None:
            return self.subject

        return ""

    def getPermission(self):
        if self.permission is not None:
            return self.permision

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "pkgs_rules_algos_id": self.getRules_algos_id(),
            "pkgs_shares_id": self.getShares_id(),
            "order": self.getOrder(),
            "subject": self.getSuject(),
            "permission": self.getPermission(),
        }

    def toH(self):
        return {
            "id": self.id,
            "pkgs_rules_algos_id": self.pkgs_rules_algos_id,
            "pkgs_shares_id": self.pkgs_shares_id,
            "order": self.order,
            "subject": self.subject,
            "permision": self.permission,
        }
