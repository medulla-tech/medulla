import os
import re
import logging
from mmc.support.config import PluginConfig
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.config import GlpiQueryManagerConfig
import mmc

from ConfigParser import NoOptionError

def activate():
    conf = GlpiQueryManagerConfig("glpi")
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

def getAllOs(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllOs(value))

def getAllEntities(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllEntities(value))

def getAllSoftwares(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllSoftwares(value))
    
