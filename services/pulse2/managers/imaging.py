# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
Computer Imaging in Profile manager
provide methods to work with profile in the imaging module
"""

import logging
from pulse2.utils import Singleton

class ComputerImagingManager(Singleton):
    components = {}
    main = 'imaging'

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting imaging computer profile manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug("Registering imaging computer profile manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        return True

    ##############################
    def isImagingInProfilePossible(self):
        " check in all the managers, if none of them have a isImagingInProfilePossible method, return False "
        ret = False
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'isImagingInProfilePossible'):
                ret = True
                r = klass().isImagingInProfilePossible()
                if not r:
                    return False
        return ret

    def getAllImagingServers(self, user_id):
        klass = self.components[self.main]
        return klass().getAllImagingServers(user_id)

    def getImagingServerEntityUUID(self, imaging_uuid):
        klass = self.components[self.main]
        return klass().getImagingServerEntityUUID(imaging_uuid)

    def computersUnregister(self, computers_UUID):
        "check in all the managers, if none of them have a computersUnregister method, return False "
        ret = False
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'computersUnregister'):
                ret = True
                r = klass().computersUnregister(computers_UUID)
                if not r:
                    return False
        return ret

class ComputerImagingI:
    def isImagingInProfilePossible(self):
        """
        tell if the imaging action is displayed for the profiles
        """
        pass

    def getAllImagingServers(self, user_id):
        """
        get all the imaging server that this user can access
        """
        pass

    def getImagingServerEntityUUID(self, imaging_uuid):
        """
        get an imaging server's entity uuid
        """
        pass


    def computersUnregister(self, computers_UUID):
        """
        unregister all the computers from the list
        """
        pass
