# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com/
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
Report methods for glpi plugin
"""

import operator

from mmc.support.mmctools import SecurityContext
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.database_utils import toUUID, fromUUID


class exportedReport(object):

    def __init__(self):
        self.db = Glpi()
        self.ctx = SecurityContext()
        self.ctx.userid = "root"

    def _getEntitiesIds(self, entities=[]):
        """
        Return a list of entities ids for the request

        @param entitites: a list of entities uuids
        @return: list of entities ids
        """
        # get all entities uuids for the current user
        if entities == []:
            entities = [entity.toH()['uuid'] for entity in self.db.getAllEntities(self.ctx)]
        return [fromUUID(str(entity)) for entity in entities]

    def _getComputerCountByOS(self, entities, os_name):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            os_count = self.db.getMachineByOsLike(self.ctx, os_name, count=1)
            result.append({'entity_id': toUUID(entity), 'value': os_count})
        return result

    def _getComputerCountByOSes(self, entities, os_names, results, oper=operator.add):
        for os_name in os_names:
            os_results = self._getComputerCountByOS(entities, os_name)
            for os_result in os_results:
                count = False
                for result in results:
                    if os_result['entity_id'] == result['entity_id']:
                         oper(result['value'], os_result['value'])
                         count = True
                if not count and oper == operator.add:
                    results.append(os_result)
        return results

    def getComputerCountByOSes(self, entities, os_names, exclude_names=[]):
        """
        Get computer count for os_names

        @param os_names: list of OS names to count
        @param exclude: list of OS names to exclude

        @return: count of machines
        """
        if isinstance(os_names, basestring):
            os_names = [os_names]

        os_names = [os_name.replace('*', '%') for os_name in os_names]
        exclude_names = [exclude_name.replace('*', '%') for exclude_name in exclude_names]

        results = self._getComputerCountByOSes(entities, os_names, [])
        results = self._getComputerCountByOSes(entities, exclude_names,
                                               results, operator.sub)

        return results

    def getComputerCountByType(self, entities, type):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            type_count = self.db.getMachineByType(self.ctx, type, count=1)
            result.append({'entity_id': toUUID(entity), 'value': type_count})
        return result

    def getComputerCountByState(self, entities, state):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            state_count = self.db.getMachineByState(self.ctx, state, count=1)
            result.append({'entity_id': toUUID(entity), 'value': state_count})
        return result

    def getComputerCountBySoftware(self, entities, name, version=None):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            if version:
                name = [name, version]
            software_count = self.db.getMachineBySoftwareAndVersion(self.ctx, name, count=1)
            result.append({'entity_id': toUUID(entity), 'value': software_count})
        return result
