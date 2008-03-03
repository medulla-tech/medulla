import os
import re
import logging
from mmc.support.config import PluginConfig
from mmc.plugins.glpi.database import Glpi
import mmc

from ConfigParser import NoOptionError

def activate():
    conf = GlpiQueryManagerConfig("glpi", None)
    if not mmc.plugins.glpi.activate():
        return False

    Glpi().activate()
    return conf.activate

def queryPossibilities():
    ret = {}
    ret['OS'] = ['list', getAllOs]
    ret['ENTITY'] = ['list', getAllEntities]
    ret['SOFTWARE'] = ['list', getAllSoftwares, 3]
    return ret

def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []
    if criterion == 'OS':
        machines = map(lambda x: x.name, Glpi().getMachineByOs(ctx, value))
    elif criterion == 'ENTITY':
        machines = map(lambda x: x.name, Glpi().getMachineByEntity(ctx, value))
    elif criterion == 'SOFTWARE':
        machines = map(lambda x: x.name, Glpi().getMachineBySoftware(ctx, value))
    return [machines, True]

class GlpiQueryManagerConfig(PluginConfig):
    def readConf(self):
        PluginConfig.readConf(self)
        self.activate = False
        try:
            self.activate = self.getboolean("querymanager", "activate")
        except NoOptionError:
            self.activate = False

def getAllOs(value = ''):
    return map(lambda x:x.name, Glpi().getAllOs(value))

def getAllEntities(value = ''):
    return map(lambda x:x.name, Glpi().getAllEntities(value))

def getAllSoftwares(value = ''):
    return map(lambda x:x.name, Glpi().getAllSoftwares(value))
    
