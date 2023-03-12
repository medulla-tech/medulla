# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

# uses SA to handle sessions

""" 
    Class to map pkgs.pkgs_shares_ars_web to SA
"""


class Pkgs_shares_ars_web(object):
    """
    Mapping between pkgs.pkgs_shares_ars_web and SA
    colunm table: 'id,ars_share_id,packages_id,status,finger_print,size,date_edition'
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getArs_share_id(self):
        if self.ars_share_id is not None:
            return self.ars_share_id

        return -1

    def getPackages_id(self):
        if self.packages_id is not None:
            return self.packages_id

        return ""

    def getStatus(self):
        if self.status is not None:
            return self.status

        return ""

    def getFinger_print(self):
        if self.finger_print is not None:
            return self.finger_print

        return ""

    def getSize(self):
        if self.size is not None:
            return self.size

        return 0

    def getEdition_date(self):
        if self.date_edition is not None:
            return self.date_edition

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "ars_share_id": self.getArs_share_id(),
            "packages_id": self.getPackages_id(),
            "status": self.getStatus(),
            "finger_print": self.getFinger_print(),
            "size": self.getSize(),
            "date_edition": self.getEdition_date(),
        }

    def toH(self):
        return {
            "id": self.id,
            "ars_share_id": self.ars_share_id,
            "packages_id": self.packages_id,
            "status": self.status,
            "finger_print": self.finger_print,
            "size": self.size,
            "date_edition": self.date_edition,
        }
