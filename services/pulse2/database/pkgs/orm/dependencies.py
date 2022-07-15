# -*- coding: utf-8; -*-
#
# (c) 2022 Siveo, http://www.siveo.net
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


""" Class to map pkgs.dependencies to SA
"""


class Dependencies(object):
    """Mapping between msc.bundle and SA"""

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getUuid_package(self):
        if self.uuid_package is not None:
            return self.uuid_package

        return ""

    def getUuid_dependency(self):
        if self.uuid_dependency is not None:
            return self.uuid_dependency

        return ""

    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            "id": self.getId(),
            "uuid_package": self.getUuid_package(),
            "uuid_dependency": self.getUuid_dependency(),
        }
