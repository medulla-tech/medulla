# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

""" Class to map pkgs.Extensions to SA
"""

class Pkgs_shares(object):
    """Mapping between pkgs.pkgs_shares and SA
    colunm table :' id,name,comments,enabled,type,uri,ars_name,ars_id,share_path'
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getName(self):
        if self.name is not None:
            return self.name

        return ""

    def getComments(self):
        if self.comments is not None:
            return self.comments

        return ""

    def getEnabled(self):
        if self.enabled is not None:
            return self.enabled

        return 0

    def getType(self):
        if self.type is not None:
            return self.type

        return ""

    def getUri(self):
        if self.uri is not None:
            return self.uri

        return ""

    def getArs_name(self):
        if self.ars_name is not None:
            return self.ars_name

        return ""

    def getArs_id(self):
        if self.ars_id is not None:
            return self.ars_id

        return 0

    def getshare_path(self):
        if self.share_path is not None:
            return self.share_path

        return ""

    def getusedquotas(self):
        """
        This function is used to retrieve the used quotas
        """
        if self.usedquotas is not None:
            return self.usedquotas

        return ""

    def getquotas(self):
        """
        This function is used to retrieve the quotas
        """
        if self.quotas is not None:
            return self.quotas

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "name": self.getName(),
            "comments": self.getComments(),
            "enabled": self.getEnabled(),
            "type": self.getType(),
            "uri": self.getUri(),
            "ars_name": self.getArs_name(),
            "Ars_id": self.getArs_id(),
            "share_path": self.getshare_path(),
            "usedquotas": self.getusedquotas(),
            "quotas": self.getquotas(),
        }

    def toH(self):
        return {
            "id": self.id,
            "name": self.name,
            "comments": self.comments,
            "enabled": self.enabled,
            "type": self.type,
            "uri": self.uri,
            "ars_name": self.ars_name,
            "ars_id": self.ars_id,
            "share_path": self.share_path,
            "usedquotas": self.usedquotas,
            "quotas": self.quotas,
        }
