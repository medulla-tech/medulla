from mmc.support.mmctools import shLaunch
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
import mmc.support.mmctools
import logging
import glob
import os
import re
import imp
import time
import datetime
import exceptions

from mmc.plugins.dyngroup.bool_equations import BoolRequest
from mmc.plugins.dyngroup.querymanager import QueryManager
from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.config import DGConfig
from mmc.plugins.dyngroup.group import DyngroupGroup

from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.pulse2.group import ComputerGroupManager


VERSION = '2.0.0'
APIVERSION = '0:0:0'
REVISION = int('$Rev: 149 $'.split(':')[1].strip(' $'))
logger = None
queryManager = None
config = None

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    global logger
    logger = logging.getLogger()
    global config
    config = DGConfig("dyngroup")

    if str(config.disable) == str(1):
        logger.warning("Plugin dyngroup: disabled by configuration.")
        return False

    if isDynamicEnable():
        logger.warning("Plugin dyngroup: dynamic groups are enabled")
        global queryManager
        queryManager = QueryManager()
        queryManager.activate()

    DyngroupDatabase().activate()
    if not DyngroupDatabase().db_check():
        return False

    ComputerGroupManager().register("dyngroup", DyngroupGroup)

    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

def isDynamicEnable():
    return config.dynamicEnable

class RpcProxy(RpcProxyI):
    # new groups implementations
    def countallgroups(self, params):
        ctx = self.currentContext
        count = DyngroupDatabase().countallgroups(ctx, params)
        return count

    def getallgroups(self, params):
        ctx = self.currentContext
        groups = DyngroupDatabase().getallgroups(ctx, params)
        return xmlrpcCleanup(map(lambda g:g.toH(), groups))
        
    def get_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().get_group(ctx, id).toH())
        
    def delete_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().delete_group(ctx, id))
        
    def create_group(self, name, visibility):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().create_group(ctx, name, visibility))

    def tos_group(self, id):
        ctx = self.currentContext
        self.logger.error('tos_group is not implemented')
        pass
        
    def setname_group(self, id, name):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setname_group(ctx, id, name))
        
    def setvisibility_group(self, id, visibility):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setvisibility_group(ctx, id, visibility))
    
    def request_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().request_group(ctx, id))

    def setrequest_group(self, id, request):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setrequest_group(ctx, id, request))

    def bool_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().bool_group(ctx, id))

    def setbool_group(self, id, bool):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setbool_group(ctx, id, bool))

    def requestresult_group(self, id, start, end, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().requestresult_group(ctx, id, start, end, filter, queryManager))

    def countrequestresult_group(self, id, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().countrequestresult_group(ctx, id, filter, queryManager))

    def result_group(self, id, start, end, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(map(lambda g:g.toH(), DyngroupDatabase().result_group(ctx, id, start, end, filter)))

    def countresult_group(self, id, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().countresult_group(ctx, id, filter))

    def canshow_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().canshow_group(ctx, id))

    def show_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().show_group(ctx, id))

    def hide_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().hide_group(ctx, id))

    def isdyn_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().isdyn_group(ctx, id))

    def todyn_group(self, id):
        ctx = self.currentContext
        self.logger.error("todyn_group is not implemented")
        pass

    def isrequest_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().isrequest_group(ctx, id))

    def reload_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().reload_group(ctx, id, queryManager))

    def addmembers_to_group(self, id, uuids):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().addmembers_to_group(ctx, id, uuids))

    def delmembers_to_group(self, id, uuids):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().delmembers_to_group(ctx, id, uuids))

    ################## dyngroup part
    def getQueryPossibilities(self):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        result = queryManager.getQueryPossibilities(ctx)
        return xmlrpcCleanup(result)
    
    def getPossiblesModules(self):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getPossiblesModules(ctx))
    
    def getPossiblesCriterionsInModule(self, moduleName):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getPossiblesCriterionsInModule(ctx, moduleName))
    
    def getPossiblesValuesForCriterionInModule(self, moduleName, criterion):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion))
    
    def getPossiblesValuesForCriterionInModuleFuzzy(self, moduleName, criterion, search = ''):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        retour = queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion, search)
        p0 = re.compile('\*')
        search = p0.sub('.*', search)
        p1 = re.compile(search, re.IGNORECASE)
        ret = []
        for r in retour[1]:
            if type(r) == str and p1.search(r):
                ret.append(r)
        return xmlrpcCleanup(ret)
    
    def getPossiblesValuesForCriterionInModuleFuzzyWhere(self, moduleName, criterion, search, value2 = ''):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        retour = queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion)
        p1 = re.compile(value2, re.IGNORECASE)
        ret = []
        for r in retour[1][search]: # must take into account * ...
            if type(r) == str and p1.search(r):
                ret.append(r)
        return ret
    
def __onlyGlpi(query):
    for q in query[1]:
        if len(q) == 4:
            if q[1] != 'glpi':
                return False
        else:
            a = __onlyGlpi(q)
            if a == False:
                return False
    return True

def __addCtxFilters(ctx, filt = {}):
    try:
        if ctx.locations:
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
    except exceptions.AttributeError:
        pass
    return filt

def replyToQuery(ctx, query, bool = None, min = 0, max = 10):
    # TODO : don't do it specifically for glpi, but call directly .getRestrictedComputersList on ComputerManager().main
    # each time all the request are for ComputerManager().main
    if ComputerManager().main == 'glpi':
        # check that queried modules are only glpi
        onlyGlpi = __onlyGlpi(query)
        filt = __addCtxFilters(ctx)

        # in this case, only call ComputerManager().getRestrictedComputersList with correct filters:
        if onlyGlpi:
            filt['query'] = query
            return xmlrpcCleanup(ComputerManager().getRestrictedComputersList(ctx, min, max, filt))
        else:
            return xmlrpcCleanup(QueryManager().replyToQuery(ctx, query, bool, min, max))
    else:
        return xmlrpcCleanup(QueryManager().replyToQuery(ctx, query, bool, min, max))

def replyToQueryLen(ctx, query, bool = None):
    if ComputerManager().main == 'glpi':
        # check that queried modules are only glpi
        onlyGlpi = __onlyGlpi(query)
        filt = __addCtxFilters(ctx)

        # in this case, only call ComputerManager().getRestrictedComputersList with correct filters:
        if onlyGlpi:
            filt['query'] = query
            return xmlrpcCleanup(ComputerManager().getRestrictedComputersListLen(ctx, filt))
        else:
            return xmlrpcCleanup(QueryManager().replyToQueryLen(ctx, query, bool))
    else:
        return xmlrpcCleanup(QueryManager().replyToQueryLen(ctx, query, bool))
 
