import logging
from mmc.plugins.pulse2.location import ComputerLocationI
from mmc.plugins.glpi.database import Glpi

class GlpiLocation(ComputerLocationI):
    def init(self, config):
        self.logger = logging.getLogger()
        self.config = config
        Glpi().activate()
    
    def getUserProfile(self, userid):
        return Glpi().getUserProfile(userid)

    def getUserLocations(self, userid):
        return map(lambda l: l.toH(), Glpi().getUserLocations(userid))

    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        return Glpi().doesUserHaveAccessToMachine(userid, machine_uuid)

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True):
        return Glpi().doesUserHaveAccessToMachines(userid, machine_uuid, all)

    def displayLocalisationBar(self):
        return self.config.displayLocalisationBar


