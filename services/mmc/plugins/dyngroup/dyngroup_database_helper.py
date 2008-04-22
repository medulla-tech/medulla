#   
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: database.py 36 2008-04-15 12:22:06Z oroussy $
#
# This file is part of MMC.
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

import logging
from mmc.support.mmctools import Singleton
from sqlalchemy import *
from sqlalchemy.exceptions import SQLError


# USAGE :
#    def getAllMachines():
#        ...
#            # filtering on query
#            join_query, query_filter = filter(self.machine, filt)
#        ...

class DyngroupDatabaseHelper(Singleton):
    def init(self):
        self.logger = logging.getLogger()

    def filter(self, join_query, filt):
        query_filter = None
        try:
            query_filter, join_tables = self.__treatQueryLevel(filt['query'])
            for table in join_tables:
                join_query = join_query.join(table)
        except KeyError:
            pass
        except TypeError:
            pass
       
        return (join_query, query_filter)

    def __treatQueryLevel(self, queries, join_tables = [], invert = False):
        """
        Use recursively by getAllMachines to build the query
        Used in the dyngroup context, to build AND, OR and NOT queries
        """
        bool = queries[0]
        level = queries[1]
        if bool == 'OR':
            query_filter, join_tables = self.__treatQueryLevelOR(level, join_tables, invert)
        elif bool == 'AND':
            query_filter, join_tables = self.__treatQueryLevelAND(level, join_tables, invert)
        elif bool == 'NOT':
            query_filter, join_tables = self.__treatQueryLevelNOT(level, join_tables, invert)
        else:
            self.logger.error("Don't know this kind of bool operation : %s" % (bool))
        return (query_filter, join_tables)

    def __treatQueryLevelOR(self, queries, join_tables, invert = False):
        """
        Build OR queries
        """
        filter_on = []
        for q in queries:
            if len(q) == 4:
                join_tab = self.mappingTable(q)
                join_tables = onlyAddNew(join_tables, join_tab)
                filter_on.append(self.mapping(q, invert))
            else:
                query_filter, join_tables = self.__treatQueryLevel(q, join_tables)
                filter_on.append(query_filter)
        query_filter = or_(*filter_on)
        return (query_filter, join_tables)

    def __treatQueryLevelAND(self, queries, join_tables, invert = False):
        """
        Build AND queries
        """
        filter_on = []
        for q in queries:
            if len(q) == 4:
                join_tab = self.mappingTable(q)
                join_tables = onlyAddNew(join_tables, join_tab)
                filter_on_mapping = self.mapping(q, invert)
                if type(filter_on_mapping) == list:
                    filter_on.extend(filter_on_mapping)
                else:
                    filter_on.append(filter_on_mapping)
            else:
                query_filter, join_tables = self.__treatQueryLevel(q, join_tables)
                filter_on.append(query_filter)
        query_filter = and_(*filter_on)
        return (query_filter, join_tables)

    def __treatQueryLevelNOT(self, queries, join_tables, invert = False):
        """
        Build NOT queries : it switches the invert flag
        """
        filter_on = []
        for q in queries:
            if len(q) == 4:
                join_tab = self.mappingTable(q)
                join_tables = onlyAddNew(join_tables, join_tab)
                filter_on.append(self.mapping(q, not invert))
            else:
                query_filter, join_tables = self.__treatQueryLevel(q, join_tables, not invert)
                filter_on.append(query_filter)
        query_filter = and_(*filter_on)
        return (query_filter, join_tables)

    def __mappingTables(self, queries):
        """
        Map multiple tables (use mappingTable)
        """
        ret = []
        for query in queries:
            if len(query) == 4:
                self.mappingTable(query)
        return ret

    def mappingTable(self, query):
        """
        Map a table name on a table mapping

        get the dyngroup format query

        return the mapped sqlalchemy table from the third field in the query struct
        """
        raise "mappingTable has to be defined"

    def mapping(self, query, invert = False):
        """
        Map a name and request parameters on a sqlalchemy request

        get the dyngroup format query
        get a flag saying if we want to map on the value or not to map on the value

        return the sqlalchemy equation to exec in a select_from()
        """
        raise "mapping has to be defined"

############################################
## specific code has to be defined 
## for these two last method
############################################
#
#    def mappingTable(self, query):
#        """
#        Map a table name on a table mapping
#        """
#        if query[2] == 'OS':
#            return self.os
#        elif query[2] == 'ENTITY':
#            return self.location
#        elif query[2] == 'SOFTWARE':
#            return [self.inst_software, self.licenses, self.software]
#        return []
#
#    def mapping(self, query, invert = False):
#        """
#        Map a name and request parameters on a sqlalchemy request
#        """
#        if query[2] == 'OS':
#            if invert:
#                return self.os.c.name != query[3]
#            else:
#                return self.os.c.name == query[3]
#        elif query[2] == 'ENTITY':
#            if invert:
#                return self.location.c.name != query[3]
#            else:
#                return self.location.c.name == query[3]
#        elif query[2] == 'SOFTWARE':
#            if invert:
#                return self.software.c.name != query[3]
#            else:
#                return self.software.c.name == query[3]


def onlyAddNew(obj, value):
    if type(value) == list:
        for i in value:
            try:
                obj.index(i)
            except:
                obj.append(i)
    else:
        try:
            obj.index(value)
        except:
            obj.append(value)
    return obj

