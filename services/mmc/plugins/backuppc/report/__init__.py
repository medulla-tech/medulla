# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Plugin to manage the interface with BackupPC
"""


class exportedReport(object):
    # Add meta class singleton_N

    def getServerUsedDiskSpace(self, entities, servername, num):
        # output format
        result = []
        result.append({"entity_id": "UUID1", "value": 14})
        result.append({"entity_id": "UUID2", "value": 18})
        return result

    def getLevel1(self, entities, servername, num):
        # output format
        result = []
        result.append({"entity_id": "UUID1", "value": 100})
        result.append({"entity_id": "UUID2", "value": 150})
        return result

    def getLevel2_1(self, entities, servername, num):
        # output format
        result = []
        result.append({"entity_id": "UUID1", "value": 31})
        result.append({"entity_id": "UUID2", "value": 48})
        return result

    def getLevel2_2(self, entities, servername, num):
        # output format
        result = []
        result.append({"entity_id": "UUID1", "value": 47})
        result.append({"entity_id": "UUID2", "value": 29})
        return result
