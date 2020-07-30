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
    ret['Printer name'] = ['list', getAllNamePrinters]
    ret['Printer serial'] = ['list', getAllSerialPrinters]
    ret['Peripheral name'] = ['list', getAllNamePeripherals]
    ret['Peripheral serial'] = ['list', getAllSerialPeripherals]
    ret['Owner of the machine'] = ['list', getAllOwnerMachine]
    ret['User location'] = ['list', getAllLocations1]
    ret['Last Logged User'] = ['list', getAllContacts]
    ret['Computer name'] = ['list', getAllHostnames]
    ret['Contact'] = ['list', getAllContacts]
    ret['Contact number'] = ['list', getAllContactNums]
    ret['Description'] = ['list', getAllComments]
    ret['System model'] = ['list', getAllModels]
    ret['System manufacturer'] = ['list', getAllManufacturers]
    ret['State'] = ['list', getAllStates]
    ret['System type'] = ['list', getAllTypes]
    ret['Inventory number'] = ['list', getAllInventoryNumbers]
    ret['Location'] = ['list', getAllLocations]
    ret['Operating system'] = ['list', getAllOs]
    ret['Service Pack'] = ['list', getAllOsSps]
    ret['Group'] = ['list', getAllGroups]
    #ret['Network'] = ['list', getAllNetworks]  # Disabled (TODO: discuss)
    ret['Installed software'] = ['list', getAllSoftwares, 3]
    ret['Installed software (specific version)'] = ['double',
                                                    getAllSoftwaresAndVersions,
                                                    3,
                                                    2]
    ret['Entity'] = ['list', getAllEntities]
    ret['Vendors'] = ['list', getAllSoftwareVendors]
    ret['Software versions'] = ['list', getAllSoftwareVersions]
    ret['Register key'] = ['list', getAllRegistryKey]
    ret['Register key value'] = ['double',
                                getRegisterKeyValue,
                                3,
                                2]
    ret['Online computer'] = [ 'bool' ]
    ret['OS Version'] = ['list', getAllOsVersions]
    ret['Architecture'] = ['list', getAllArchitectures]

    logging.getLogger().info('queryPossibilities %s' %
                             (str(ret)))
    return ret


def queryGroups():
    # Assign criterions to categories
    ret = []
    # Identification cat
    ret.append(['Identification',
                [['Computer name', 'Hostname of the computer'],
                 ['Description', 'Description of the computer'],
                 ['Inventory number', 'Your internal inventory number'],
                 ['Group', 'GLPI Group']
                 ]])
    """
    # If we want to add printers, everything is already done.
    Currently all printers are searched through peripherals

    ret.append(['Printers',
                [['Printer name', 'Name printer'],
                 ['Printer serial', 'serial printer']
                 ]])
    """
    ret.append(['Peripherals',
                [['Peripheral name', 'Peripheral name'],
                 ['Peripheral serial', 'Peripheral serial']
                 ]])

    # Hardware cat
    ret.append(['Hardware',
                [['System type', 'Laptop, Desktop, Rack Mount Chassis ...'],
                 ['System manufacturer', 'Dell, HP, Apple ...'],
                 ['System model',
                  'Latitude E6420, ProLiant DL120, MacBookAir5,2 ...']]])

    ret.append(['user',
                [['Owner of the machine', 'user name ...'],
                 ['Last Logged User', 'Last user of the machine'],
                 ['User location', 'Computer belonging to the user']]])
    # Contact
    #ret['Contact'] =        [ \
    #                            ['Contact',''], \
    #                            ['Contact number',''] \
    #                        ]
    #Zone

    ret.append(['Location',
                [['Location',
                  'Third Floor, Room 401, Headquarters building ... (user defined)'],
                ['State',
                 'In Production, Under Maintenance, Decommissioned ... (user defined)'],
                ['Entity',
                 'Organizational structure (automatic assignment)']]])
    # Software
    ret.append(['Software',
                [['Operating system',
                  'Microsoft Windows 7, Debian GNU/Linux 7.1 ...'],
                 ['Installed software',
                  'Mozilla Firefox, LibreOffice, Microsoft Office 2003 ...'],
                 ['Installed software (specific version)',
                  'Two-step query: Mozilla Firefox -> 23.0.1, LibreOffice -> 4.0.4 ...'],
                 ['OS Version',
                  '(Windows 10 1803, Debian stretch (9), ...)'],
                 ['Architecture',
                  '(32-bit, 64-bit)']
                 ]])
    # REGISTER
    ret.append(['Register',
                [['Register key',
                  'Microsoft Windows keys registers'],
                ['Register key value',
                  'Microsoft Windows keys registers value']]])
    #PRESENCE XMPP
    ret.append(['Presence',
                [['Online computer', 'Presence of the machine Yes/No']
                 ]])
    return ret


