# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from sqlalchemy import and_, or_, not_
from pulse2.managers.group import ComputerGroupManager

from mmc.database.database_helper import DatabaseHelper

import logging

logger = logging.getLogger()

# USAGE :
#    def getAllMachines():
#        ...
#            # filtering on query
#            join_query, query_filter = filter(self.machine, filt)
#        ...


class DyngroupDatabaseHelper(DatabaseHelper):
    def init(self):
        self.filters = {}

    def filter(self, ctx, join_query, filt, query, grpby, filters=None):

        # Add filter clause
        filters = [t for t in filters if t is not None]
        if filters is not None:
            self.filters[ctx.userid] = and_(*filters)
        query_filter = None

        try:
            if "query" not in filt:
                return (join_query, query_filter)
            query_filter, join_tables = self.__treatQueryLevel(
                ctx, query, grpby, join_query, filt["query"]
            )
            for table in join_tables:
                join_query = join_query.join(table)
        except KeyError as e:
            self.logger.error(e)
        except TypeError as e:
            self.logger.error(e)

        return (join_query, query_filter)

    def __treatQueryLevel(
        self, ctx, query, grpby, join_query, queries, join_tables=[], invert=False
    ):
        """
        Use recursively by getAllMachines to build the query
        Used in the dyngroup context, to build AND, OR and NOT queries
        """
        bool = queries[0]
        level = queries[1]
        if bool == "OR":
            query_filter, join_tables = self.__treatQueryLevelOR(
                ctx, query, grpby, join_query, level, join_tables, invert
            )
        elif bool == "AND":
            query_filter, join_tables = self.__treatQueryLevelAND(
                ctx, query, grpby, join_query, level, join_tables, invert
            )
        elif bool == "NOT":
            query_filter, join_tables = self.__treatQueryLevelNOT(
                ctx, query, grpby, join_query, level, join_tables, invert
            )
        else:
            self.logger.error("Don't know this kind of bool operation : %s" % (bool))
        return (query_filter, join_tables)

    def __treatQueryLevelOR(
        self, ctx, query, grpby, join_query, queries, join_tables, invert=False
    ):
        """
        Build OR queries
        """
        filter_on = []
        for lq in queries:
            if len(lq) >= 4:
                if lq[1] == "dyngroup":
                    join_tab = self.computersTable()
                    computers = ComputerGroupManager().result_group_by_name(ctx, lq[3])
                    filt = self.computersMapping(computers, invert)
                else:
                    join_tab = self.mappingTable(ctx, lq)
                    filt = self.mapping(ctx, lq, invert)
                join_q = join_query
                if isinstance(join_tab, list):
                    for table in join_tab:
                        if table != join_query:
                            join_q = join_q.outerjoin(table)
                else:
                    join_q = join_q.join(join_tab)

                q = query.add_column(grpby).select_from(join_q).filter(filt)
                if ctx.userid in self.filters:
                    q = q.filter(self.filters[ctx.userid])

                if lq[2] == "online computer":
                    if lq[3] == "True":
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(grpby.notin_(lq[4]))

                if lq[2].lower() == "ou machine":
                    if lq[4]:
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(False)

                if lq[2].lower() == "ou user":
                    if lq[4]:
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(False)
                q = q.group_by(grpby).all()
                res = [x[1] for x in q]
                self.logger.debug(
                    "__treatQueryLevelOR : %s %s" % (str(lq), str(len(res)))
                )
                filter_on.append(grpby.in_(res))
            else:
                query_filter, join_tables = self.__treatQueryLevel(
                    ctx, query, grpby, join_query, lq, join_tables
                )
                filter_on.append(query_filter)
        query_filter = or_(*filter_on)
        return (query_filter, join_tables)

    def __treatQueryLevelAND(
        self, ctx, query, grpby, join_query, queries, join_tables, invert=False
    ):
        """
        Build AND queries
        """
        filter_on = []
        result_set = None
        optimize = True
        for lq in queries:
            if len(lq) >= 4:
                if lq[1] == "dyngroup":
                    join_tab = self.computersTable()
                    computers = ComputerGroupManager().result_group_by_name(ctx, lq[3])
                    filt = self.computersMapping(computers, invert)
                else:
                    join_tab = self.mappingTable(ctx, lq)
                    filt = self.mapping(ctx, lq, invert)
                join_q = join_query
                if isinstance(join_tab, list):
                    for table in join_tab:
                        if table != join_query:
                            join_q = join_q.outerjoin(table)
                else:
                    join_q = join_q.join(join_tab)

                q = query.add_column(grpby).select_from(join_q).filter(filt)
                if ctx.userid in self.filters:
                    q = q.filter(self.filters[ctx.userid])

                if lq[2] == "online computer":
                    if lq[3] == "True":
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(grpby.notin_(lq[4]))

                if lq[2].lower() == "ou machine":
                    if lq[4]:
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(False)

                if lq[2].lower() == "ou user":
                    if lq[4]:
                        q = q.filter(grpby.in_(lq[4]))
                    else:
                        q = q.filter(False)

                q = q.group_by(grpby).all()
                res = [x[1] for x in q]
                self.logger.debug(
                    "__treatQueryLevelAND  : %s %s" % (str(lq), str(len(res)))
                )
                if result_set is not None:
                    result_set.intersection_update(Set(res))
                else:
                    result_set = Set(res)
                filter_on.append(grpby.in_(res))

            else:
                optimize = False
                query_filter, join_tables = self.__treatQueryLevel(
                    ctx, query, grpby, join_query, lq, join_tables
                )
                filter_on.append(query_filter)
        if optimize:
            query_filter = grpby.in_(result_set)
        else:
            query_filter = and_(*filter_on)
        return (query_filter, join_tables)

    def __treatQueryLevelNOT(
        self, ctx, query, grpby, join_query, queries, join_tables, invert=False
    ):
        """
        Build NOT queries : it switches the invert flag
        """
        filter_on = []
        for lq in queries:
            if len(lq) >= 4:
                if lq[1] == "dyngroup":
                    join_tab = self.computersTable()
                    computers = ComputerGroupManager().result_group_by_name(ctx, lq[3])
                    filt = self.computersMapping(computers, invert)
                else:
                    join_tab = self.mappingTable(ctx, lq)
                    filt = self.mapping(ctx, lq, invert)
                join_q = join_query
                if isinstance(join_tab, list):
                    for table in join_tab:
                        if table != join_query:
                            join_q = join_q.outerjoin(table)
                else:
                    join_q = join_q.join(join_tab)

                q = query.add_column(grpby).select_from(join_q).filter(filt)
                if ctx.userid in self.filters:
                    q = q.filter(self.filters[ctx.userid])

                if lq[2] == "online computer":
                    if lq[3] == "True":
                        q = q.filter(grpby.notin_(lq[4]))
                    else:
                        q = q.filter(grpby.in_(lq[4]))

                if lq[2].lower() == "ou machine":
                    if lq[4]:
                        q = q.filter(grpby.notin_(lq[4]))

                if lq[2].lower() == "ou user":
                    if lq[4]:
                        q = q.filter(grpby.notin_(lq[4]))
                    else:
                        q = q.filter(False)

                q = q.group_by(grpby).all()
                res = [x[1] for x in q]
                self.logger.debug(
                    "__treatQueryLevelNOT : %s %s" % (str(lq), str(len(res)))
                )
                filter_on.append(grpby.in_(res))

            else:
                query_filter, join_tables = self.__treatQueryLevel(
                    ctx, query, grpby, join_query, lq, join_tables, invert
                )
                filter_on.append(query_filter)
        query_filter = not_(and_(*filter_on))
        return (query_filter, join_tables)

    def __mappingTables(self, queries):
        """
        Map multiple tables (use mappingTable)
        """
        ret = []
        for query in queries:
            if len(query) == 4:
                self.mappingTable(query)  # TODO check
        return ret

    def mappingTable(self, ctx, query):
        """
        Map a table name on a table mapping

        get the dyngroup format query

        return the mapped sqlalchemy table from the third field in the query struct
        """
        raise "mappingTable has to be defined"

    def mapping(self, ctx, query, invert=False):
        """
        Map a name and request parameters on a sqlalchemy request

        get the dyngroup format query
        get a flag saying if we want to map on the value or not to map on the value

        return the sqlalchemy equation to exec in a select_from()
        """
        raise "mapping has to be defined"

    def computersTable(self):
        """
        return the computers table mapping

        return the mapped sqlalchemy table for computer
        """
        raise "computersTable has to be defined"

    def computersMapping(self, computers, invert=False):
        """
        Map the computer object on the good field in the database

        get the list of computers we want to map
        get a flag saying if we want to map on the value or not to map on the value

        return the sqlalchemy equation to exec in a select_from()
        """
        raise "computersMapping has to be defined"


############################################
# specific code has to be defined
# for these two last method
############################################
#
#    def mappingTable(self, ctx, query):
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
#    def mapping(self, ctx, query, invert = False):
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


def onlyAddNew(obj, value, main):
    if isinstance(value, list):
        for i in value:
            try:
                obj.index(i)
            except BaseException:
                if i != main:
                    obj.append(i)
    else:
        try:
            obj.index(value)
        except BaseException:
            if value != main:
                obj.append(value)
    return obj
