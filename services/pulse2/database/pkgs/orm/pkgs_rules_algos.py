# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

""" Class to map pkgs.pkgs_rules_algos to SA
"""
class Pkgs_rules_algos(object):
    """ Mapping between pkgs.pkgs_rules_algos and SA
        colunm table: ' id,name,description,level'
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
            return-1

    def getDescription(self):
        if self.description is not None:
            return self.description
        else:
            return ""

    def getLevel(self):
        if self.level is not None:
            return self.level
        else:
            return ""

    def to_array(self):
        return {
            'id': self.getId(),
            'name': self.getName(),
            'description': self.getDescription(),
            'level': self.getLevel()}

    def toH(self):
        return {
            'id': self.id,
            'name': self.ars_share_id,
            'description': self.packages_id,
            'level': self.level}
