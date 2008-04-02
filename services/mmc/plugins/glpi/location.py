import logging
from mmc.plugins.pulse2.location import ComputerLocationI
from mmc.plugins.glpi.database import Glpi

class GlpiLocation(ComputerLocationI):
    def getUserProfile(self, userid):
        glpi = Glpi()
        glpi.activate()
        return glpi.getUserProfile(userid)

    def getUserLocations(self, userid):
        glpi = Glpi()
        glpi.activate()
        return glpi.getUserLocations(userid)

    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        glpi = Glpi()
        glpi.activate()
        return glpi.doesUserHaveAccessToMachine(userid, machine_uuid)

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True):
        glpi = Glpi()
        glpi.activate()
        return glpi.doesUserHaveAccessToMachines(userid, machine_uuid, all)

