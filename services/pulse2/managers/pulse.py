# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
The pulse2 manager, it give access to eveything that is stocked in the pulse2 database
"""
import logging
from pulse2.utils import Singleton


class Pulse2Manager(Singleton):
    components = {}
    main = "pulse2"

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting pulse2 manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug("Registering pulse2 manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        return True

    ###########################################################################
    def getPackageServerEntityByPackageServer(self, ps_uuid):
        klass = self.components[self.main]
        return klass().getPackageServerEntityByPackageServer(ps_uuid)

    def getPackageServerEntityByEntity(self, e_uuid):
        klass = self.components[self.main]
        return klass().getPackageServerEntityByEntity(e_uuid)

    def getPackageServerEntityByEntities(self, e_uuids):
        klass = self.components[self.main]
        return klass().getPackageServerEntityByEntities(e_uuids)

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        klass = self.components[self.main]
        return klass().getPackageServerEntity(ps_uuid, e_uuid)

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        ret = True
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, "putPackageServerEntity"):
                r = klass().putPackageServerEntity(ps_uuid, e_uuid)
                ret = ret and r
        return ret

    def delPackageServerEntity(self, e_uuid):
        klass = self.components[self.main]
        return klass().delPackageServerEntity(e_uuid)


class Pulse2I:
    def getPackageServerEntityByPackageServer(self, ps_uuid):
        """
        get the PackageServerEntity object as a dict from the main Pulse2Manager
        """
        pass

    def getPackageServerEntityByEntity(self, e_uuid):
        pass

    def getPackageServerEntityByEntities(self, e_uuids):
        pass

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        """
        get the PackageServerEntity object as a dict from the main Pulse2Manager
        """
        pass

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        """
        put the PackageServerEntity object in all the Pulse2Manager
        """
        pass
