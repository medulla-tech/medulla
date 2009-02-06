# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id: target.py 265 2008-08-29 09:08:03Z oroussy $
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" Class to map msc.target to SA
"""

import sqlalchemy

class Target(object):
    """ Mapping between msc.target and SA
    """
    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.create_session()
        session.save_or_update(self)
        session.flush()
        session.close()

    def getId(self):
        return self.id

    def getUUID(self):
        return self.target_uuid

    def getFQDN(self):
        return self.target_name

    def getShortName(self):
        return self.target_name

    def getIps(self):
        return self.target_ipaddr.split('||')

    def getMacs(self):
        return self.target_macaddr.split('||')

    def toH(self):
        return {
            'id': self.id,
            'target_name': self.target_name,
            'target_uuid': self.target_uuid,
            'target_ipaddr': self.target_ipaddr,
            'target_macaddr': self.target_macaddr,
            'target_bcast': self.target_bcast,
            'mirrors': self.mirrors,
            'id_group': self.id_group
        }
