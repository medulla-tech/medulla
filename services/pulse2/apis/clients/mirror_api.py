# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
# $Id: mirror_api.py 689 2009-02-06 15:18:43Z oroussy $
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

from pulse2.apis.clients import Pulse2Api
from pulse2.database.imaging import ImagingDatabase
from urlparse import urlparse
import logging
from pulse2.managers.location import ComputerLocationManager
# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class MirrorApi(Pulse2Api):
    def __init__(self, *attr):
        self.name = "MirrorApi"
        Pulse2Api.__init__(self, *attr)
#location = db.getTargetsEntity([uuid])[0]
#url = chooseImagingApiUrl(location[0].uuid)
    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        uuid = machine['uuid']
        try:
            entity_uuid = ComputerLocationManager().getMachinesLocations([uuid])[uuid]['uuid']
            parent_entities = [entity_uuid] + ComputerLocationManager().getLocationParentPath(entity_uuid)
            url = ''
            entity_uuid = ''
            db = ImagingDatabase()
            for _uuid in parent_entities:
                urlsearch = db.getEntityUrl(_uuid)
                if urlsearch is not None:
                    entity_uuid = _uuid
                    url = urlsearch
                    break;
            Entity_Name = ComputerLocationManager().getLocationName(entity_uuid)
            machine ['Entity_Name']= Entity_Name
            serverinfo = db.getImagingServerInfo(entity_uuid)
            machine ['entity_uuid']= entity_uuid
            machine ['server']= urlparse(url).hostname
            machine ['servernane']=serverinfo.name
        except:
            logging.getLogger().error("Cannot get Entity for this machine UUID (%s)" % uuid)
        d = self.callRemote("getMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getMirror", machine)
        return d

    #def getMirror(self, machine):
        #if self.initialized_failed:
            #return []
        #machine = self.convertMachineIntoH(machine)
        #d = self.callRemote("getMirror", machine)
        #d.addErrback(self.onError, "MirrorApi:getMirror", machine)
        #return d

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.callRemote("getMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getMirrors", machines)
        return d

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.callRemote("getFallbackMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirror", machine)
        return d

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.callRemote("getFallbackMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirrors", machines)
        return d

    def getApiPackage(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        uuid = machine['uuid']
        try:
            entity_uuid = ComputerLocationManager().getMachinesLocations([uuid])[uuid]['uuid']
            parent_entities = [entity_uuid] + ComputerLocationManager().getLocationParentPath(entity_uuid)
            url = ''
            entity_uuid = '' 
            db = ImagingDatabase()
            for _uuid in parent_entities:
                urlsearch = db.getEntityUrl(_uuid)
                if urlsearch is not None:
                    entity_uuid = _uuid
                    url = urlsearch
                    break;
            Entity_Name = ComputerLocationManager().getLocationName(entity_uuid)
            machine ['Entity_Name']= Entity_Name
            serverinfo = db.getImagingServerInfo(entity_uuid)
            machine ['entity_uuid']= entity_uuid
            machine ['server']= urlparse(url).hostname
            machine ['servernane']=serverinfo.name
        except:
            logging.getLogger().error("Cannot get Entity for this machine UUID (%s)" % uuid)

        d = self.callRemote("getApiPackage", machine)
        d.addErrback(self.onError, "MirrorApi:getApiPackage", machine)
        return d

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.callRemote("getApiPackages", machines)
        d.addErrback(self.onError, "MirrorApi:getApiPackages", machines)
        return d

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