def extendedPossibilities():
    """
    GLPI plugin has no extended possibilities
    """
    return {}


def query(ctx, criterion, value):
    machines = []
    if criterion == 'OS' or criterion == 'Operating system':
        machines = [x.name for x in Glpi().getMachineByOs(ctx, value)]
    elif criterion == 'ENTITY' or criterion == 'Entity':
        machines = [x.name for x in Glpi().getMachineByEntity(ctx, value)]
    elif criterion == 'SOFTWARE' or criterion == 'Installed software':
        machines = [x.name for x in Glpi().getMachineBySoftware(ctx, value)]
    elif criterion == 'Installed software (specific version)':
        machines = [x.name for x in
                    Glpi().getMachineBySoftwareAndVersion(ctx, value)]
    elif criterion == 'Computer name':
        machines = [x.name for x in Glpi().getMachineByHostname(ctx, value)]
    elif criterion == 'Contact':
        machines = [x.name for x in Glpi().getMachineByContact(ctx, value)]
    elif criterion == 'Contact number':
        machines = [x.name for x in Glpi().getMachineByContactNum(ctx, value)]
    elif criterion == 'Description':
        machines = [x.name for x in Glpi().getMachineByComment(ctx, value)]
    elif criterion == 'System model':
        machines = [x.name for x in Glpi().getMachineByModel(ctx, value)]
    elif criterion == 'System manufacturer':
        machines = [x.name for x in
                    Glpi().getMachineByManufacturer(ctx, value)]
    elif criterion == 'State':
        machines = [x.name for x in Glpi().getMachineByState(ctx, value)]
    elif criterion == 'System type':
        machines = [x.name for x in Glpi().getMachineByType(ctx, value)]
    elif criterion == 'Inventory number':
        machines = [x.name for x in
                    Glpi().getMachineByInventoryNumber(ctx, value)]
    elif criterion == 'Location':
        machines = [x.name for x in Glpi().getMachineByLocation(ctx, value)]
    elif criterion == 'Service Pack':
        machines = [x.name for x in Glpi().getMachineByOsSp(ctx, value)]
    elif criterion == 'Group':
        machines = [x.name for x in Glpi().getMachineByGroup(ctx, value)]
    elif criterion == 'Network':
        machines = [x.name for x in Glpi().getMachineByNetwork(ctx, value)]
    elif criterion == "OS Version":
        machines = [x.name for x in Glpi().getMachineByOsVersion(ctx, value)]
    elif criterion == "Architecture":
        machines = [x.name for x in Glpi().getMachineByArchitecure(ctx, value)]
    elif criterion == "Printer name":
        machines = [x.name for x in Glpi().getMachineByPrinter(ctx, value)]
    elif criterion == "Printer serial":
        machines = [x.name for x in Glpi().getMachineByPrinterserial(ctx, value)]
    elif criterion == "Peripheral name":
        machines = [x.name for x in Glpi().getMachineByPeripheral(ctx, value)]
    elif criterion == "Peripheral serial":
        machines = [x.name for x in Glpi().getMachineByPeripheralserial(ctx, value)]
    #elif criterion == '':
    #    machines = map(lambda x: x.name, Glpi().getMachineBy(ctx, value))
    return [machines, True]


def getAllOs(ctx, value=''):
    return unique([x.name for x in Glpi().getAllOs(ctx, value)])


def getAllEntities(ctx, value=''):
    return [x.name for x in Glpi().getAllEntities(ctx, value)]


def getAllSoftwares(ctx, softname='', vendor=None):
    def replace_splat(param):
        if '*' in param:
            return param.replace('*', '%')
        return param

    def check_param(param):
        if param == '' or param == '*' or param == '%':
            return None
        return replace_splat(param)

    software = check_param(softname)
    if vendor is not None:
        vendor = check_param(vendor)
    if software is None:
        software = '%'
    return [x[0] for x in Glpi().getAllSoftwares(ctx,
                                             softname=softname,
                                             vendor=vendor,
                                             limit=20)]

