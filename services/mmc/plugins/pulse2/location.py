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

import logging
from mmc.support.mmctools import Singleton

class ComputerLocationManager(Singleton):
    components = {}
    main = 'glpi'

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting computer location manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug("Registering computer location manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        return True

    def getUserProfile(self, userid):
        klass = self.components[self.main]
        return klass().getUserProfile(userid)

    def getUserLocations(self, userid):
        klass = self.components[self.main]
        return klass().getUserLocations(userid)

    def getMachinesInLocation(self, location, a_profile = []):
        klass = self.components[self.main]
        return klass().getMachinesInLocation(location, a_profile)
        
    def getLocationsForMachine(self, machine_uuid, a_profile = []):
        klass = self.components[self.main]
        return klass().getLocationsForMachine(machine_uuid, a_profile)
        
    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        klass = self.components[self.main]
        return klass().doesUserHaveAccessToMachine(userid, machine_uuid)

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True):
        klass = self.components[self.main]
        return klass().doesUserHaveAccessToMachines(userid, machine_uuid, all)

class ComputerLocationI:
    def getUserProfile(self, userid):
        """ return the linked profiles for one user """
        pass

    def getUserLocations(self, userid):
        """ return the linked locations for one user """
        pass

    def getMachinesInLocation(self, location, a_profile = []): # TODO implement and use in glpi module
        """ should return the machines that are in the specified location with the good profiles (or any) """
        pass
    
    def getLocationsForMachine(self, machine_uuid, a_profile = []): # TODO implement and use in glpi module
        """ should return the locations in which this machine is """
        pass

    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        """ should return true if the machine is accessible for this user """
        pass

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True):
        """ should return true if more than one or all machines are accessible for this user """
        pass

