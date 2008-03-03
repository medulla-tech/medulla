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

from mmc.plugins.base import ComputerI
from mmc.plugins.glpi.database import GlpiConfig, Glpi
from mmc.plugins.glpi.utilities import complete_ctx
import logging
import exceptions

class GlpiComputers(ComputerI):
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()
        self.config = GlpiConfig("glpi")
        self.glpi = Glpi()

    def getComputer(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass
            
        return self.glpi.getComputer(filt)
    
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
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass
            
        return self.glpi.getComputersList(filt)

    def getRestrictedComputersListLen(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass
        return self.glpi.getRestrictedComputersListLen(filt)
                    
    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = None, advanced = True):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass
        return self.glpi.getRestrictedComputersList(min, max, filt, advanced)

    def getComputerCount(self, ctx, filt = None):
        if filt == None or filt == '':
            filt = {}
        try:
            complete_ctx(ctx)
            location = ctx.locations
            if type(location) != list:
                location = [location]
            filt['ctxlocation'] = location
        except exceptions.AttributeError:
            pass
        return self.glpi.getComputerCount(filt)

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

    def delComputer(self, ctx, uuid):
        """
        Remove a computer, given its uuid
        """
        self.logger.warning("delComputer has not yet been implemented for glpi")
        return False