def getRegisterKeyValue(ctx, keyregister="", value=None):
    if value is None:
        return getAllRegistryKey(ctx, keyregister)
    else:
        return getAllRegistryKeyValue(ctx, keyregister, value)

def getAllRegistryKeyValue(ctx, keyregister, value):
    return [x[0] for x in Glpi().getAllRegistryKeyValue(ctx, keyregister, value)]

def getAllSoftwaresAndVersions(ctx, softname="", version=None):
    if version is None:
        return [x[0] for x in Glpi().getAllSoftwares(ctx, softname=softname)]
    else:
        return [x[0] for x in Glpi().getAllVersion4Software(ctx, softname, version)]

def getAllHostnames(ctx, value=''):
    return unique([x.name for x in Glpi().getAllHostnames(ctx, value)])


def getAllContacts(ctx, value=''):
    return unique([x.contact for x in Glpi().getAllContacts(ctx, value)])


def getAllContactNums(ctx, value=''):
    return unique([x.contact_num for x in
                   Glpi().getAllContactNums(ctx, value)])

def getAllComments(ctx, value=''):
    if Glpi().glpi_version[:3] == '0.8':
        return unique([x.comment for x in Glpi().getAllComments(ctx, value)])
    else: # glpi 7
        return unique([x.comments for x in Glpi().getAllComments(ctx, value)])


def getAllModels(ctx, value=''):
    return unique([x.name for x in Glpi().getAllModels(ctx, value)])


def getAllTypes(ctx, value=''):
    return unique([x.name for x in Glpi().getAllTypes(ctx, value)])


def getAllInventoryNumbers(ctx, value=''):
    return unique([x.name for x in Glpi().getAllInventoryNumbers(ctx, value)])


def getAllManufacturers(ctx, value=''):
    return unique([x.name for x in Glpi().getAllManufacturers(ctx, value)])


def getAllStates(ctx, value=''):
    return unique([x.name for x in Glpi().getAllStates(ctx, value)])


def getAllLocations(ctx, value=''):
    return unique([x.completename for x in Glpi().getAllLocations(ctx, value)])

def getAllLocations1(ctx, value=''):
    return unique([x.completename for x in Glpi().getAllLocations1(ctx, value)])

def getAllOsSps(ctx, value=''):
    return unique([x.name for x in Glpi().getAllOsSps(ctx, value)])

def getAllGroups(ctx, value=''):
    return unique([x.name for x in Glpi().getAllGroups(ctx, value)])

def getAllNetworks(ctx, value=''):
    return unique([x.name for x in Glpi().getAllNetworks(ctx, value)])

def getAllSoftwareVendors(ctx, value=''):
    res = Glpi().getAllSoftwareVendors(ctx, value)
    return unique([x.name for x in res])

def getAllSoftwareVersions(ctx, value='', software=None):
    res = Glpi().getAllSoftwareVersions(ctx, filt=value, software=software)
    return unique([x.name for x in res])

def getAllRegistryKey(ctx, value=''):
    res = Glpi().getAllRegistryKey(ctx, value)
    return unique([x.name for x in res])

def getAllOwnerMachine(ctx, value=''):
    res = Glpi().getAllOwnerMachine(ctx, filt=value)
    return unique([x.name for x in res])

def getAllLoggedUser(ctx, value=''):
    return unique([x.contact for x in Glpi().getAllContacts(ctx, value)])

def getAllOsVersions(ctx, value=""):
    return unique([element.name for element in Glpi().getAllOsVersions(ctx, filt=value)])

def getAllArchitectures(ctx, value=""):
    return unique([element.name for element in Glpi().getAllArchitectures(ctx, filt=value)])


def getAllNamePrinters(ctx, value=""):
    return unique([element.name for element in Glpi().getAllNamePrinters(ctx, filt=value)])


def getAllSerialPrinters(ctx, value=""):
    return unique([element.serial for element in Glpi().getAllSerialPrinters(ctx, filt=value)])


def getAllNamePeripherals(ctx, value=""):
    return unique([element.name for element in Glpi().getAllNamePeripherals(ctx, filt=value)])


def getAllSerialPeripherals(ctx, value=""):
    return unique([element.serial for element in Glpi().getAllSerialPeripherals(ctx, filt=value)])
