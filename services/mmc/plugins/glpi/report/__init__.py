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
import logging
import operator

from mmc.support.mmctools import SecurityContext
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.database_utils import toUUID, fromUUID


logger = logging.getLogger()


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
        # Be sure to get all entities
        self.ctx.locations = None
        if hasattr(self.ctx, 'locationsid'):
            del self.ctx.locationsid
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
                        result['value'] = oper(result['value'], os_result['value'])
                        count = True
                if not count and oper == operator.add:
                    results.append(os_result)
        return results

    def getComputerCountByOSes(self, entities, os_names, exclude_names=[]):
        """
        Get computer count for os_names

        @param os_names: list of OS names to count
        @param exclude_names: list of OS names to exclude

        @return: count of machines by entity
        """
        if isinstance(os_names, basestring):
            os_names = [os_names]

        os_names = [os_name.replace('*', '%') for os_name in os_names]
        exclude_names = [exclude_name.replace('*', '%') for exclude_name in exclude_names]

        results = self._getComputerCountByOSes(entities, os_names, [])
        results = self._getComputerCountByOSes(entities, exclude_names,
                                               results, operator.sub)

        return results

    def _getComputerCountByType(self, entities, type):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            type_count = self.db.getMachineByType(self.ctx, type, count=1)
            result.append({'entity_id': toUUID(entity), 'value': type_count})
        return result

    def getComputerCountByTypes(self, entities, types):
        """
        Get computer count for types

        @param types: list of computer types to count

        @return: count of machines by entity
        """
        if isinstance(types, basestring):
            types = [types]
        types = [type.replace("*", "%") for type in types]

        results = []
        for type in types:
            type_results = self._getComputerCountByType(entities, type)
            for type_result in type_results:
                count = False
                for result in results:
                    if type_result['entity_id'] == result['entity_id']:
                        result['value'] += type_result['value']
                        count = True
                if not count:
                    results.append(type_result)
        return results

    def getComputerCountByState(self, entities, state):
        result = []
        state = state.replace("*", "%")
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            state_count = self.db.getMachineByState(self.ctx, state, count=1)
            result.append({'entity_id': toUUID(entity), 'value': state_count})
        return result

    def _constructSoftwareTuple(self, soft):
        """
        @param soft: string or dict
        @return: software tuple:
            (name, version, vendor)
        """
        name = version = vendor = None
        if soft and isinstance(soft, basestring):
            name = soft.replace('*', '%')
        elif type(soft) == dict:
            name = soft.get('name', None)
            if name:
                name = name.replace('*', '%')
            version = soft.get('version', None)
            if version:
                version = version.replace('*', '%')
            vendor = soft.get('vendor', None)
            if vendor:
                vendor = vendor.replace('*', '%')
        if name is None:
            logger.error("Missing software name")
            return None
        return (name, version, vendor)

    def _constructSoftwaresList(self, softs):
        """
        @param softs: dict, string, list of mixed string and dict
        @return: list of software tuples
            [(name, version, vendor),
             (name, version, vendor),
             (name, version, vendor),
             ...]
        """
        if type(softs) == list:
            return [self._constructSoftwareTuple(soft) for soft in softs]
        if softs:
            return [self._constructSoftwareTuple(softs)]
        return []

    def _getComputerCountBySoftware(self, entities, soft):
        result = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            soft_count = self.db.getMachineBySoftware(self.ctx, soft[0], version=soft[1], vendor=soft[2], count=1)
            result.append({'entity_id': toUUID(entity), 'value': soft_count})
        return result

    def _getComputerCountBySoftwares(self, entities, softs, results, oper=operator.add):
        for soft in softs:
            soft_results = self._getComputerCountBySoftware(entities, soft)
            for soft_result in soft_results:
                count = False
                for result in results:
                    if soft_result['entity_id'] == result['entity_id']:
                        result['value'] = oper(result['value'], soft_result['value'])
                        count = True
                if not count and oper == operator.add:
                    results.append(soft_result)
        return results

    def getComputerCountBySoftwares(self, entities, soft_names, exclude_names={}):
        """
        Get computer count for software names

        @param soft_names: list of softwares to count
        @param exclude_names: list of softwares to exclude

        soft_names can be a simple string (ie: 'Mozilla Firefox*')
        soft_names can be a dict (ie: {'name': 'Mozilla Firefox', 'version': '24.0', vendor:'Mozilla'})
        soft_names can be a list of mixed dict and strings

        Same for exclude_names

        @return: count of machines by entity
        """
        softs = self._constructSoftwaresList(soft_names)
        excludes = self._constructSoftwaresList(exclude_names)
        results = self._getComputerCountBySoftwares(entities, softs, [])
        results = self._getComputerCountBySoftwares(entities, excludes,
                                                    results, operator.sub)
        return results
