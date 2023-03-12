# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Computer Location manager
provide methods to work with location association with computers
"""

import logging
from pulse2.utils import Singleton


class ComputerLocationManager(Singleton):
    components = {}
    main = None

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name=None):
        if not name:
            if len(self.components) == 1:
                name = list(self.components.keys())[0]
            else:
                raise Exception(
                    "Can't auto-select a computer location manager, please configure one in pulse2.ini."
                )
        self.logger.info("Selecting computer location manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug(
            "Registering computer location manager %s / %s" % (name, str(klass))
        )
        self.components[name] = klass

    def validate(self):
        return True

    def displayLocalisationBar(self):
        if self.main in self.components:
            klass = self.components[self.main]
            ret = klass().displayLocalisationBar()
        else:
            ret = False
        return ret

    def getUserProfile(self, userid):
        try:
            klass = self.components[self.main]
            return klass().getUserProfile(userid)
        except KeyError:
            return None

    def getUserLocations(self, userid):
        try:
            klass = self.components[self.main]
            return klass().getUserLocations(userid)
        except KeyError:
            return None

    def getUsersInSameLocations(self, userid):
        try:
            klass = self.components[self.main]
            return klass().getUsersInSameLocations(userid)
        except KeyError:
            return None

    def getMachinesInLocation(self, location, a_profile=[]):
        # Mutable list a_profile used as default argument to a method or
        # function
        try:
            klass = self.components[self.main]
            return klass().getMachinesInLocation(location, a_profile)
        except KeyError:
            return None

    def getLocationsForMachine(self, machine_uuid, a_profile=[]):
        # Mutable list a_profile used as default argument to a method or
        # function
        try:
            klass = self.components[self.main]
            return klass().getLocationsForMachine(machine_uuid, a_profile)
        except KeyError:
            return None

    def getLocationsCount(self):
        try:
            klass = self.components[self.main]
            return klass().getLocationsCount()
        except KeyError:
            return None

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        try:
            klass = self.components[self.main]
            return klass().doesUserHaveAccessToMachine(ctx, machine_uuid)
        except KeyError:
            return True

    def doesUserHaveAccessToMachines(self, ctx, machine_uuid, all=True):
        try:
            klass = self.components[self.main]
            return klass().doesUserHaveAccessToMachines(ctx, machine_uuid, all)
        except KeyError:
            return True

    def getMachinesLocations(self, machine_uuids):
        try:
            klass = self.components[self.main]
            return klass().getMachinesLocations(machine_uuids)
        except KeyError:
            return True

    def getLocationsFromPathString(self, location_path):
        try:
            klass = self.components[self.main]
            return klass().getLocationsFromPathString(location_path)
        except KeyError:
            return True

    def getLocationParentPath(self, loc_uuid):
        try:
            klass = self.components[self.main]
            return klass().getLocationParentPath(loc_uuid)
        except KeyError:
            return True

    def getLocationName(self, loc_uuid):
        try:
            klass = self.components[self.main]
            return klass().getLocationName(loc_uuid)
        except KeyError:
            return None


class ComputerLocationI(Singleton):
    def displayLocalisationBar(self):
        """return True if the module want to display the location bar in computers lists"""
        return False

    def getUserProfile(self, userid):
        """return the linked profiles for one user"""
        pass

    def getUserLocations(self, userid):
        """return the linked locations for one user"""
        pass

    # TODO implement and use in glpi module
    def getMachinesInLocation(self, location, a_profile=[]):
        """should return the machines that are in the specified location with the good profiles (or any)"""
        # Mutable list a_profile used as default argument to a method or
        # function
        pass

    # TODO implement and use in glpi module
    def getLocationsForMachine(self, machine_uuid, a_profile=[]):
        """should return the locations in which this machine is"""
        # Mutable list a_profile used as default argument to a method or
        # function
        pass

    def getLocationsCount(self):
        """Returns the total count of locations"""
        pass

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        """should return true if the machine is accessible for this user"""
        pass

    def doesUserHaveAccessToMachines(self, ctx, machine_uuid, all=True):
        """should return true if more than one or all machines are accessible for this user"""
        pass

    def getMachinesLocations(self, machine_uuids):
        """should return the location in which the machines are as a dict {machine_uuid:location}"""
        pass

    def getLocationsFromPathString(self, location_path):
        """should return the locations that correspond to that path"""
        pass

    def getLocationParentPath(self, loc_uuid):
        """return an array containing all the parent uuids of this location"""
        pass

    def getLocationName(self, loc_uuid):
        """return a string of the location name"""
        pass
