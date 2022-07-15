# -*- coding: utf-8; -*-
#
# (c) 2021-2022 Siveo, http://www.siveo.net/
#
# $Id$
#
# This file is part of Pulse 2, http://www.siveo.net
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

""" Class to map pkgs.pkgs_shares_ars to SA
"""

class Pkgs_shares_ars(object):
    """Mapping between pkgs.pkgs_shares_ars and SA
    colunm : 'id,hostname,jid,pkgs_shares_id
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getHostname(self):
        if self.hostname is not None:
            return self.hostname

        return ""

    def getJid(self):
        if self.jid is not None:
            return self.jid

        return ""

    def getShareid(self):
        if self.pkgs_shares_id is not None:
            return self.pkgs_shares_ars

        return ""

    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            "id": self.getId(),
            "hostname": self.getHostname(),
            "jid": self.getJid(),
            "pkgs_shares_id": getShareid(),
        }

    def toH(self):
        return {
            "id": self.id,
            "hostname": self.hostname,
            "jid": self.jid,
            "pkgs_shares_id": self.pkgs_shares_id,
        }
