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
The pulse2 manager, it give access to eveything that is stocked in the pulse2 database
"""
import logging
from pulse2.utils import Singleton

class Pulse2Manager(Singleton):
    components = {}
    main = 'pulse2'

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
        print "putPackageServerEntity !!!!"
        ret = True
        for mod in self.components:
            print "mod %s"%mod
            klass = self.components[mod]
            if hasattr(klass, 'putPackageServerEntity'):
                print "ok"
                r = klass().putPackageServerEntity(ps_uuid, e_uuid)
                ret = ret and r
        return ret

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

