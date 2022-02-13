# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
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

# uses SA to handle sessions

# file : pkgs/orm/pkgs_shares.py

import logging

""" Class to map pkgs.Extensions to SA
"""


class Pkgs_shares(object):
    """ Mapping between pkgs.pkgs_shares and SA
        colunm table :' id,name,comments,enabled,type,uri,ars_name,ars_id,share_path'
    """

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getName(self):
        if self.name is not None:
            return self.name
        else:
            return ""

    def getComments(self):
        if self.comments is not None:
            return self.comments
        else:
            return ""

    def getEnabled(self):
        if self.enabled is not None:
            return self.enabled
        else:
            return 0

    def getType(self):
        if self.type is not None:
            return self.type
        else:
            return ""

    def getUri(self):
        if self.uri is not None:
            return self.uri
        else:
            return ""

    def getArs_name(self):
        if self.ars_name is not None:
            return self.ars_name
        else:
            return ""

    def getArs_id(self):
        if self.ars_id is not None:
            return self.ars_id
        else:
            return 0

    def getshare_path(self):
        if self.share_path is not None:
            return self.share_path
        else:
            return ""

    def getusedquotas(self):
        """
            This function is used to retrieve the used quotas
        """
        if self.usedquotas is not None:
            return self.usedquotas
        else:
            return ""

    def getquotas(self):
        """
            This function is used to retrieve the quotas
        """
        if self.quotas is not None:
            return self.quotas
        else:
            return ""

    def to_array(self):
        return {
            'id': self.getId(),
            'name': self.getName(),
            'comments': self.getComments(),
            'enabled': self.getEnabled(),
            'type': self.getType(),
            'uri': self.getUri(),
            'ars_name': self.getArs_name(),
            'Ars_id': self.getArs_id(),
            'share_path': self.getshare_path(),
            'usedquotas': self.getusedquotas(),
            'quotas': self.getquotas()}

    def toH(self):
        return {
            'id': self.id,
            'name': self.name,
            'comments': self.comments,
            'enabled': self.enabled,
            'type': self.type,
            'uri': self.uri,
            'ars_name': self.ars_name,
            'ars_id': self.ars_id,
            'share_path': self.share_path,
            'usedquotas': self.usedquotas,
            'quotas': self.quotas}
