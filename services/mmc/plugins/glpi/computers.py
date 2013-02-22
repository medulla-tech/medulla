#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
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

"""
Glpi implementation of the interface ComputerI
Provides functions to get computers informations filtered on criterions
"""
from mmc.plugins.base import ComputerI
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.utilities import complete_ctx
from pulse2.managers.imaging import ComputerImagingManager
import logging
import exceptions

class GlpiComputers(ComputerI):
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()
        self.config = GlpiConfig("glpi", conffile)
        self.glpi = Glpi()

    def getComputer(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list and location != None:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass

        try:
            return self.glpi.getComputer(ctx, filt)
        except Exception, e:
            if len(e.args) > 0 and e.args[0].startswith('NOPERM##'):
                machine = e.args[0].replace('NOPERM##', '')
                self.logger.warn("User %s does not have good permissions to access machine '%s'" % (ctx.userid, machine))
                return False
            raise e

    def getComputersNetwork(self, ctx, params):
        if 'uuids' in params:
            return self.glpi.getComputersList(ctx, {'uuid' : params['uuids'] }).values()
        elif 'uuid' in params:
            return self.glpi.getComputersList(ctx, {'uuid' : params['uuid'] }).values()
        return self.glpi.getComputersList(ctx, {}).values()

    def getMachineMac(self, ctx, params):
        # format : { 'uuid' : ['mac1' ...], ... }
        if params.has_key('uuids'):
            return self.glpi.getMachinesMac(params['uuids'])
        elif params.has_key('uuid'):
            return {params['uuid'] : self.glpi.getMachineMac(params['uuid'])}

    def getMachineIp(self, ctx, filt):
        return self.glpi.getMachineIp(filt['uuid'])

    def getMachineHostname(self, ctx, filt = None):
        machines = self.glpi.getRestrictedComputersList(ctx, 0, -1, filt)
        ret = []
        for x, m in machines.values():
            if 'hostname' not in m:
                if type(m['cn']) == list:
                    m['hostname'] = m['cn'][0]
                else:
                    m['hostname'] = m['cn']
            if 'uuid' not in m:
                if type(m['objectUUID']) == list:
                    m['uuid'] = m['objectUUID'][0]
                else:
                    m['uuid'] = m['objectUUID']
            ret.append(m)
        if len(ret) == 1:
            return ret[0]
        return ret

    def getComputersList(self, ctx, filt = None):
        """
        Return a list of computers

        @param filter: computer name filter
        @type filter: str

        @return: LDAP results
        @rtype:
        """
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list and location != None:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass

        return self.glpi.getComputersList(ctx, filt)

    def __restrictLocationsOnImagingServerOrEntity(self, filt, location, ctx):
        if filt.has_key('imaging_server') and filt['imaging_server'] != '':
            entity_uuid = ComputerImagingManager().getImagingServerEntityUUID(filt['imaging_server'])
            if entity_uuid != None:
                filt['entity_uuid'] = entity_uuid
            else:
                self.logger.warn("can't get the entity that correspond to the imaging server %s"%(filt['imaging_server']))
                return [False, 0]

        if filt.has_key('entity_uuid') and filt['entity_uuid'] != '':
            grep_entity = None
            for l in location:
                if l.uuid == filt['entity_uuid']:
                    grep_entity = l
            if grep_entity != None:
                filt['ctxlocation'] = [grep_entity]
            else:
                self.logger.warn("the user '%s' try to filter on an entity he shouldn't access '%s'"%(ctx.userid, filt['entity_uuid']))
                return [False, 0]
        return [True, filt]

    def getRestrictedComputersListLen(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list and location != None:
                location = [location]
            filt['ctxlocation'] = location
            filt = self.__restrictLocationsOnImagingServerOrEntity(filt, location, ctx)
            if not filt[0]: return 0
            filt = filt[1]
        except exceptions.AttributeError:
            pass
        return self.glpi.getRestrictedComputersListLen(ctx, filt)

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = None, advanced = True, justId = False, toH = False):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list and location != None:
                location = [location]
            filt['ctxlocation'] = location
            filt = self.__restrictLocationsOnImagingServerOrEntity(filt, location, ctx)
            if not filt[0]: return {}
            filt = filt[1]
        except exceptions.AttributeError:
            pass
        return self.glpi.getRestrictedComputersList(ctx, min, max, filt, advanced, justId, toH)

    def getTotalComputerCount(self):
        return self.glpi.getTotalComputerCount()

    def getComputerCount(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list and location != None:
                location = [location]
            filt['ctxlocation'] = location
            filt = self.__restrictLocationsOnImagingServerOrEntity(filt, location, ctx)
            if not filt[0]: return 0
            filt = filt[1]
        except exceptions.AttributeError:
            pass
        return self.glpi.getComputerCount(ctx, filt)

    def canAddComputer(self):
        return False

    def addComputer(self, ctx, params):
        """
        Add a computer in the main computer list

        @param name: name of the computer. It should be a fqdn
        @type name: str

        @param comment: a comment for the computer list
        @type comment: str

        @return: the machine uuuid
        @rtype: str
        """
        #name = params["computername"]
        #comment = params["computerdescription"].encode("utf-8")
        #uuid = str(uuid1())
        self.logger.warning("addComputer has not yet been implemented for glpi")
        return False

    def canDelComputer(self):
        return False

    def delComputer(self, ctx, uuid, backend):
        """
        Remove a computer, given its uuid
        """
        self.logger.warning("delComputer has not yet been implemented for glpi")
        return False


    def getComputerByMac(self, mac):
        ret = self.glpi.getMachineByMacAddress('imaging_module', mac)
        if type(ret) == list:
            if len(ret) != 0:
                return ret[0]
            else:
                return None
        return ret

    def getComputersListHeaders(self, ctx):
        ret = []
        if 'cn' in self.config.summary:
            ret.append(['cn', 'Computer Name'])
        if 'os' in self.config.summary:
            ret.append(['os', 'Operating System'])
        if 'description' in self.config.summary:
            ret.append(['displayName', 'Description'])
        if 'type' in self.config.summary:
            ret.append(['type', 'Computer Type'])
        if 'user' in self.config.summary:
            ret.append(['user', 'Last Logged User'])
        if 'entity' in self.config.summary:
            ret.append(['entity', 'Entity'])
        if 'location' in self.config.summary:
            ret.append(['location', 'Location'])

        return ret

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        return self.glpi.isComputerNameAvailable(ctx, locationUUID, name)

