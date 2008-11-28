import logging
from mmc.plugins.pulse2.location import ComputerLocationI
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.utilities import complete_ctx

class GlpiLocation(ComputerLocationI):
    def init(self, config):
        self.logger = logging.getLogger()
        self.config = config
        Glpi().activate()
    
    def getUserProfile(self, userid):
        return Glpi().getUserProfile(userid)

    def getUserLocations(self, userid):
        return map(lambda l: l.toH(), Glpi().getUserLocations(userid))

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        if not hasattr(ctx, 'locations'):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachine(ctx, machine_uuid)

    def doesUserHaveAccessToMachines(self, ctx, machine_uuid, all = True):
        if not hasattr(ctx, 'locations'):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachines(ctx, machine_uuid, all)

    def displayLocalisationBar(self):
        return self.config.displayLocalisationBar

    def getLocationsCount(self):
        return Glpi().getLocationsCount()

    def getUsersInSameLocations(self, userid):
        return Glpi().getUsersInSameLocations(userid)
