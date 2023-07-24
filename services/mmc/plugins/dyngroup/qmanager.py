# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
QueryManager implementation.
"""
from sqlalchemy import types as sqltypes

import mmc.support.mmctools
import logging
import glob
import os
import re
import imp
from .bool_equations import BoolRequest
from mmc.plugins.base.computers import ComputerManager
import traceback
from mmc.support.mmctools import Singleton


class QueryManager(Singleton):
    """
    MMC Query manager.

    Query all plugins to know if they can query things.
    """

    def activate(self):
        self.logger = logging.getLogger()

        os.chdir(os.path.dirname(mmc.support.mmctools.__file__) + "/..")

        # hash{ pluginName:module }
        self.queryablePlugins = self._getQueryablePlugins()

        # list[ possibilities ]
        self.queryPossibilities = {}
        # query fields groups
        self.queryGroups = {}
        # extended possibilites
        self.extendedPossibilities = {}
        for pluginName in self.queryablePlugins:
            module = self.queryablePlugins[pluginName]
            self.queryPossibilities[pluginName] = self._getPluginQueryPossibilities(
                module
            )
            self.queryGroups[pluginName] = self._getPluginQueryGroups(module)
            self.extendedPossibilities[
                pluginName
            ] = self._getPluginExtendedPossibilities(module)

    def _getQueryablePlugins(self):
        """
        Check in existing plugins which one support the query manager
        """
        from mmc.agent import PluginManager

        pm = PluginManager()
        ret = {}

        for plugin in pm.getEnabledPluginNames():
            if os.path.exists(
                os.path.join("plugins/", plugin, "querymanager", "__init__.py")
            ):
                self.logger.debug("QueryManager is trying to load plugin " + plugin)
                f, p, d = imp.find_module(
                    "querymanager", [os.path.join("plugins/", plugin)]
                )
                try:
                    mod = imp.load_module(plugin + "_querymanager", f, p, d)
                    func = getattr(mod, "activate")
                    if func():
                        ret[plugin] = mod
                        self.logger.info("QueryManager plugin " + plugin + " loaded")
                    else:
                        self.logger.info(
                            "QueryManager plugin "
                            + plugin
                            + " is disabled by configuration."
                        )

                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error(
                        "QueryManager plugin "
                        + plugin
                        + " raise an exception.\n"
                        + plugin
                        + " not loaded."
                    )
                    continue
        return ret

    def _getPluginQueryPossibilities(self, pluginModule):
        func = getattr(pluginModule, "queryPossibilities")
        return func()

    def _getPluginQueryGroups(self, pluginModule):
        try:
            func = getattr(pluginModule, "queryGroups")
            return func()
        except:
            return {}

    def _getPluginExtendedPossibilities(self, pluginModule):
        func = getattr(pluginModule, "extendedPossibilities")
        return func()

    def _getPluginReplyToQuery(self, ctx, pluginModule, query):
        func = getattr(pluginModule, "query")
        return func(ctx, query[0], query[1])

    def getQueryPossibilities(self, ctx):
        return self.queryPossibilities

    def getQueryGroups(self, ctx):
        return self.queryGroups

    def getExtendedPossibilities(self, ctx):
        return self.extendedPossibilities

    def getPossiblesModules(self, ctx):
        return list(self.queryPossibilities.keys())

    def getQueryGroupsForModule(self, ctx, moduleName):
        try:
            return self.queryGroups[moduleName]
        except:
            self.logger.error("Dyngroup module %s don't exists" % (moduleName))
            return []

    def getPossiblesCriterionsInModule(self, ctx, moduleName):
        try:
            return list(self.queryPossibilities[moduleName].keys())
        except:
            self.logger.error("Dyngroup module %s don't exists" % (moduleName))
            return []

    def getTypeForCriterionInModule(self, ctx, moduleName, criterion):
        ret = self.queryPossibilities[moduleName][criterion]
        return ret[0]

    def getPossiblesValuesForCriterionInModule(
        self, ctx, moduleName, criterion, value1="", value2=None
    ):
        ret = self.queryPossibilities[moduleName][criterion]
        if ret[0] == "list" and len(ret) == 3:
            if len(value1) < ret[2]:
                return [ret[0], []]
        elif ret[0] == "double" and len(ret) > 2:
            if value2 == None:
                if len(value1) < ret[2]:
                    return [ret[0], []]
            elif len(ret) > 3 and len(value2) < ret[3]:
                return [ret[0], []]
        elif ret[0] == "double":
            table, cols = criterion.split("/")
            if value2 == None:  # ajax search on field 1
                return [ret[0], ret[1](ctx, table, cols, value1)]
            else:  # ajax search on field 2
                return [ret[0], ret[1](ctx, table, cols, value1, value2)]
        if value2 == None:
            return [ret[0], ret[1](ctx, value1)]

        return [ret[0], ret[1](ctx, value1, value2)]

    def getExtended(self, moduleName, criterion):
        """
        Return the type of a given criterion for a module.
        Extended criterions are criterions from which we know the type.

        @rtype: str
        @return: type of a given criterion for a module
        """
        retType = ""
        try:
            possibilities = self.extendedPossibilities[moduleName][criterion]
            ret = possibilities[1]
            if isinstance(ret, sqltypes.Date):
                retType = "date"
            elif isinstance(ret, sqltypes.Integer):
                retType = "int"
        except KeyError:
            pass
        except Exception as e:
            self.logger.error(e)
            self.logger.error("\n%s" % (traceback.format_exc()))
        return retType

    def replyToQuery(self, ctx, query, bool=None, min=0, max=10):
        return self._replyToQuery(ctx, query, bool)[int(min) : int(max)]

    def replyToQueryLen(self, ctx, query, bool=None):
        return len(self._replyToQuery(ctx, query, bool))

    def __recursive_query(self, ctx, query):
        op = query[0]
        ret = []
        for q in query[1]:
            if len(q) == 4:
                qid, module, criterion, value = q
                val, neg = self._getPluginReplyToQuery(
                    ctx, self.queryablePlugins[module], [criterion, value]
                )
            else:
                ret += [[mmc.plugins.dyngroup.replyToQuery(ctx, q, 0, -1), True]]
        return self.__treat_query(op, ret)

    def _replyToQuery(self, ctx, query, bool=None):
        raise "DON'T USE _replyToQuery!!!"
        self.__recursive_query(ctx, query)

        values = {}

        # TODO does not seems to work...
        # ['AND', [['1', 'dyngroup', 'groupname', 'test']]]
        for qid, module, criterion, value in query:
            val, neg = self._getPluginReplyToQuery(
                ctx, self.queryablePlugins[module], [criterion, value]
            )
            values[str(qid)] = [val, neg]

        self.logger.debug(values)

        br = BoolRequest()
        if bool == None or bool == "" or bool == 0 or bool == "0":
            bool = "AND(" + ",".join([a[0][0] for a in values]) + ")"

        all = ComputerManager().getComputersList(ctx)
        # all = ComputerManager().getRestrictedComputersList(ctx, 0, 50)
        # for the moment everything is based on names... should be changed into uuids
        # all = map(lambda a: a[1]['cn'][0], all.values())
        all = list(all.keys())
        values["A"] = [all, True]

        bool = "AND(A, " + bool + ")"

        br.parse(bool)
        if bool == None or not br.isValid():  # no bool specified = only AND
            if len(list(values.keys())) > 0:
                retour = values.pop()
                for val in values:
                    neg = val[1]
                    val = val[0]
                    if neg:
                        retour = list(filter(lambda a, val=val: a in val, retour))
                    else:
                        retour = list(filter(lambda a, val=val: a not in val, retour))

                return retour
            else:
                return (
                    []
                )  # TODO : when plugged on Machines : should return : Machine - values_neg
        else:
            retour = br.merge(values)
            return retour[0]

    def replyToQueryXML(self, ctx, query, bool=None, min=0, max=10):
        return self._replyToQueryXML(ctx, query, bool)[int(min) : int(max)]

    def replyToQueryXMLLen(self, ctx, query, bool=None):
        return len(self._replyToQueryXML(ctx, query, bool))

    def _replyToQueryXML(self, ctx, query, bool=None):
        values = {}
        for qid, module, criterion, value in query:
            val, neg = self._getPluginReplyToQuery(
                ctx, self.queryablePlugins[module], [criterion, value]
            )
            values[str(qid)] = [val, neg]

        self.logger.debug(values)

        br = BoolRequest()
        if bool == None or bool == "":
            bool = (
                "<AND><p>" + ("</p><p>".join([a[0][0] for a in values])) + "</p></AND>"
            )

        all = ComputerManager().getComputersList(ctx)
        # for the moment everything is based on names... should be changed into uuids
        all = [a[1]["cn"][0] for a in all]
        values["A"] = [all, True]

        bool = "<AND><p>A</p><p>" + bool + "</p></AND>"

        br.parseXML(bool)
        if bool == None or not br.isValid():  # no bool specified = only AND
            if len(list(values.keys())) > 0:
                retour = values.pop()
                for val in values:
                    neg = val[1]
                    val = val[0]
                    if neg:
                        retour = list(filter(lambda a, val=val: a in val, retour))
                    else:
                        retour = list(filter(lambda a, val=val: a not in val, retour))

                return retour
            else:
                return (
                    []
                )  # TODO : when plugged on Machines : should return : Machine - values_neg
        else:
            retour = br.merge(values)
            return retour[0]

    def getQueryTree(self, query, bool=None):
        if not isinstance(query, list):
            query = self.parse(query)

        values = {}

        for qid, module, criterion, value in query:
            values[str(qid)] = [qid, module, criterion, value]

        br = BoolRequest()
        if (
            bool == None or bool == "" or bool == 0 or bool == "0"
        ):  # no bool specified = only AND
            bool = "AND(" + ",".join([a for a in values]) + ")"

        br.parse(bool)
        if not br.isValid():  # invalid bool specified = only AND
            bool = "AND(" + ",".join([a for a in values]) + ")"
            br.parse(bool)

        try:
            return br.getTree(values)
        except KeyError:
            self.logger.error(
                "Your boolean equation does not match your request (if you are using a group please check it's correct)"
            )
            return None

    def parse(self, query):
        p1 = re.compile("\|\|")
        p2 = re.compile("::")
        p3 = re.compile("==")
        p4 = re.compile(", ")
        p5 = "(^>.+<$)"
        p_sep_plural = "(^>|<$)"  # multiple entries are surounded by > and <

        queries = p1.split(query)
        ret = []
        for q in queries:
            a = p2.split(q)
            b = p3.split(a[0])
            c = p3.split(a[1])
            if re.search(p5, c[1]) != None:
                c[1] = re.sub(p_sep_plural, "", c[1])
            val = p4.split(c[1])
            if len(val) == 1:
                val = val[0]
            ret.append([b[0], b[1], c[0], val])
        return ret


def getAvailablePlugins(path):
    """
    Fetch all available MMC plugin

    @param path: UNIX path where the plugins are located
    @type path: str

    @return: list of all .py in a path
    @rtype: list
    """
    ret = []
    for item in glob.glob(os.path.join(path, "*", "__init__.py")):
        ret.append(item.split("/")[1])
    return ret
