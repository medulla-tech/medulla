# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later


import logging

""" Class to map pkgs.pkgs_rules_global to SA
"""


class Pkgs_rules_global(object):
    """Mapping between pkgs.pkgs_rules_global and SA
    colunm table: 'id,pkgs_rules_algos_id,pkgs_cluster_ars_id,order,suject'
    """

    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getRules_algos_id(self):
        if self.pkgs_rules_algos_id is not None:
            return self.pkgs_rules_algos_id

        return -1

    def getCluster_ars_id(self):
        if self.pkgs_cluster_ars_id is not None:
            return self.pkgs_cluster_ars_id

        return ""

    def getOrder(self):
        if self.order is not None:
            return self.order

        return ""

    def getSuject(self):
        if self.suject is not None:
            return self.suject

        return ""

    def to_array(self):
        return {
            "id": self.getId(),
            "pkgs_rules_algos_id": self.getRules_algos_id(),
            "pkgs_cluster_ars_id": self.getCluster_ars_id(),
            "order": self.getOrder(),
            "suject": self.getSuject(),
        }

    def toH(self):
        return {
            "id": self.id,
            "pkgs_rules_algos_id": self.pkgs_rules_algos_id,
            "pkgs_cluster_ars_id": self.pkgs_cluster_ars_id,
            "order": self.order,
            "suject": self.suject,
        }
