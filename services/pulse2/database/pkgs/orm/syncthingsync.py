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


class syncthingsync(object):

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getDate(self):
        if self.date != None:
            return self.date
        else:
            return ""

    def getUuidpackage(self):
        if self.uuidpackage is not None:
            return self.uuidpackage
        else:
            return ""

    def getTypesynchro(self):
        if self.typesynchro is not None:
            return self.typesynchro
        else:
            return ""

    def getRelayserver_jid(self):
        if self.relayserver_jid is not None:
            return self.relayserver_jid
        else:
            return ""

    def getWatching(self):
        if self.watching is not None:
            return self.watching
        else:
            return ""


    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            'id' : self.getId(),
            'date' : self.getDate(),
            'uuidpackage' : self.getUuidpackage(),
            'typesynchro': self.getTypesynchro(),
            'relayserver_jid': self.getRelayserver_jid(),
            'watching': self.getWatching()
        }
