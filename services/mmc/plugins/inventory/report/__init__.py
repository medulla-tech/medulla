# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Report methods for glpi plugin
"""
import logging
import operator

from mmc.support.mmctools import SecurityContext
from pulse2.database.inventory import Inventory

logger = logging.getLogger()


def fromUUID(uuid):
    return int(uuid.replace("UUID", ""))


class exportedReport(object):
    def __init__(self):
        self.db = Inventory()
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
        if hasattr(self.ctx, "locationsid"):
            del self.ctx.locationsid
        # get all entities uuids for the current user
        if entities == []:
            entities = [
                entity.toH()["uuid"] for entity in self.db.getAllEntities(self.ctx)
            ]
        return [fromUUID(str(entity)) for entity in entities]

    def _getComputerCountByOSes(self, entities, os_names, results, oper=operator.add):
        os_results = []
        if os_names:
            for entity in self._getEntitiesIds(entities):
                self.ctx.locationsid = [entity]
                os_count = self.db.getMachineByOsLike(self.ctx, os_names, count=1)
                os_results.append({"entity_id": entity, "value": os_count})
        for os_result in os_results:
            count = False
            for result in results:
                if os_result["entity_id"] == result["entity_id"]:
                    if result["value"] is not None and os_result["value"] is not None:
                        result["value"] = oper(result["value"], os_result["value"])
                    else:
                        result["value"] = 0
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
        if isinstance(os_names, str):
            os_names = [os_names]

        os_names = [os_name.replace("*", "%") for os_name in os_names]
        exclude_names = [
            exclude_name.replace("*", "%") for exclude_name in exclude_names
        ]

        results = self._getComputerCountByOSes(entities, os_names, [])
        results = self._getComputerCountByOSes(
            entities, exclude_names, results, operator.sub
        )

        return results

    def getAllComputerCount(self, entities):
        """
        Count all computers by entity
        """
        results = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            count = self.db.getAllComputers(self.ctx, count=1)
            results.append({"entity_id": entity, "value": count})
        return results

    def getAllComputerCountByAgencies(self, entities, agencies):
        """
        Get computer count for agency

        @param agency: list of computer to count by agency

        @return: count of machines by entity
        """
        if isinstance(agencies, str):
            agencies = [agencies]
        results = []
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            self.ctx.agencies = agencies
            count = self.db.getAllComputersByAgencies(self.ctx, agencies, count=1)
            results.append({"entity_id": entity, "value": count})
        return results

    def getComputerCountByTypes(self, entities, types):
        """
        Get computer count for types

        @param types: list of computer types to count

        @return: count of machines by entity
        """
        if isinstance(types, str):
            types = [types]
        types = [type.replace("*", "%") for type in types]

        results = []
        if types:
            for entity in self._getEntitiesIds(entities):
                self.ctx.locationsid = [entity]
                type_count = self.db.getMachineByType(self.ctx, types, count=1)
                results.append({"entity_id": entity, "value": type_count})
        return results

    def getComputerCountByState(self, entities, state):
        result = []
        state = state.replace("*", "%")
        for entity in self._getEntitiesIds(entities):
            self.ctx.locationsid = [entity]
            state_count = self.db.getMachineByState(self.ctx, state, count=1)
            result.append({"entity_id": entity, "value": state_count})
        return result

    def _constructSoftwareTuple(self, soft):
        """
        @param soft: string or dict
        @return: software tuple:
            (name, version, vendor)
        """
        name = version = vendor = None
        if soft and isinstance(soft, str):
            name = soft.replace("*", "%")
        elif isinstance(soft, dict):
            name = soft.get("name", None)
            if name:
                name = name.replace("*", "%")
            version = soft.get("version", None)
            if version:
                version = version.replace("*", "%")
            vendor = soft.get("vendor", None)
            if vendor:
                vendor = vendor.replace("*", "%")
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
        if isinstance(softs, list):
            return [self._constructSoftwareTuple(soft) for soft in softs]
        if softs:
            return [self._constructSoftwareTuple(softs)]
        return []

    def _getComputerCountBySoftwares(self, entities, softs, results, oper=operator.add):
        soft_results = []
        if softs:
            for entity in self._getEntitiesIds(entities):
                self.ctx.locationsid = [entity]
                soft_count = self.db.getAllSoftwaresImproved(
                    self.ctx,
                    [soft[0] for soft in softs],
                    version=[soft[1] for soft in softs],
                    vendor=[soft[2] for soft in softs],
                    count=1,
                )
                soft_results.append({"entity_id": entity, "value": soft_count})
        for soft_result in soft_results:
            count = False
            for result in results:
                if soft_result["entity_id"] == result["entity_id"]:
                    if result["value"] is not None and soft_result["value"] is not None:
                        result["value"] = oper(result["value"], soft_result["value"])
                    else:
                        result["value"] = 0
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
        results = self._getComputerCountBySoftwares(
            entities, excludes, results, operator.sub
        )
        return results
