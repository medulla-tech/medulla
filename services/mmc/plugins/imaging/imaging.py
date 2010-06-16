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
Imaging implementation of the imaging in profile manager interface
"""

from pulse2.managers.imaging import ComputerImagingI
from pulse2.managers.location import ComputerLocationManager
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import P2IT
import logging

class ComputerImagingImaging(ComputerImagingI):
    def isImagingInProfilePossible(self):
        " check if the root entity is registered "
        return True
        # TODO getRootLocationUUID no longer exists!
        #root_entity_uuid = ComputerLocationManager().getRootLocationUUID()
        #ret = ImagingDatabase().doesLocationHasImagingServer(root_entity_uuid)
        #return ret

    def getAllImagingServers(self, user_id):
        """
        get all the imaging server that this user can access
        """
        locations = ComputerLocationManager().getUserLocations(user_id)
        locations = map(lambda l:l['uuid'], locations)
        r = ImagingDatabase().getEntitiesImagingServer(locations)
        ret = {}
        for ims, loc_uuid in r:
            ims = ims.toH()
            ret[ims['imaging_uuid']] = ims
        return ret

    def getImagingServerEntityUUID(self, imaging_uuid):
        """
        get the imaging server's entity UUID
        """
        db = ImagingDatabase()
        ims = db.getImagingServerByUUID(imaging_uuid)
        en = db.getImagingServerEntity(ims.packageserver_uuid)
        if en != None:
            return en.uuid
        return None

    def computersUnregister(self, computers_UUID):
        """
        unregister all the computers from the list
        """
        db = ImagingDatabase()
        logger = logging.getLogger()

        # get the computers
        ret = db.isTargetRegister(computers_UUID, P2IT.ALL_COMPUTERS)
        if not ret[0]:
            for uuid in ret[1]:
                logger.info("%s is not registered, it can be unregister"%uuid)
                try:
                    computers_UUID.pop(computers_UUID.index(uuid))
                except ValueError, e:
                    pass

        # send a request to the pserver to unregister them
        # if they manage to unregister, unregister from the DB
            # remove the menu + menuitem
            # remove the computer
        # return the status of the whole thing


