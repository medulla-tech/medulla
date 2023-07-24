# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText:2007-2014 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Glpi implementation of the ComputerLocationI Interface
Provide functions to get all user profiles and user locations informations
"""

import logging
from pulse2.managers.location import ComputerLocationI
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.utilities import complete_ctx


class GlpiLocation(ComputerLocationI):
    def init(self, config):
        self.logger = logging.getLogger()
        self.config = config
        return Glpi().activate()

    def getUserProfile(self, userid):
        return Glpi().getUserProfile(userid)

    def getUserParentLocations(self, userid):
        return [l.toH() for l in Glpi().getUserParentLocations(userid)]

    def getUserLocations(self, userid):
        return [l.toH() for l in Glpi().getUserLocations(userid)]

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        if not hasattr(ctx, "locations"):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachine(ctx, machine_uuid)

    def doesUserHaveAccessToMachines(self, ctx, machine_uuid, all=True):
        if not hasattr(ctx, "locations"):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachines(ctx, machine_uuid, all)

    def displayLocalisationBar(self):
        return self.config.displayLocalisationBar

    def getLocationsCount(self):
        return Glpi().getLocationsCount()

    def getUsersInSameLocations(self, userid):
        return Glpi().getUsersInSameLocations(userid)

    def getMachinesLocations(self, machine_uuids):
        return Glpi().getMachinesLocations(machine_uuids)

    def getLocationsFromPathString(self, location_path):
        return Glpi().getLocationsFromPathString(location_path)

    def getLocationParentPath(self, loc_uuid):
        return Glpi().getLocationParentPath(loc_uuid)

    def getLocationName(self, loc_uuid):
        return Glpi().getLocationName(loc_uuid)
