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
    ret['Nom'] = ['list', getAllHostnames]
    ret['Contact'] = ['list', getAllContacts]
    ret['Numero du contact'] = ['list', getAllContactNums]
    ret['Comments'] = ['list', getAllComments]
    ret['Modele'] = ['list', getAllModels]
    ret['Lieu'] = ['list', getAllLocations]
    ret['OS'] = ['list', getAllOs]
    ret['ServicePack'] = ['list', getAllOsSps]
    ret['Groupe'] = ['list', getAllGroups]
    ret['Reseau'] = ['list', getAllNetworks]
    ret['Logiciel'] = ['list', getAllSoftwares, 3]
    ret['Version'] = ['double', getAllSoftwaresAndVersions]
    
#    ret['OS'] = ['list', getAllOs]
#    ret['ENTITY'] = ['list', getAllEntities]
#    ret['SOFTWARE'] = ['list', getAllSoftwares, 3]
    logging.getLogger().info('queryPossibilities %s'%(str(ret)))
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
    elif criterion == 'SOFTWARE' or criterion == 'Logiciel':
        machines = map(lambda x: x.name, Glpi().getMachineBySoftware(ctx, value))
    elif criterion == 'Version':
        machines = map(lambda x: x.name, Glpi().getMachineBySoftwareAndVersion(ctx, value))
    elif criterion == 'Nom':
        machines = map(lambda x: x.name, Glpi().getMachineByHostname(ctx, value))
    elif criterion == 'Contact':
        machines = map(lambda x: x.name, Glpi().getMachineByContact(ctx, value))
    elif criterion == 'Numero du contact':
        machines = map(lambda x: x.name, Glpi().getMachineByContactNum(ctx, value))
    elif criterion == 'Comments':
        machines = map(lambda x: x.name, Glpi().getMachineByComment(ctx, value))
    elif criterion == 'Modele':
        machines = map(lambda x: x.name, Glpi().getMachineByModel(ctx, value))
    elif criterion == 'Lieu':
        machines = map(lambda x: x.name, Glpi().getMachineByLocation(ctx, value))
    elif criterion == 'ServicePack':
        machines = map(lambda x: x.name, Glpi().getMachineByOsSp(ctx, value))
    elif criterion == 'Groupe':
        machines = map(lambda x: x.name, Glpi().getMachineByGroup(ctx, value))
    elif criterion == 'Reseau':
        machines = map(lambda x: x.name, Glpi().getMachineByNetwork(ctx, value))
    #elif criterion == '':
    #    machines = map(lambda x: x.name, Glpi().getMachineBy(ctx, value))
    return [machines, True]

def getAllOs(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllOs(ctx, value))

def getAllEntities(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllEntities(ctx, value))

def getAllSoftwares(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllSoftwares(ctx, value))

def getAllSoftwaresAndVersions(ctx, value = ""):
    return map(lambda x:x.name, Glpi().getAllSoftwares(ctx, value))
    
def getAllHostnames(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllHostnames(ctx, value))

def getAllContacts(ctx, value = ''):
    return map(lambda x:x.contact, Glpi().getAllContacts(ctx, value))

def getAllContactNums(ctx, value = ''):
    return map(lambda x:x.contact_num, Glpi().getAllContactNums(ctx, value))

def getAllComments(ctx, value = ''):
    return map(lambda x:x.comments, Glpi().getAllComments(ctx, value))
    
def getAllModels(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllModels(ctx, value))
    
def getAllLocations(ctx, value = ''):
    return map(lambda x:x.completename, Glpi().getAllLocations(ctx, value))
    
def getAllOsSps(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllOsSps(ctx, value))
    
def getAllGroups(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllGroups(ctx, value))
    
def getAllNetworks(ctx, value = ''):
    return map(lambda x:x.name, Glpi().getAllNetworks(ctx, value))
    
