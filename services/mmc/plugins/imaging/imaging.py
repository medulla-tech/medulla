# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Imaging implementation of the imaging in profile manager interface
"""

from pulse2.managers.imaging import ComputerImagingI
from pulse2.managers.location import ComputerLocationManager
from pulse2.database.imaging import ImagingDatabase


class ComputerImagingImaging(ComputerImagingI):
    def isImagingInProfilePossible(self):
        "check if the root entity is registered"
        return True
        # TODO getRootLocationUUID no longer exists!
        # root_entity_uuid = ComputerLocationManager().getRootLocationUUID()
        # ret = ImagingDatabase().doesLocationHasImagingServer(root_entity_uuid)
        # return ret

    def getAllImagingServers(self, user_id, is_associated):
        """
        get all the imaging server that this user can access
        """
        locations = ComputerLocationManager().getUserLocations(user_id)
        locations = [l["uuid"] for l in locations]
        r = ImagingDatabase().getEntitiesImagingServer(locations, is_associated)
        ret = {}
        for ims, loc_uuid in r:
            ims = ims.toH()
            ims["entity_uuid"] = loc_uuid
            ret[ims["imaging_uuid"]] = ims
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

    def isChildOfImagingServer(self, loc_uuid, main_imaging_server_uuid):
        """
        Check if loc_uuid is child of main_imaging_server_uuid
        """
        parents = ComputerLocationManager().getLocationParentPath(loc_uuid)
        # Check if loc_uuid is child of main_imaging_server_uuid
        if main_imaging_server_uuid in parents:
            # Cool ! Now check if loc_uuid has not his own imaging server
            if not ImagingDatabase().doesLocationHasImagingServer(loc_uuid):
                return True
        return False
