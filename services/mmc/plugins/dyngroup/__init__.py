#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
MMC Dyngroup Backend plugin
It provide an API to work with the informations in the Dyngroup database.
It also provide access to the QueryManager API
"""

from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext

import logging
import re
import exceptions

from mmc.plugins.dyngroup.bool_equations import BoolRequest
from mmc.plugins.dyngroup.qmanager import QueryManager
from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.config import DGConfig
from mmc.plugins.dyngroup.group import DyngroupGroup
from mmc.plugins.dyngroup.profile import DyngroupProfile
from mmc.plugins.dyngroup.computers import DyngroupComputers

from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.base import LdapUserGroupControl
from pulse2.managers.group import ComputerGroupManager
from pulse2.managers.profile import ComputerProfileManager

from pulse2.version import getVersion, getRevision # pyflakes.ignore

# health check
from mmc.plugins.dyngroup.health import scheduleCheckStatus

APIVERSION = '0:0:0'
queryManager = None
config = None

def getApiVersion(): return APIVERSION

def activate():
    logger = logging.getLogger()
    global config
    config = DGConfig()
    config.init("dyngroup")

    if config.disable:
        logger.warning("Plugin dyngroup: disabled by configuration.")
        return False

    DyngroupDatabase().activate(config)
    if not DyngroupDatabase().db_check():
        return False

    ComputerGroupManager().register("dyngroup", DyngroupGroup)
    ComputerProfileManager().register("dyngroup", DyngroupProfile)
    ComputerManager().register("dyngroup", DyngroupComputers)

    if config.check_db_enable:
        scheduleCheckStatus(config.check_db_interval)

    return True


def activate_2():
    if isDynamicEnable():
        logger = logging.getLogger()
        logger.info("Plugin dyngroup: dynamic groups are enabled")
        global queryManager
        queryManager = QueryManager()
        queryManager.activate()
    return True


def calldb(func, *args, **kw):
    return getattr(DyngroupDatabase(), func).__call__(*args, **kw)

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

def isDynamicEnable():
    return config.dynamicEnable

def isProfilesEnable(): #NEW
    return config.profilesEnable

class RpcProxy(RpcProxyI):
    # new groups implementations
    def arePartOfAProfile(self, uuids):
        ctx = self.currentContext
        return DyngroupDatabase().arePartOfAProfile(ctx, uuids)

    def hasMoreThanOneEthCard(self, uuids):
        ctx = self.currentContext
        moreThanOneEthCard = []
        # Exclude computers who have more than one network card
        nets = ComputerManager().getComputersNetwork(ctx, {'uuids':uuids})
        for net in nets:
            net = net[1]
            if len(net['macAddress']) > 1:
                if net['objectUUID'] not in moreThanOneEthCard:
                    logging.getLogger().debug("Computer %s (%s) has more than one network card, it won't be added to profile" % (net['cn'], net['objectUUID']))
                    moreThanOneEthCard.append(net['objectUUID'][0])

        return moreThanOneEthCard

    def countallprofiles(self, params): #NEW
        ctx = self.currentContext
        count = DyngroupDatabase().countallgroups(ctx, params, 1)
        return count

    def countallgroups(self, params):
        ctx = self.currentContext
        count = DyngroupDatabase().countallgroups(ctx, params)
        return count

    def getallprofiles(self, params): #NEW
        ctx = self.currentContext
        groups = DyngroupDatabase().getallgroups(ctx, params, 1)
        return xmlrpcCleanup(map(lambda g:g.toH(), groups))

    def getmachinesprofiles(self, ids): #NEW
        ret = []
        for id in ids:
            ret.append(self.getmachineprofile(id))
        return ret

    def getmachineprofile(self, id): #NEW
        ctx = self.currentContext
        profile = DyngroupDatabase().getMachineProfile(ctx, id)
        return xmlrpcCleanup(profile)

    def getallgroups(self, params):
        ctx = self.currentContext
        groups = DyngroupDatabase().getallgroups(ctx, params)
        return xmlrpcCleanup(map(lambda g:g.toH(), groups))

    def profile_name_exists(self, name, gid=None):
        ctx = self.currentContext
        return DyngroupDatabase().groupNameExists(ctx, name, gid, True)

    def group_name_exists(self, name, gid=None):
        #TODO possible risks of collision betwen share/group/profiles...
        ctx = self.currentContext
        return DyngroupDatabase().groupNameExists(ctx, name, gid)

    def get_group(self, id, ro=False, root_context=False):
        ctx = root_context and self.getContext() or self.currentContext
        grp = DyngroupDatabase().get_group(ctx, id, ro)
        if grp:
            return xmlrpcCleanup(grp.toH())
        return xmlrpcCleanup(False)

    def delete_group(self, id):
        ctx = self.currentContext
        if self.isprofile(id):
            grp = DyngroupDatabase().get_group(ctx, id, True)
            profile_UUID = grp.getUUID()
            ComputerProfileManager().delProfile(profile_UUID)
        return xmlrpcCleanup(DyngroupDatabase().delete_group(ctx, id))

    def getContext(self, user='root'):
            s = SecurityContext()
            s.userid = user
            s.userdn = LdapUserGroupControl().searchUserDN(s.userid)
            return s

    def create_group(self, name, visibility, type=0, parent_id=None):
        if type == 2 and parent_id is not None: # convergence group, get parent group's user context
            _group_user = DyngroupDatabase()._get_group_user(parent_id)
            ctx = self.getContext(user=_group_user)
        else:
            ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().create_group(ctx, name, visibility, type, parent_id))

    def create_profile(self, name, visibility): #NEW
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().create_group(ctx, name, visibility, 1))

    def tos_group(self, id):
        self.logger.error('tos_group is not implemented')

    def setname_group(self, id, name):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setname_group(ctx, id, name))

    def setvisibility_group(self, id, visibility):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().setvisibility_group(ctx, id, visibility))

    def request_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().request_group(ctx, id))

    def setrequest_group(self, id, request, root_context=False):
        ctx = root_context and self.getContext() or self.currentContext
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
        return xmlrpcCleanup(map(lambda g:g.toH(), DyngroupDatabase().result_group(ctx, id, start, end, filter, False)))

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
        return xmlrpcCleanup(DyngroupDatabase().todyn_group(ctx, id))

    def isrequest_group(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().isrequest_group(ctx, id))

    def isprofile(self, id): #NEW
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().isprofile(ctx, id))

    def reload_group(self, id):
        ctx = self.currentContext
        ret = DyngroupDatabase().reload_group(ctx, id, queryManager)
        # WIP : call ComputerProfileManager to add machines
#        if self.isprofile(id):
#            ComputerProfileManager().addComputersToProfile(ctx, [1, 2], id) # fake!
        return xmlrpcCleanup(ret)

    def addmembers_to_group(self, id, uuids):
        ctx = self.currentContext
        # remove all the computers that cant be added to a profile from the list
        didnt_work = []
        are_some_to_remove = False
        if self.isprofile(id):
            computers = []
            uuid2key = {}
            for c in uuids:
                computers.append(uuids[c]['uuid'])
                uuid2key[uuids[c]['uuid']] = c
            didnt_work = ComputerProfileManager().areForbiddebComputers(computers)

            if len(didnt_work) > 0:
                logging.getLogger().debug("Can't add the following computers in that profile %s : %s"%(str(id), str(didnt_work)))
                for i in didnt_work:
                    if uuid2key[i] in uuids:
                        are_some_to_remove = True
                        uuids.pop(uuid2key[i])

        if len(uuids) != 0:
            if self.isprofile(id):
                ComputerProfileManager().addComputersToProfile(ctx, uuids, id)
            else:
                ret = DyngroupDatabase().addmembers_to_group(ctx, id, uuids)
                return [ret]
        return xmlrpcCleanup([not are_some_to_remove, didnt_work])

    def delmembers_to_group(self, id, uuids):
        ctx = self.currentContext
        ret = DyngroupDatabase().delmembers_to_group(ctx, id, uuids)
        # WIP : call ComputerProfileManager to add machines
        if len(uuids) != 0 and self.isprofile(id):
            ComputerProfileManager().delComputersFromProfile(uuids, id)
        return xmlrpcCleanup(ret)

    def importmembers_to_group(self, id, elt, values):
        ctx = self.currentContext
        # get machines uuids from values
        request, bool, optimization = forgeRequest(elt, values)
        req = {'request':request, 'equ_bool':bool, 'optimization' : optimization}
        machines = ComputerManager().getRestrictedComputersList(ctx, 0, -1, req)
        # put in the wanted format
        uuids = {}
        if type(machines) == dict:
            machines = machines.values()
        for m in machines:
            uuid = m[1]['objectUUID'][0]
            hostname = m[1]['cn'][0]
            uuids[uuid] = {'hostname':hostname, 'uuid':uuid}

        # insert uuid in group with addmembers_to_group
        return self.addmembers_to_group(id, uuids)

    def getForbiddenComputersUUID(self, profile_UUID = None):
        ret = ComputerProfileManager().getForbiddenComputersUUID(profile_UUID)
        return ret

    def share_with(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().share_with(ctx, id))

    def add_share(self, id, shares):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().add_share(ctx, id, shares))

    def del_share(self, id, shares):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().del_share(ctx, id, shares))

    def can_edit(self, id):
        ctx = self.currentContext
        return xmlrpcCleanup(DyngroupDatabase().can_edit(ctx, id))

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

    def getQueryGroupsForModule(self, moduleName):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getQueryGroupsForModule(ctx, moduleName))

    def getPossiblesCriterionsInMainModule(self):
        moduleName = ComputerManager().main
        return self.getPossiblesCriterionsInModule(moduleName)

    def getPossiblesCriterionsInModule(self, moduleName):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getPossiblesCriterionsInModule(ctx, moduleName))

    def getTypeForCriterionInModule(self, moduleName, criterion):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getTypeForCriterionInModule(ctx, moduleName, criterion))

    def getPossiblesValuesForCriterionInModule(self, moduleName, criterion):
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        return xmlrpcCleanup(queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion))

    def getPossiblesValuesForCriterionInModuleFuzzy(self, moduleName, criterion, search = ''):
        """
        Used in "double" type. It's used where you search on 2 fields of a table.
        Example: On table Software, you can search on ProductName and ProductVersion

        This function is related to field 1
        """
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        result = queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion, unescape(search))
        ret = result[1]
        # Only returns the 100 first results
        # FIXME: maybe the range limitation could be done on the queryManager ?
        ret = ret[:100]
        return xmlrpcCleanup(ret)

    def getPossiblesValuesForCriterionInModuleFuzzyWhere(self, moduleName, criterion, value1, value2 = ''):
        """
        Used in "double" type. It's used where you search on 2 fields of a table.
        Example: On table Software, you can search on ProductName and ProductVersion

        This function is related to field 2
        """
        ctx = self.currentContext
        if not isDynamicEnable():
            return False
        result = queryManager.getPossiblesValuesForCriterionInModule(ctx, moduleName, criterion, unescape(value1), unescape(value2))
        ret = result[1]
        # Only returns the 100 first results
        # FIXME: maybe the range limitation could be done on the queryManager ?
        ret = ret[:100]
        return xmlrpcCleanup(ret)

    def checkBoolean(self, bool):
        if bool == None or bool == '':
            return [True, -1]
        b = BoolRequest()
        try:
            b.parse(bool)
        except Exception, e:
            logging.getLogger().debug('checkBoolean failed : ')
            logging.getLogger().debug(e)
            return [False, -1]
        return xmlrpcCleanup([b.isValid(), b.countOps()])

    def update_machine_cache(self):
        ctx = self.currentContext
        dyndatabase = DyngroupDatabase()

        cache = dyndatabase.getAllMachinesUuid()
        machines = ComputerManager().getRestrictedComputersList(ctx, 0, -1, {'uuids':cache.keys()}, False, False, True)

        need_update = {}
        for m in machines:
            if m['hostname'] != cache[m['uuid']]:
                need_update[m['uuid']] = m['hostname']

        dyndatabase.updateNewNames(need_update)
        return len(need_update)

    def set_profile_imaging_server(self, gid, imaging_uuid):
        if not self.isprofile(gid):
            return False
        dyndatabase = DyngroupDatabase()
        ret = dyndatabase.setProfileImagingServer(gid, imaging_uuid)
        return xmlrpcCleanup(ret)

    def get_profile_imaging_server(self, gid):
        if gid == '':
            return False
        if not self.isprofile(gid):
            return False
        ret = DyngroupDatabase().getProfileImagingServer(gid)
        return xmlrpcCleanup(ret)

    def set_profile_entity(self, gid, entity_uuid):
        if not self.isprofile(gid):
            return False
        dyndatabase = DyngroupDatabase()
        ret = dyndatabase.setProfileEntity(gid, entity_uuid)
        return xmlrpcCleanup(ret)

    def get_profile_entity(self, gid):
        if gid == '':
            return False
        if not self.isprofile(gid):
            return False
        ret = DyngroupDatabase().getProfileEntity(gid)
        return xmlrpcCleanup(ret)

    def isProfileAssociatedToImagingServer(self, gid):
        ims_uuid = self.get_profile_imaging_server(gid)
        return (ims_uuid != False)

    def getExtended(self, moduleName, criterion):
        if not isDynamicEnable():
            return ""
        else:
            return queryManager.getExtended(moduleName, criterion)

    def add_convergence_datas(self, parent_group_id, deploy_group_id, done_group_id, pid, p_api, command_id, active, params):
        ret = DyngroupDatabase().add_convergence_datas(parent_group_id, deploy_group_id, done_group_id, pid, p_api, command_id, active, params)
        return xmlrpcCleanup(ret)

    def edit_convergence_datas(self, gid, papi, package_id, datas):
        ret = DyngroupDatabase().edit_convergence_datas(gid, papi, package_id, datas)
        return xmlrpcCleanup(ret)

    def getConvergenceStatus(self, gid):
        ret = DyngroupDatabase().getConvergenceStatus(gid)
        return xmlrpcCleanup(ret)

    def get_convergence_groups_to_update(self, papi_id, package_id):
        ret = DyngroupDatabase().get_convergence_groups_to_update(papi_id, package_id)
        return xmlrpcCleanup(ret)

    def get_convergence_command_id(self, gid, papi, package_id):
        ret = DyngroupDatabase().get_convergence_command_id(gid, papi, package_id)
        return xmlrpcCleanup(ret)

    def is_convergence_active(self, gid, papi, package_id):
        ret = DyngroupDatabase().is_convergence_active(gid, papi, package_id)
        return xmlrpcCleanup(ret)

    def get_deploy_group_id(self, gid, papi, package_id):
        ret = DyngroupDatabase().get_deploy_group_id(gid, papi, package_id)
        return xmlrpcCleanup(ret)

    def get_convergence_group_parent_id(self, gid):
        ret = DyngroupDatabase().get_convergence_group_parent_id(gid)
        return xmlrpcCleanup(ret)


def __onlyIn(query, module):
    for q in query[1]:
        if len(q) == 4:
            if q[1] != module and q[1] != 'dyngroup':
                return False
        else:
            a = __onlyIn(q, module)
            if a == False:
                return False
    return True

def __addCtxFilters(ctx, filt = None):
    if filt is None:
        filt = {}
    try:
        if ctx.locations:
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = map(lambda l: l.toH(), location)
    except exceptions.AttributeError:
        pass
    return filt

def replyToQuery(ctx, query, bool = None, min = 0, max = 10, justId = False, toH = False, filt = None):
    if query == None: return []
    if __onlyIn(query, ComputerManager().main):
        ComputerManager().main
        filt = __addCtxFilters(ctx, filt)
        filt['query'] = query
        return xmlrpcCleanup(ComputerManager().getRestrictedComputersList(ctx, min, max, filt, False, justId, toH))
    else:
        return xmlrpcCleanup(QueryManager().replyToQuery(ctx, query, bool, min, max))

def replyToQueryLen(ctx, query, bool = None, filt = None):
    if query == None: return 0
    if __onlyIn(query, ComputerManager().main):
        ComputerManager().main
        filt = __addCtxFilters(ctx, filt)
        filt['query'] = query
        return xmlrpcCleanup(ComputerManager().getRestrictedComputersListLen(ctx, filt))
    else:
        return xmlrpcCleanup(QueryManager().replyToQueryLen(ctx, query, bool))

def forgeRequest(elt, values):
    i = 1
    module = ComputerManager().main
    crit = elt
    requests = []
    bools = []
    optimization = True
    for val in values:
        # If there is a wildcard in a value, we don't flag this request for
        # possible optimization
        if optimization:
            optimization = not "*" in val
        requests.append("%i==%s::%s==%s" % (i, module, crit, val))
        bools.append(str(i))
        i += 1
    request = '||'.join(requests)
    bools = "OR("+",".join(bools)+")"
    if optimization and ComputerManager().getManagerName() == "inventory":
        optim = { "criterion" : crit, "data" : values }
    else:
        optim = {}
    return (request, bools, optim)

def getDefaultModule():
    return config.defaultModule

def getMaxElementsForStaticList():
    return config.maxElementsForStaticList

def unescape(search):
    if type(search) == str and search != '':
        return re.sub('&lt;', '<', re.sub('&gt;', '>', search))
    return search

