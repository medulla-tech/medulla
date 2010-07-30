#
# (c) 2008 Mandriva, http://www.mandriva.com/
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
Glpi querymanager
give informations to the dyngroup plugin to be able to build dyngroups
on glpi informations
"""

import logging
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.config import GlpiQueryManagerConfig

from pulse2.utils import unique

def activate():
    conf = GlpiQueryManagerConfig("glpi")
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
    ret['Version'] = ['double', getAllSoftwaresAndVersions, 3, 2]

#    ret['OS'] = ['list', getAllOs]
#    ret['ENTITY'] = ['list', getAllEntities]
#    ret['SOFTWARE'] = ['list', getAllSoftwares, 3]
    logging.getLogger().info('queryPossibilities %s'%(str(ret)))
    return ret

def extendedPossibilities():
    """
    GLPI plugin has no extended possibilities
    """
    return {}

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
    return unique(map(lambda x:x.name, Glpi().getAllOs(ctx, value)))

def getAllEntities(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllEntities(ctx, value)))

def getAllSoftwares(ctx, value = ''):
    ret = unique(map(lambda x:x.name, Glpi().getAllSoftwares(ctx, value)))
    ret.sort()
    return ret

def getAllSoftwaresAndVersions(ctx, softname = "", version = None):
    ret = []
    if version == None:
        if Glpi().glpi_chosen_version().find('0.8') == 0: # glpi in 0.8
            ret = unique(map(lambda x:x.name, Glpi().getAllSoftwares(ctx, softname)))
        else:
            ret = unique(map(lambda x:x.name, Glpi().getAllSoftwares(ctx, softname)))
    else:
        if Glpi().glpi_chosen_version().find('0.8') == 0: # glpi in 0.8
            ret = unique(map(lambda x:x.name, Glpi().getAllVersion4Software(ctx, softname, version)))
        else:
            if Glpi().glpi_version_new():
                ret = unique(map(lambda x:x.name, Glpi().getAllVersion4Software(ctx, softname, version)))
            else:
                ret = unique(map(lambda x:x.version, Glpi().getAllVersion4Software(ctx, softname, version)))
    ret.sort()
    return ret

def getAllHostnames(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllHostnames(ctx, value)))

def getAllContacts(ctx, value = ''):
    return unique(map(lambda x:x.contact, Glpi().getAllContacts(ctx, value)))

def getAllContactNums(ctx, value = ''):
    return unique(map(lambda x:x.contact_num, Glpi().getAllContactNums(ctx, value)))

def getAllComments(ctx, value = ''):
    if Glpi().glpi_chosen_version().find('0.8') == 0:
        return unique(map(lambda x:x.comment, Glpi().getAllComments(ctx, value)))
    else:
        return unique(map(lambda x:x.comments, Glpi().getAllComments(ctx, value)))

def getAllModels(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllModels(ctx, value)))

def getAllLocations(ctx, value = ''):
    return unique(map(lambda x:x.completename, Glpi().getAllLocations(ctx, value)))

def getAllOsSps(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllOsSps(ctx, value)))

def getAllGroups(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllGroups(ctx, value)))

def getAllNetworks(ctx, value = ''):
    return unique(map(lambda x:x.name, Glpi().getAllNetworks(ctx, value)))

