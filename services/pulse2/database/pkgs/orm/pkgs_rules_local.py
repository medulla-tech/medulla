# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

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
