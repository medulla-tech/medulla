# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
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

"""
Plugin to manage the interface with BackupPC
"""


class exportedReport(object):
    #Add meta class singleton_N

    def getServerUsedDiskSpace(self, entities, servername, num):
        return [
            {'entity_id': 'UUID1', 'value': 14},
            {'entity_id': 'UUID2', 'value': 18},
        ]

    def getLevel1(self, entities, servername, num):
        return [
            {'entity_id': 'UUID1', 'value': 100},
            {'entity_id': 'UUID2', 'value': 150},
        ]

    def getLevel2_1(self, entities, servername, num):
        return [
            {'entity_id': 'UUID1', 'value': 31},
            {'entity_id': 'UUID2', 'value': 48},
        ]

    def getLevel2_2(self, entities, servername, num):
        return [
            {'entity_id': 'UUID1', 'value': 47},
            {'entity_id': 'UUID2', 'value': 29},
        ]
