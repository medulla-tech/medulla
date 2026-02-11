# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MMC GLPI Backend plugin
It provide an API to access informations in the GLPI database.
"""

from mmc.support.mmctools import (
    xmlrpcCleanup,
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext,
    update_filter
)
from mmc.plugins.base import (with_xmpp_context,
                              with_optional_xmpp_context,
                              Contexte_XmlRpc_surcharge_info_Glpi)
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.base.provisioning import ProvisioningManager
from mmc.plugins.base.output import XLSGenerator
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.computers import GlpiComputers
from mmc.plugins.glpi.provisioning import GlpiProvisioner
from pulse2.managers.location import ComputerLocationManager
from mmc.plugins.glpi.location import GlpiLocation
from mmc.plugins.mobile import getHmdmDevicesOsCount #hmdm
import inspect

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

# health check
from mmc.plugins.glpi.health import scheduleCheckStatus
from configparser import ConfigParser

import logging
import os

APIVERSION = "0:0:0"
logger = logging.getLogger()

NOAUTHNEEDED = [
    "getMachineUUIDByMacAddress",
    "hasKnownOS",
]


def getApiVersion():
    return APIVERSION


def activate():
    config = GlpiConfig("glpi", None, "database")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin glpi: disabled by configuration.")
        return False

    if not GlpiLocation().init(config):  # does Glpi().activate()
        return False
    if not Glpi().db_check():
        return False

    ComputerManager().register("glpi", GlpiComputers)
    ProvisioningManager().register("glpi", GlpiProvisioner)
    if config.displayLocalisationBar:
        ComputerLocationManager().register("glpi", GlpiLocation)

    if config.check_db_enable:
        scheduleCheckStatus(config.check_db_interval)

    return True


class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s

class RpcProxy(RpcProxyI):

    @with_optional_xmpp_context
    def get_machines_list(self, start, end, filter, ctx=None):
        filter = update_filter(filter, ctx.get_session_info()['mondict']['liste_entities_user'])
        logger.debug("filter : %s " % filter)
        return xmlrpcCleanup(Glpi().get_machines_list(start, end, filter))


    @with_optional_xmpp_context
    def get_machines_list1(self, start, end, filter, ctx=None):
        filter = update_filter(filter, ctx.get_session_info()['mondict']['liste_entities_user'])
        logger.debug("filter : %s " % filter)
        return xmlrpcCleanup(Glpi().get_machines_list1(start, end, filter))

    @with_optional_xmpp_context
    def get_os_for_dashboard(self, ctx=None):
        entities = ctx.get_session_info()['mondict']['liste_entities_user']
        os_data = Glpi().get_os_for_dashboard(entities)
        os_data.extend(getHmdmDevicesOsCount()) #hmdm
        return xmlrpcCleanup(os_data)

    def getMachineNumberByState(self):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineNumberByState(ctx))

    def getMachineListByState(self, groupName):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineListByState(ctx, groupName))

    def getAntivirusStatus(self):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getAntivirusStatus(ctx))

    def getRestrictedComputersListLen(self):
        ctx = self.currentContext
        return Glpi().getRestrictedComputersListLen(ctx, {})

    def getMachineByOsLike(self, osname, count):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineByOsLike(ctx, osname, count))

    def getMachineListByAntivirusState(self, groupName):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineListByAntivirusState(ctx, groupName))

    def getMachineByHostnameAndMacs(self, hostname, macs):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineByHostnameAndMacs(ctx, hostname, macs))
    
    @with_optional_xmpp_context
    def get_devices_list(self, start, end, filter, ctx=None):
        #[HMDM]
        filter = update_filter(filter, ctx.get_session_info()['mondict']['liste_entities_user'])
        logger.debug("filter : %s " % filter)
        return xmlrpcCleanup(Glpi().get_devices_list(start, end, filter))

    @with_optional_xmpp_context
    def get_antiviruses_for_dashboard(self, ctx=None):
        entities = ctx.get_session_info()['mondict']['liste_entities_user']
        return xmlrpcCleanup(Glpi().get_antiviruses_for_dashboard(entities))

    @with_optional_xmpp_context
    def get_inventories_for_dashboard(self, ctx=None):
        entities = ctx.get_session_info()['mondict']['liste_entities_user']
        return xmlrpcCleanup(Glpi().get_inventories_for_dashboard(entities))


def getLicensesComputer(vendor, software, version):
    return getLicensesCount(vendor, software, version, 3)


def getLicensesCount(vendor, software, version, valcount=1):
    ctx = SecurityContext()
    ctx.userid = "root"

    def replace_splat(param):
        if "*" in param:
            return param.replace("*", "%")
        return param

    def check_param(param):
        if param == "" or param == "*" or param == "%":
            return None
        return replace_splat(param)

    software = check_param(software)
    vendor = check_param(vendor)
    version = check_param(version)
    if software is None:
        software = "%"
    rr = xmlrpcCleanup(
        Glpi().getAllSoftwaresImproved(
            ctx, software, vendor=vendor, version=version, count=valcount
        )
    )
    return rr


def getLastMachineInventoryFull(uuid):
    return xmlrpcCleanup(Glpi().getLastMachineInventoryFull(uuid))


def getdbreadonly():
    config = GlpiConfig("glpi")
    return xmlrpcCleanup(config.dbreadonly)


def inventoryExists(uuid):
    return xmlrpcCleanup(Glpi().inventoryExists(uuid))


def getReport(uuid, lang):
    xsl = XLSGenerator("/var/tmp/report-" + uuid + ".xls", lang)
    xsl.get_summary_sheet(getLastMachineInventoryPart(uuid, "Summary"))
    xsl.get_hardware_sheet(
        getLastMachineInventoryPart(uuid, "Processors"),
        getLastMachineInventoryPart(uuid, "Controllers"),
        getLastMachineInventoryPart(uuid, "GraphicCards"),
        getLastMachineInventoryPart(uuid, "SoundCards"),
    )
    xsl.get_network_sheet(getLastMachineInventoryPart(uuid, "Network"))
    xsl.get_storage_sheet(getLastMachineInventoryPart(uuid, "Storage"))
    xsl.get_software_sheet(
        getLastMachineInventoryPart(
            uuid, "Softwares", 0, -1, None, {"hide_win_updates": True}
        )
    )
    xsl.save()
    return xmlrpcCleanup(xsl.path)


def getMachineInfoImaging(uuid):
    return xmlrpcCleanup(Glpi().getMachineInfoImaging(uuid))


def getLastMachineInventoryPart(
    uuid, part, minbound=0, maxbound=-1, filt=None, options={}
):
    return xmlrpcCleanup(
        Glpi().getLastMachineInventoryPart(
            uuid, part, minbound, maxbound, filt, options
        )
    )


def countLastMachineInventoryPart(uuid, part, filt=None, options={}):
    return xmlrpcCleanup(
        Glpi().countLastMachineInventoryPart(uuid, part, filt, options)
    )


def getMachineMac(uuid):
    return xmlrpcCleanup(Glpi().getMachineMac(uuid))


def getMachineIp(uuid):
    return xmlrpcCleanup(Glpi().getMachineIp(uuid))


def setGlpiEditableValue(uuid, name, value):
    return xmlrpcCleanup(Glpi().setGlpiEditableValue(uuid, name, value))


# TODO
def getInventoryEM(part):
    return []


def getGlpiMachineUri():
    return Glpi().config.glpi_computer_uri


def glpi_version():
    return Glpi().glpi_version

def check_saas() -> bool:
    cfg = ConfigParser(interpolation=None)
    cfg.read(['/etc/mmc/plugins/glpi.ini', '/etc/mmc/plugins/glpi.ini.local'], encoding='utf-8')
    return cfg.get('main', 'hide_itsm_link', fallback='False') == 'True'

def getMachineUUIDByMacAddress(mac):
    return xmlrpcCleanup(Glpi().getMachineUUIDByMacAddress(mac))


def getMachinesLocations(uuids):
    return xmlrpcCleanup(Glpi().getMachinesLocations(uuids))


def hasKnownOS(uuid):
    return xmlrpcCleanup(Glpi().hasKnownOS(uuid))


def getLocationsForUser(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getLocationsForUser(*args, **kwargs))

def getLocationsForUsersName(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getLocationsForUsersName(*args, **kwargs))

def setLocationsForUser(*args, **kwargs):
    return xmlrpcCleanup(Glpi().setLocationsForUser(*args, **kwargs))


def getAllUserProfiles(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllUserProfiles(*args, **kwargs))


def getAllEntityRules(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllEntityRules(*args, **kwargs))


def getEntityRule(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getEntityRule(*args, **kwargs))


def getAllLocations(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllLocations(*args, **kwargs))


def getAllLocationsPowered(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllLocationsPowered(*args, **kwargs))


def addUser(*args, **kwargs):
    return xmlrpcCleanup(Glpi().addUser(*args, **kwargs))


def addEntity(*args, **kwargs):
    return xmlrpcCleanup(Glpi().addEntity(*args, **kwargs))


def editEntity(*args, **kwargs):
    return xmlrpcCleanup(Glpi().editEntity(*args, **kwargs))


def addEntityRule(*args, **kwargs):
    return xmlrpcCleanup(Glpi().addEntityRule(*args, **kwargs))


def editEntityRule(*args, **kwargs):
    return xmlrpcCleanup(Glpi().editEntityRule(*args, **kwargs))


def deleteEntityRule(*args, **kwargs):
    return xmlrpcCleanup(Glpi().deleteEntityRule(*args, **kwargs))


def setUserPassword(*args, **kwargs):
    return xmlrpcCleanup(Glpi().setUserPassword(*args, **kwargs))


def addLocation(*args, **kwargs):
    return xmlrpcCleanup(Glpi().addLocation(*args, **kwargs))


def editLocation(*args, **kwargs):
    return xmlrpcCleanup(Glpi().editLocation(*args, **kwargs))


def getAllEntities(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllEntities(*args, **kwargs))


def getAllEntitiesPowered(*args, **kwargs):
    return xmlrpcCleanup(Glpi().getAllEntitiesPowered(*args, **kwargs))


def moveEntityRuleUp(*args, **kwargs):
    return xmlrpcCleanup(Glpi().moveEntityRuleUp(*args, **kwargs))


def moveEntityRuleDown(*args, **kwargs):
    return xmlrpcCleanup(Glpi().moveEntityRuleDown(*args, **kwargs))


def get_all_uuids_and_hostnames():
    return Glpi().get_all_uuids_and_hostnames()


def get_machines_with_os_and_version(os, version):
    return xmlrpcCleanup(Glpi().get_machines_with_os_and_version(os, version))


def getMachinesMac(uuid):
    if uuid != "":
        return xmlrpcCleanup(Glpi().getMachinesMac(uuid))
    else:
        return ""


def get_os_xmpp_update_major_stats(presence=False):
    return xmlrpcCleanup(Glpi().get_os_xmpp_update_major_stats(presence))


def get_machine_for_hostname(strlisthostnale, filter="", start=0, end=0):
    return xmlrpcCleanup(
        Glpi().get_machine_for_hostname(strlisthostnale, filter, start, end)
    )


def get_user_by_name(name):
     return xmlrpcCleanup(Glpi().get_user_by_name(name))

def get_user_profile_name(login):
     return xmlrpcCleanup(Glpi().get_user_profile_name(login))

def get_entities_with_counts( colonne: bool = True,
                              entities: list[int] = None):
    return xmlrpcCleanup(Glpi().get_entities_with_counts(colonne = colonne,
                                        entities=entities))

def get_entities_with_counts_root( filter: str = None,
                                   start: int = -1,
                                   end: int = -1,
                                   colonne: bool = True,
                                   entities: list[int] = None):
    return xmlrpcCleanup(Glpi().get_entities_with_counts_root( filter=filter,
                                                               start=-1,
                                                               end=-1,
                                                               colonne=colonne,
                                                               entities=entities))

def set_user_api_token(user_id, api_token):
    return xmlrpcCleanup(Glpi().set_user_api_token(user_id, api_token))

def get_user_profile_email(id_user, id_profile=None, id_entity=None, filters=None, is_active=None):
    if not isinstance(filters, dict):
        filters = {}
    return xmlrpcCleanup(
        Glpi().get_user_profile_email(
            id_user,
            id_profile,
            id_entity,
            is_active=is_active,
            filters=filters,
        )
    )

def get_user_identifier(id_user):
    return xmlrpcCleanup(Glpi().get_user_identifier(id_user))

def get_complete_name(id_entity):
    return xmlrpcCleanup(Glpi().get_complete_name(id_entity))

def list_entity_ids_subtree(id_entity):
    return xmlrpcCleanup(Glpi().list_entity_ids_subtree(id_entity))

def list_user_ids_in_subtree(id_entity):
    return xmlrpcCleanup(Glpi().list_user_ids_in_subtree(id_entity))

def list_computer_ids_in_subtree(id_entity):
    return xmlrpcCleanup(Glpi().list_computer_ids_in_subtree(id_entity))

def get_machine_for_id(strlistuuid, filter="", start=0, end=0):
    return xmlrpcCleanup(Glpi().get_machine_for_id(strlistuuid, filter, start, end))


def get_os_update_major_stats():
    return Glpi().get_os_update_major_stats()


def get_os_update_major_details(entity_id,
                                filter="",
                                start=0,
                                limit=-1,
                                colonne=True):
    return Glpi().get_os_update_major_details(entity_id,
                                              filter,
                                              start,
                                              limit,
                                              colonne)
