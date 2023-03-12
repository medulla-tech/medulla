# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Computer Imaging in Profile manager
provide methods to work with profile in the imaging module
"""

import logging
from pulse2.utils import Singleton


class ComputerImagingManager(Singleton):
    components = {}
    main = "imaging"

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting imaging computer profile manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug(
            "Registering imaging computer profile manager %s / %s" % (name, str(klass))
        )
        self.components[name] = klass

    def validate(self):
        return True

    ##############################
    def isImagingInProfilePossible(self):
        "check in all the managers, if none of them have a isImagingInProfilePossible method, return False"
        ret = False
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, "isImagingInProfilePossible"):
                ret = True
                r = klass().isImagingInProfilePossible()
                if not r:
                    return False
        return ret

    def getAllImagingServers(self, user_id, associated):

        if self.main in self.components:
            klass = self.components[self.main]
            ret = klass().getAllImagingServers(user_id, associated)
        else:
            ret = False
        return ret

    def getImagingServerEntityUUID(self, imaging_uuid):
        klass = self.components[self.main]
        return klass().getImagingServerEntityUUID(imaging_uuid)

    def isChildOfImagingServer(self, loc_uuid, main_imaging_server_uuid):
        klass = self.components[self.main]
        return klass().isChildOfImagingServer(loc_uuid, main_imaging_server_uuid)


class ComputerImagingI:
    def isImagingInProfilePossible(self):
        """
        tell if the imaging action is displayed for the profiles
        """
        pass

    def getAllImagingServers(self, user_id, associated):
        """
        get all the imaging server that this user can access
        """
        pass

    def getImagingServerEntityUUID(self, imaging_uuid):
        """
        get an imaging server's entity uuid
        """
        pass
