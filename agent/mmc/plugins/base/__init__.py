#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Contains the base plugin for the MMC agent.
"""


from mmc.support.errorObj import errorMessage
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.base.config import BasePluginConfig
from mmc.plugins.base.computers import ComputerManager, ComputerI
from mmc.plugins.base.auth import (
    AuthenticationManager,
    AuthenticatorI,
    AuthenticationToken,
)
from mmc.plugins.base.provisioning import ProvisioningManager
from mmc.plugins.base.externalldap import (
    ExternalLdapAuthenticator,
    ExternalLdapProvisioner,
)
from mmc.plugins.base.ldapconnect import LDAPConnection
from mmc.support import mmctools
from mmc.support.mmctools import (
    cSort,
    rchown,
    copytree,
    cleanFilter,
    xmlrpcCleanup,
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
)
from mmc.site import mmcconfdir, localstatedir
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory as AF
from mmc.plugins.base.audit import AA, AT, PLUGIN_NAME
from mmc.plugins.base.subscription import SubscriptionManager
from mmc.agent import PluginManager


from uuid import uuid1
import shelve
import ldap
import ldif
import crypt
import base64
import random
import string
import re
import os
import time
import copy
import tempfile
import logging
import shutil
import xmlrpc.client
from subprocess import Popen, PIPE

from time import mktime, strptime, strftime, localtime
from configparser import NoSectionError, NoOptionError
from twisted.internet import defer

import hashlib

_digest = hashlib.sha1
from mmc.core.tasks import TaskManager
from time import strftime
import gc
import datetime
from memory_profiler import *

mesuref = 0.0
countseconde = 0
mesure = ""
name_file_log_leak_memory = "/tmp/leakmemory.data"
timecheck = 3600


# global definition for ldapUserGroupControl
INI = f"{mmcconfdir}/plugins/base.ini"

modList = None

VERSION = "5.1.0"
APIVERSION = "9:0:5"
REVISION = scmRevision("$Rev$")

# List of methods that can be called without user authentication
NOAUTHNEEDED = [
    "authenticate",
    "ldapAuth",
    "isCommunityVersion",
    "createAuthToken",
    "tokenAuthenticate",
]


def cmp(a, b):
    return (a > b) - (a < b)


def getVersion():
    return VERSION


def getApiVersion():
    return APIVERSION


def getRevision():
    return REVISION


def listEvent():
    return mmctools.ProcessScheduler().listEvent()


def activate():
    """
    this function define if the module "base" can be activated.
    @return: return True if this module can be activate
    @rtype: boolean
    """
    logger = logging.getLogger()
    global name_file_log_leak_memory
    global timecheck
    try:
        ldapObj = ldapUserGroupControl()
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False

    # Test if the MMC LDAP schema is available in the directory
    try:
        schema = ldapObj.getSchema("lmcUserObject")
        if len(schema) <= 0:
            logger.error("MMC schema seems not be include in LDAP directory")
            return False
    except:
        logger.exception("invalid schema")
        return False

    if not os.path.isdir(ldapObj.skelDir):
        logger.error(
            f"Skeleton directory {ldapObj.skelDir} does not exist or is not a directory"
        )
        return False

    config = PluginConfigFactory.new(BasePluginConfig, "base")
    if not os.path.isdir(config.backupdir):
        logger.error(
            f"Backup directory {config.backupdir} does not exist or is not a directory"
        )
        return False

    if not os.path.exists(os.path.join(config.backuptools, "backup.sh")):
        logger.error(
            f"Backup tools in directory {config.backuptools} are not available"
        )
        return False

    # Create required OUs
    ous = [ldapObj.baseUsersDN, ldapObj.baseGroupsDN, ldapObj.gpoDN]
    for ou in ous:
        head, path = ou.split(",", 1)
        ouName = head.split("=")[1]
        ldapObj.addOu(str(ouName), path)

    # Create the default user group
    if not ldapObj.existGroup(ldapObj.defaultUserGroup):
        if ldapObj.defaultUserGroup not in (
            "Domain Users",
            "Account Operators",
            "Administrators",
            "Backup Operators",
            "Domain Admins",
            "Domain Computers",
            "Domain Guests",
            "Print Operators",
            "Replicators",
        ):
            logger.info(
                f"The default user group {ldapObj.defaultUserGroup} does not exist. Creating..."
            )
            ldapObj.addGroup(ldapObj.defaultUserGroup)
        else:
            # Can't create automatically a SAMBA group
            logger.warning(
                f"The default user group {ldapObj.defaultUserGroup} must be created with the smbldap-populate command"
            )

    # Plug the subscription system
    SubscriptionManager().init(config)

    # Register authenticators
    AuthenticationManager().register("baseldap", BaseLdapAuthenticator)
    AuthenticationManager().register("externalldap", ExternalLdapAuthenticator)

    # Register provisioner
    ProvisioningManager().register("externalldap", ExternalLdapProvisioner)

    # Register computer list manager
    # ComputerManager().register("baseldap", Computers)

    # if  logging.getLevelName(logging.DEBUG) == "DEBUG":
    if not config.leak_memory_disable:
        TaskManager().addTask(
            "leakmemory", (leakmemory,), interval=config.leak_memorytime
        ).addErrback(err)
        with open(config.fileoutresult, "a") as fichier:
            date = datetime.datetime.now()
            fichier.write("\nSTART MMC [%s]\n" % date)
        timecheck = config.leak_memorytime
        name_file_log_leak_memory = config.fileoutresult
    return True


def activate_2():
    """
    This function is called by the MMC agent when all the plugins activate()
    functions have been called.

    This function configures and validates all the manager object.
    """
    ret = True
    config = PluginConfigFactory.new(BasePluginConfig, "base")

    for manager, method in [
        (AuthenticationManager(), config.authmethod),
        (ProvisioningManager(), config.provmethod),
        (ComputerManager(), config.computersmethod),
    ]:
        manager.select(method)
        ret = manager.validate()
        if not ret:
            break
    return ret


def err(failure):
    logging.debug("error leakmemory")
    failure.raiseException()


def leakmemory():
    """
    function scheduler use to chase memory leaks
    """
    # schedule deployement
    global countseconde
    global timecheck
    global mesure
    global mesuref
    global name_file_log_leak_memory

    countseconde += timecheck
    mem_usage = memory_usage(-1, interval=1, timeout=1)
    mesurel = str(mem_usage[0]).replace(".", ",")
    if mesurel != mesure:
        logging.debug("__________leak memory_________")
        logging.debug("evaluate the memory RSS")
        taillepris = mem_usage[0] - mesuref
        mesuref = mem_usage[0]
        with open(name_file_log_leak_memory, "a") as fichier:
            datetimewrite = strftime("%H:%M:%S")
            stem = (
                "\n%s count %s\ntime %ss MT %.2f MiB delta [ %s Mo | %s Ko | %s o | %s o/s]\n"
                % (
                    datetimewrite,
                    gc.get_count(),
                    countseconde,
                    mem_usage[0],
                    round(taillepris, 2),
                    int(taillepris * 1024),
                    int(taillepris * 1024 * 1024),
                    int((taillepris * 1024 * 1024) / countseconde),
                )
            )
            fichier.write(stem)
            countseconde = 0
            logging.debug(f"{stem}")
        mesure = mesurel
        logging.debug("______________________________")


def getModList():
    """
    define all modules avaible in mmc-agent
    @rtype: list
    @return: list with all modules loaded
    """
    global modList
    return modList


def setModList(param):
    """
    set a module liste
    @param param: module list to set
    @type param: list
    """
    global modList
    modList = param


def createAuthToken(user, server, lang):
    return ldapUserGroupControl().createAuthToken(user, server, lang)


def changeAclAttributes(uid, acl):
    ldapObj = ldapUserGroupControl()
    ldapObj.changeUserAttributes(uid, acl)
    return 0


def setPrefs(uid, pref):
    ldapObj = ldapUserGroupControl()
    ldapObj.changeUserAttributes(uid, "lmcPrefs", pref)
    return 0


def getPrefs(uid):
    ldapObj = ldapUserGroupControl()
    try:
        return ldapObj.getDetailedUser(uid)["lmcPrefs"][0]
    except:
        return ""


def changeGroupDescription(cn, desc):
    ldapObj = ldapUserGroupControl()
    ldapObj.changeGroupAttributes(cn, "description", desc)
    return 0


def getUsersLdap(searchFilter=""):
    ldapObj = ldapUserGroupControl()
    searchFilter = cleanFilter(searchFilter)
    return ldapObj.searchUser(searchFilter)


def searchUserAdvanced(searchFilter="", start=None, end=None):
    """
    Used by the MMC web interface to get a user list
    """
    ldapObj = ldapUserGroupControl()
    if "=" in searchFilter:
        terms = [f"({term})" for term in searchFilter.split() if "=" in term]
        searchFilter = f'(&{"".join(terms)})'
    else:
        searchFilter = cleanFilter(searchFilter)
        if searchFilter:
            searchFilter = f"(|(uid={searchFilter})(givenName={searchFilter})(sn={searchFilter})(telephoneNumber={searchFilter})(mail={searchFilter}))"
    return ldapObj.searchUserAdvance(searchFilter, None, start, end)


def getGroupEntry(cn):
    return ldapUserGroupControl().getGroupEntry(cn)


def getGroupsLdap(searchFilter=""):
    ldapObj = ldapUserGroupControl()
    searchFilter = cleanFilter(searchFilter)

    # Need to cast bytes to str
    raw = ldapObj.searchGroup(searchFilter)
    return {
        key.decode("utf-8"): [
            val.decode("utf-8") if type(val) is bytes else val for val in raw[key]
        ]
        for key in raw
    }


def getDefaultUserGroup():
    ldapObj = ldapUserGroupControl()
    return ldapObj.defaultUserGroup


def getUserDefaultPrimaryGroup():
    return ldapUserGroupControl().defaultUserGroup


def getUserPrimaryGroup(uid):
    if type(uid) is bytes:
        uid = uid.decode("utf-8")
    return ldapUserGroupControl().getUserPrimaryGroup(uid)


def getUserSecondaryGroups(uid):
    return ldapUserGroupControl().getUserSecondaryGroups(uid)


def createGroup(groupName):
    ldapObj = ldapUserGroupControl()
    return ldapObj.addGroup(groupName)


def existGroup(groupName):
    return ldapUserGroupControl().existGroup(groupName)


def getHomeDir(uid, homeDir):
    return ldapUserGroupControl().getHomeDir(uid, homeDir)


def getDefaultShells():
    return ldapUserGroupControl().getDefaultShells()


def createUser(
    login,
    passwd,
    firstname,
    surname,
    homedir,
    createHomeDir=True,
    ownHomeDir=False,
    primaryGroup=None,
):
    return ldapUserGroupControl().addUser(
        login,
        passwd,
        firstname,
        surname,
        homedir,
        createHomeDir,
        ownHomeDir,
        primaryGroup,
    )


def addUserToGroup(cngroup, uiduser):
    ldapObj = ldapUserGroupControl()
    return ldapObj.addUserToGroup(cngroup, uiduser)


def delUserFromGroup(cngroup, uiduser):
    ldapObj = ldapUserGroupControl()
    return ldapObj.delUserFromGroup(cngroup, uiduser)


def delUserFromAllGroups(uid):
    ldapObj = ldapUserGroupControl()
    return ldapObj.delUserFromAllGroups(uid)


def changeUserPrimaryGroup(uid, groupName):
    return ldapUserGroupControl().changeUserPrimaryGroup(uid, groupName)


def delUser(uiduser, home):
    ldapObj = ldapUserGroupControl()
    return ldapObj.delUser(uiduser, home)


def delGroup(cngroup):
    return ldapUserGroupControl().delGroup(cngroup)


# return a list of member
# return an array
def getMembers(cngroup):
    ldapObj = ldapUserGroupControl()
    return ldapObj.getMembers(cngroup)


# change password for account and
# for sambaAccount via smbpasswd
def changeUserPasswd(uid, passwd, oldpasswd=None, bind=False):
    ldapObj = ldapUserGroupControl()
    return ldapObj.changeUserPasswd(uid, passwd, oldpasswd, bind)


# return all users of a specific group
def getUserGroups(pattern):
    ldapObj = ldapUserGroupControl()
    return ldapObj.getUserGroups(pattern)


# backup fonction
def backupUser(user, media, login, configFile=f"{mmcconfdir}/plugins/base.ini"):
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    cmd = os.path.join(config.backuptools, "backup.sh")
    ldapObj = ldapUserGroupControl()
    homedir = ldapObj.getDetailedUser(user)["homeDirectory"][0]
    mmctools.shlaunchBackground(
        cmd
        + " "
        + user
        + " "
        + homedir
        + " "
        + config.backupdir
        + " "
        + login
        + " "
        + media
        + " "
        + config.backuptools,
        f"backup user {user}",
        mmctools.progressBackup,
    )
    return os.path.join(config.backupdir, f'{login}-{user}-{strftime("%Y%m%d")}')


# return entire ldap info on uid user
def getDetailedUser(uid):
    ldapObj = ldapUserGroupControl()
    return ldapObj.getDetailedUser(uid)


def getDetailedGroup(cn):
    ldapObj = ldapUserGroupControl()
    return ldapObj.getDetailedGroup(cn)


def getUserAttribute(uid, attr):
    return getUserAttributes(uid, attr)[0]


def getUserAcl(uid):
    if uid == "root":
        return ""
    ldapObj = ldapUserGroupControl()
    try:
        allInfo = ldapObj.getDetailedUser(uid)
        result = allInfo["lmcACL"][0]
        if isinstance(result, bytes):
            result = result.decode("utf-8")
        return result
    except:
        # test if contain lmcUserObject
        if "lmcUserObject" not in allInfo["objectClass"]:
            allInfo["objectClass"].append(b"lmcUserObject")
            ldapObj.changeUserAttributes(uid, "objectClass", allInfo["objectClass"])
        return ""


def setUserAcl(uid, aclString):
    ldapObj = ldapUserGroupControl()
    ldapObj.changeUserAttributes(uid, "lmcACL", aclString)
    return 0


def getUserAttributes(uid, attr):
    ldapObj = ldapUserGroupControl()
    arr = ldapObj.getDetailedUser(uid)
    return arr[attr]


def existUser(uid):
    # if no uid precise
    if uid == "":
        return False
    ldapObj = ldapUserGroupControl()
    return ldapObj.existUser(uid)


# change main UserAttributes
def changeUserMainAttributes(uid, newuid, name, surname):
    ldapObj = ldapUserGroupControl()
    try:
        gecos = delete_diacritics(f"{name} {surname}")
    except UnicodeEncodeError:
        gecos = uid

    if surname:
        ldapObj.changeUserAttributes(uid, "sn", surname)
    if name:
        ldapObj.changeUserAttributes(uid, "givenName", name)
    try:
        ldapObj.changeUserAttributes(uid, "gecos", gecos)
    except ldap.INVALID_SYNTAX:
        ldapObj.changeUserAttributes(uid, "gecos", uid)
    if newuid != uid:
        ldapObj.changeUserAttributes(uid, "cn", uid)
        ldapObj.changeUserAttributes(uid, "uid", newuid)
    return 0


def changeUserAttributes(uid, attr, attrval):
    ldapObj = ldapUserGroupControl()
    ldapObj.changeUserAttributes(uid, attr, attrval)


def maxUID():
    ldapObj = ldapUserGroupControl()
    return ldapObj.maxUID()


def freeUID():
    return ldapUserGroupControl().freeUID()


def maxGID():
    ldapObj = ldapUserGroupControl()
    return ldapObj.maxGID()


def moveHome(uid, home):
    ldapObj = ldapUserGroupControl()
    return ldapObj.moveHome(uid, home)


def addOu(ouname, ldappath):
    """
    add Organizational Unit
     - ouname: Name of new Organizational Unit
     - ldappath : ldap path
        ex: uid=foo, ou=bar, dc=linbox, dc=com
    """
    ldapObj = ldapUserGroupControl()
    ldapObj.addOu(ouname, ldappath)


def enableUser(login):
    ldapObj = ldapUserGroupControl()
    return ldapObj.enableUser(login)


def disableUser(login):
    ldapObj = ldapUserGroupControl()
    return ldapObj.disableUser(login)


def isEnabled(login):
    ldapObj = ldapUserGroupControl()
    return ldapObj.isEnabled(login)


def isLocked(login):
    ldapObj = ldapUserGroupControl()
    return ldapObj.isLocked(login)


def getAllGroupsFromUser(uid):
    ldapObj = ldapUserGroupControl()
    return ldapObj.getAllGroupsFromUser(uid)


def getUserDN(uid):
    ldapObj = ldapUserGroupControl()
    return ldapObj.searchUserDN(uid)


def getLog(*args):
    return AF().getLog(*args)


def getLogById(*args):
    return AF().getLogById(*args)


def getActionType(*args):
    return AF().getActionType(*args)


def hasAuditWorking():
    """
    Returns True if the audit module is enabled
    """
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    return config.auditmethod != "none"


def getSubscriptionInformation(is_dynamic=False):
    return xmlrpcCleanup(SubscriptionManager().getInformations(is_dynamic))


def isCommunityVersion():
    return xmlrpcCleanup(SubscriptionManager().isCommunity())


###log view accessor
def isLogViewEnabled():
    return LogView().isLogViewEnabled()


def getLdapLog(filter=""):
    return LogView().getLog(filter)


_reptable = {}


def _fill_reptable():
    """
    this function create array to remove accent
    not call, execute on startup
    """
    _corresp = [
        ("A", [0x00C0, 0x00C1, 0x00C2, 0x00C3, 0x00C4, 0x00C5, 0x0100, 0x0102, 0x0104]),
        ("AE", [0x00C6]),
        ("a", [0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5, 0x0101, 0x0103, 0x0105]),
        ("ae", [0x00E6]),
        ("C", [0x00C7, 0x0106, 0x0108, 0x010A, 0x010C]),
        ("c", [0x00E7, 0x0107, 0x0109, 0x010B, 0x010D]),
        ("D", [0x00D0, 0x010E, 0x0110]),
        ("d", [0x00F0, 0x010F, 0x0111]),
        ("E", [0x00C8, 0x00C9, 0x00CA, 0x00CB, 0x0112, 0x0114, 0x0116, 0x0118, 0x011A]),
        ("e", [0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x0113, 0x0115, 0x0117, 0x0119, 0x011B]),
        ("G", [0x011C, 0x011E, 0x0120, 0x0122]),
        ("g", [0x011D, 0x011F, 0x0121, 0x0123]),
        ("H", [0x0124, 0x0126]),
        ("h", [0x0125, 0x0127]),
        ("I", [0x00CC, 0x00CD, 0x00CE, 0x00CF, 0x0128, 0x012A, 0x012C, 0x012E, 0x0130]),
        ("i", [0x00EC, 0x00ED, 0x00EE, 0x00EF, 0x0129, 0x012B, 0x012D, 0x012F, 0x0131]),
        ("IJ", [0x0132]),
        ("ij", [0x0133]),
        ("J", [0x0134]),
        ("j", [0x0135]),
        ("K", [0x0136]),
        ("k", [0x0137, 0x0138]),
        ("L", [0x0139, 0x013B, 0x013D, 0x013F, 0x0141]),
        ("l", [0x013A, 0x013C, 0x013E, 0x0140, 0x0142]),
        ("N", [0x00D1, 0x0143, 0x0145, 0x0147, 0x014A]),
        ("n", [0x00F1, 0x0144, 0x0146, 0x0148, 0x0149, 0x014B]),
        ("O", [0x00D2, 0x00D3, 0x00D4, 0x00D5, 0x00D6, 0x00D8, 0x014C, 0x014E, 0x0150]),
        ("o", [0x00F2, 0x00F3, 0x00F4, 0x00F5, 0x00F6, 0x00F8, 0x014D, 0x014F, 0x0151]),
        ("OE", [0x0152]),
        ("oe", [0x0153]),
        ("R", [0x0154, 0x0156, 0x0158]),
        ("r", [0x0155, 0x0157, 0x0159]),
        ("S", [0x015A, 0x015C, 0x015E, 0x0160]),
        ("s", [0x015B, 0x015D, 0x015F, 0x01610, 0x017F]),
        ("ss", [0x00DF]),
        ("T", [0x0162, 0x0164, 0x0166]),
        ("t", [0x0163, 0x0165, 0x0167]),
        (
            "U",
            [
                0x00D9,
                0x00DA,
                0x00DB,
                0x00DC,
                0x0168,
                0x016A,
                0x016C,
                0x016E,
                0x0170,
                0x172,
            ],
        ),
        ("u", [0x00F9, 0x00FA, 0x00FB, 0x00FC, 0x0169, 0x016B, 0x016D, 0x016F, 0x0171]),
        ("W", [0x0174]),
        ("w", [0x0175]),
        ("Y", [0x00DD, 0x0176, 0x0178]),
        ("y", [0x00FD, 0x00FF, 0x0177]),
        ("Z", [0x0179, 0x017B, 0x017D]),
        ("z", [0x017A, 0x017C, 0x017E]),
    ]
    global _reptable
    for repchar, codes in _corresp:
        for code in codes:
            _reptable[code] = repchar


_fill_reptable()


def delete_diacritics(s):
    """
    Delete accent marks.

    @param s: string to clean
    @type s: unicode
    @return: cleaned string
    @rtype: unicode
    """
    if isinstance(s, bytes):
        s = s.decode("utf-8")

    ret = [_reptable.get(ord(c), c) for c in s]
    return "".join(ret)


# FIXME: Change this class name
class LdapUserGroupControl:
    """
    Control of User/Group/Computer(smb) control via LDAP
    this class create

    When instantiaciate, this class create an admin connection on ldap.
    After that, we have two members:
     - self.config: ConfigParser of main config file
     - self.l: bind on ldap with admin privilege
    """

    def _getSalt(self, method):
        """
        Generate salt for password encryption, according to the wanted
        encryption method.

        @returns: if method is crypt, return a random two character string, else return a random twenty character string
        @rtype: str

        """
        length = 2 if method == "crypt" else 20
        ret = ""
        for _ in range(length):
            ret = ret + random.choice(string.letters + string.digits)
        return ret

    def _generatePassword(self, password, scheme=None):
        """
        Generate a string suitable for the LDAP userPassword field

        @param password: password to hash
        @type password: str

        @param scheme: LDAP password scheme to use (crypt or ssha)
        @type scheme: str

        @returns: string suitable for the LDAP userPassword field
        @rtype: str
        """
        if not scheme:
            scheme = self.config.passwordscheme
        # If the passwd has been encoded in the XML-RPC stream, decode it
        if isinstance(password, xmlrpc.client.Binary):
            password = str(password)
        salt = self._getSalt(scheme)
        if scheme == "crypt":
            return "{crypt}" + crypt.crypt(password, salt)
        ctx = _digest(password)
        ctx.update(salt)
        return "{SSHA}" + base64.encodestring(ctx.digest() + salt)

    def _setDefaultConfig(self):
        """
        Set default config options.
        """
        self.gpoDN = f"ou=System,{self.baseDN}"
        self.skelDir = "/etc/skel"
        self.defaultUserGroup = None
        self.defaultHomeDir = "/home"
        self.defaultShellEnable = "/bin/bash"
        self.defaultShellDisable = "/bin/false"
        self.uidStart = 10000
        self.gidStart = 10000

    def __init__(self, conffile=None):
        """
        Constructor
        Create a LDAP connection on self.l with admin right
        Create a ConfigParser on self.config
        """
        configFile = conffile if conffile else INI
        self.conffile = configFile
        self.config = PluginConfigFactory.new(BasePluginConfig, "base", self.conffile)

        self.logger = logging.getLogger()

        self.baseDN = self.config.baseDN
        self.baseGroupsDN = self.config.getdn("ldap", "baseGroupsDN")
        self.baseUsersDN = self.config.baseUsersDN
        self.userHomeAction = self.config.getboolean("ldap", "userHomeAction")
        self._setDefaultConfig()

        try:
            self.gpoDN = self.config.getdn("ldap", "gpoDN")
        except:
            pass
        try:
            self.defaultUserGroup = self.config.get("ldap", "defaultUserGroup")
        except:
            pass
        try:
            self.skelDir = self.config.get("ldap", "skelDir")
        except:
            pass
        try:
            self.defaultHomeDir = self.config.get("ldap", "defaultHomeDir")
        except:
            pass
        try:
            self.uidStart = self.config.getint("ldap", "uidStart")
        except:
            pass
        try:
            self.gidStart = self.config.getint("ldap", "gidStart")
        except:
            pass
        try:
            self.defaultShellEnable = self.config.getint("ldap", "defaultShellEnable")
        except:
            pass
        try:
            self.defaultShellDisable = self.config.getint("ldap", "defaultShellDisable")
        except:
            pass

        try:
            listHomeDir = self.config.get("ldap", "authorizedHomeDir")
            self.authorizedHomeDir = listHomeDir.replace(" ", "").split(",")
        except:
            self.authorizedHomeDir = [self.defaultHomeDir]

        # Fill dictionnary of hooks from config
        self.hooks = {}
        if self.config.has_section("hooks"):
            for option in self.config.options("hooks"):
                self.hooks[f"base.{option}"] = self.config.get("hooks", option)

        self.userDefault = {"base": {}}
        USERDEFAULT = "userdefault"
        if self.config.has_section(USERDEFAULT):
            for option in self.config.options(USERDEFAULT):
                self.userDefault["base"][option] = self.config.get(USERDEFAULT, option)

        self.l = LDAPConnection(self.config).get()

        # Any error will throw a ldap.LDAPError exception
        self.l.simple_bind_s(str(self.config.username), self.config.password)

    def runHook(self, hookName, uid=None, password=None):
        """
        Run a hook.
        """
        if hookName not in self.hooks:
            return
        self.logger.info(f"Hook {hookName} called.")
        if uid:
            # Make a temporary ldif file with user entry if an uid is specified
            fd, tmpname = tempfile.mkstemp()
            try:
                fob = os.fdopen(fd, "wb")
                dn = self.searchUserDN(uid)
                entry = self.getUserEntry(uid)
                if password:
                    if isinstance(password, xmlrpc.client.Binary):
                        password = str(password)
                    # Put user password in clear text in ldif
                    entry["userPassword"] = [password]
                writer = ldif.LDIFWriter(fob)
                writer.unparse(dn, entry)
                fob.close()
                mmctools.shlaunch(f"{self.hooks[hookName]} {tmpname}")
            finally:
                os.remove(tmpname)
        else:
            mmctools.shlaunch(self.hooks[hookName])

    def enableUser(self, login):
        """
        Enable user by setting his/her shell to defaultShellEnable (default /bin/bash)

        @param login: login of the user
        @type login: str
        """
        userdn = self.searchUserDN(login)
        attr = "loginShell"
        r = AF().log(
            PLUGIN_NAME, AA.BASE_ENABLE_USER, [(userdn, AT.USER), (attr, AT.ATTRIBUTE)]
        )
        s = self.l.search_s(userdn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        new[attr] = self.defaultShellEnable
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(userdn, modlist)
        r.commit()
        return 0

    def disableUser(self, login):
        """
        Disable user by setting his/her shell to defaultShellDisable (default /bin/false)

        @param login: login of the user
        @type login: str
        """
        userdn = self.searchUserDN(login)
        attr = "loginShell"
        r = AF().log(
            PLUGIN_NAME, AA.BASE_DISABLE_USER, [(userdn, AT.USER), (attr, AT.ATTRIBUTE)]
        )
        s = self.l.search_s(userdn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        new["loginShell"] = self.defaultShellDisable
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(userdn, modlist)
        r.commit()
        return 0

    def isEnabled(self, login):
        """
        Return True if the user is enabled, else False.
        A user is enabled if his/her shell is not defaultShellDisable
        A user is also disabled if the user has no loginShell attribute.
        """
        u = self.getDetailedUser(login)
        try:
            return u["loginShell"] != [self.defaultShellDisable]
        except KeyError:
            return False

    def _applyUserDefault(self, entry, default):
        """
        Prepare the modification of a user entry with default values.

        @param entry: current user entry
        @type entry: dict

        @param default: default values to apply
        @type default: dict

        @return: new user entry
        @rtype: dict
        """
        entry = copy.deepcopy(entry)
        for attribute, value in list(default.items()):
            if s := re.search("^\[(.*)\]", value):
                modifiers = s.groups()[0]
                # Remove modifiers from the string
                value = re.sub("^\[.*\]", "", value)
            else:
                modifiers = ""
            # Interpolate value
            if "%" in value:
                for a, v in list(entry.items()):
                    if isinstance(v, list):
                        v = v[0]
                    if isinstance(v, str):
                        if "/" in modifiers:
                            v = delete_diacritics(v)
                        if "_" in modifiers:
                            v = v.lower()
                        if "|" in modifiers:
                            v = v.upper()
                        value = value.replace(f"%{a}%", v)
            if value == "DELETE":
                for key in list(entry.keys()):
                    if key.lower() == attribute:
                        del entry[key]
                        break
            elif value.startswith("+"):
                for key in list(entry.keys()):
                    if key.lower() == attribute:
                        entry[key] = entry[key] + value[1:].split(",")
                        break
            else:
                found = False
                for key in list(entry.keys()):
                    if key.lower() == attribute:
                        entry[key] = value
                        found = True
                        break
                if not found:
                    entry[attribute] = value
        return entry

    def addUser(
        self,
        uid,
        password,
        firstN,
        lastN,
        homeDir=None,
        createHomeDir=True,
        ownHomeDir=False,
        primaryGroup=None,
    ):
        """
        Add an user in ldap directory

        accent remove for gecos entry in ldap directory

        @param uid: login of the user
        @type uid: str

        @param password: user's password
        @type password : str

        @param firstN: unicode string with first name
        @type firstN: str

        @param lastN: unicode string with last name
        @type lastN: str

        @param homeDir: home directory of the user. If empty or None, default to defaultHomeDir/uid
        @type homeDir: str

        @param primaryGroup: primary group of the user. If empty or None, default to defaultUserGroup
        @type primaryGroup: str

        @param createHomeDir: Flag telling if the user home directory is
                              created on the filesystem
        @type createHomeDir: bool
        """
        ident = f"uid={uid},{self.baseUsersDN}"
        r = AF().log(PLUGIN_NAME, AA.BASE_ADD_USER, [(ident, AT.USER)])

        # Get the homeDir path
        if ownHomeDir:
            homeDir = self.getHomeDir(uid, homeDir, False)
        else:
            homeDir = self.getHomeDir(uid, homeDir)

        uidNumber = self.freeUID()

        # Get a gid number
        if not primaryGroup:
            if self.defaultUserGroup:
                primaryGroup = self.defaultUserGroup
            else:
                primaryGroup = uid
                if self.addGroup(uid) == -1:
                    raise Exception("group error: already exist or cannot instanciate")
        gidNumber = int(self.getDetailedGroup(primaryGroup)["gidNumber"][0])

        # Get the loginShell
        shell = self.defaultShellEnable

        # Put default value in firstN and lastN
        if not firstN:
            firstN = uid
        if not lastN:
            lastN = uid

        # For the gecos LDAP field, make a full ASCII string
        try:
            gecosFirstN = str(delete_diacritics((firstN.encode("UTF-8"))))
            gecosLastN = str(delete_diacritics((lastN.encode("UTF-8"))))
            gecos = f"{gecosFirstN} {gecosLastN}"
        except UnicodeEncodeError:
            gecos = uid

        # Build a UTF-8 representation of the unicode strings
        lastN = str(lastN.encode("utf-8"))
        firstN = str(firstN.encode("utf-8"))

        # Create insertion array in ldap dir
        # FIXME: document shadow attributes choice
        user_info = {
            "loginShell": shell,
            "uidNumber": str(uidNumber),
            "gidnumber": str(gidNumber),
            "objectclass": [
                "inetOrgPerson",
                "posixAccount",
                "shadowAccount",
                "top",
                "person",
                "lmcUserObject"
            ],
            "uid": uid,
            "gecos": gecos,
            "cn": f"{firstN} {lastN}",
            "displayName": f"{firstN} {lastN}",
            "sn": lastN,
            "givenName": firstN,
            "homeDirectory": homeDir,
            "shadowExpire": "-1",
            "shadowInactive": "-1",
            "shadowWarning": "7",
            "shadowMin": "-1",
            "shadowMax": "99999",
            "shadowFlag": "134538308",
            "shadowLastChange": "11192",
        }

        user_info = self._applyUserDefault(user_info, self.userDefault["base"])

        # Search Python unicode string and encode them to UTF-8
        attributes = []
        for k, v in list(user_info.items()):
            if isinstance(v, list):
                fields = []
                for item in v:
                    if isinstance(item, str):
                        item = item.encode("utf-8")
                    fields.append(item)
                attributes.append((k, fields))
            elif isinstance(v, str):
                attributes.append((k, v.encode("utf-8")))
            else:
                attributes.append((k, v))

        try:
            # Write user entry into the directory
            self.l.add_s(ident, attributes)
            # Set user password
            pwd_change = True
            try:
                self.changeUserPasswd(uid, password)
            # continue user creation when password fails pwd policies
            except ldap.CONSTRAINT_VIOLATION:
                pwd_change = False
            # Add user to her/his group primary group
            self.addUserToGroup(primaryGroup, uid)
        except ldap.LDAPError as error:
            # if we have a problem, we delete the group
            if not self.defaultUserGroup:
                self.delGroup(uid)
            # create error message
            raise error

        # creating home directory
        if self.userHomeAction and createHomeDir:
            # if we are here, we need to make
            # the user the owner of the directory
            if os.path.exists(homeDir):
                rchown(homeDir, uidNumber, gidNumber)
            else:
                try:
                    copytree(self.skelDir, homeDir, symlinks=True)
                    rchown(homeDir, uidNumber, gidNumber)
                except OSError:
                    # Problem when creating the user home directory,
                    # so we delete the user
                    self.delUser(uid, False)
                    raise

        # Run addUser hook
        self.runHook("base.adduser", uid, password)
        r.commit()
        # password has been changed, user is created
        return 0 if pwd_change else 5

    def isAuthorizedHome(self, home):
        return any(ahome in home for ahome in self.authorizedHomeDir)

    def getDefaultShells(self):
        return {
            "enabledShell": self.defaultShellEnable,
            "disabledShell": self.defaultShellDisable,
        }

    def getHomeDir(self, uid, homeDir=None, checkExists=True):
        """
        Check if home directory can be created
        Returns path

        @param home: the home directory path.
        @type home: str
        """

        # Make a home string if none was given
        if not homeDir:
            homeDir = os.path.join(self.defaultHomeDir, uid)
        if not self.isAuthorizedHome(os.path.realpath(homeDir)):
            raise Exception(f"{homeDir} is not an authorized home dir.")
        if not checkExists or not self.userHomeAction:
            return homeDir
        if not os.path.exists(homeDir):
            return homeDir
        else:
            raise Exception(f"{homeDir} already exists.")

    def addGroup(self, cn):
        """
        Add a group in an ldap directory

        @param cn: group name.
            We just precise the name, complete path for group is define
            in config file.
        @type cn: str
        """
        entry = f"cn={cn},{self.baseGroupsDN}"
        r = AF().log(PLUGIN_NAME, AA.BASE_ADD_GROUP, [(entry, AT.GROUP)])
        maxgid = self.maxGID()
        gidNumber = maxgid + 1

        # creating group skel
        group_info = {}

        # RFC2307bis posixGroup: add groupOfUniqueNames objectclass
        # this allow to use memberOf ldap overlay
        if self.posixGroupIsRFC2307bis():
            group_info = {
                "cn": cn.encode("utf-8"),
                "gidnumber": str(gidNumber).encode("utf-8"),
                "objectclass": (b"groupOfUniqueNames", b"posixGroup", b"top"),
                "uniqueMember": "",
            }
        # regular posixGroup
        else:
            group_info = {
                "cn": cn.encode("utf-8"),
                "gidnumber": str(gidNumber).encode("utf-8"),
                "objectclass": (b"posixGroup", b"top"),
            }

        attributes = list(list(group_info.items()))
        self.l.add_s(entry, attributes)

        r.commit()
        return self.getGroupEntry(cn)

    def getGroupEntry(self, cn, base=None):
        """
        Search a group entry and returns the raw LDAP entry content of a group.

        @param cn: Group common name
        @type cn: str

        @param base: LDAP base scope where to look for
        @type base: str

        @return: full raw ldap array (dictionnary of lists)
        @type: dict
        """
        if not base:
            base = self.baseGroupsDN
        ret = self.search(f"cn={str(cn)}", base)
        newattrs = {}
        if ret:
            for result in ret:
                c, attrs = result[0]
                newattrs = copy.deepcopy(attrs)
                break
        return newattrs

    def delUserFromGroup(self, cngroup, uiduser):
        """
        Remove a user from a posixGroup account.
        Remove memberUid in LDAP entry attributes.

        @param cngroup: name of the group (not full ldap path)
        @type cngroup: unicode

        @param uiduser: user uid (not full ldap path)
        @type uiduser: unicode
        """
        if type(cngroup) is bytes:
            cngroup = cngroup.decode("utf-8")
        if type(uiduser) is bytes:
            uiduser = uiduser.decode("utf-8")

        groupdn = f"cn={cngroup},{self.baseGroupsDN}"
        userdn = self.searchUserDN(uiduser)
        r = AF().log(
            PLUGIN_NAME,
            AA.BASE_DEL_USER_FROM_GROUP,
            [(groupdn, AT.GROUP), (userdn, AT.USER)],
        )

        operations = [(ldap.MOD_DELETE, "memberUid", bytes(uiduser, "utf-8"))]
        if self.posixGroupIsRFC2307bis():
            operations.append((ldap.MOD_DELETE, "uniqueMember", bytes(userdn, "utf-8")))

        try:
            self.l.modify_s(groupdn, operations)
        except ldap.NO_SUCH_ATTRIBUTE:
            # There are no member in this group
            pass
        r.commit()

    def delUserFromAllGroups(self, uid):
        """
        Remove an user from all groups in the LDAP

        @param uid: login of the user
        @type uid: unicode
        """
        if ret := self.search(f"memberUid={uid}", self.baseGroupsDN):
            for result in ret:
                group = result[0][1]["cn"][0]
                self.delUserFromGroup(group.decode("utf-8"), uid)
        return 0

    def changeUserPrimaryGroup(self, uid, group):
        """
        Change the primary group of a user

        @param uid: login of the user
        @type uid: unicode

        @param group: new primary group
        @type uid: unicode
        """
        gidNumber = self.getDetailedGroup(group)["gidNumber"][0]
        currentPrimary = self.getUserPrimaryGroup(uid)
        try:
            self.delUserFromGroup(currentPrimary, uid)
        except ldap.NO_SUCH_ATTRIBUTE:
            # Try to delete the user from a group where the she/he is not
            # Can be safely passed
            pass
        self.addUserToGroup(group, uid)
        self.changeUserAttributes(uid, "gidNumber", gidNumber)

    def getAllGroupsFromUser(self, uid):
        """
        Get all groups that own this user

        @param uid: login of the user
        @type uid: unicode
        """
        ret = self.search(f"memberUid={uid}", self.baseGroupsDN)
        resArray = []
        if ret:
            resArray.extend(result[0][1]["cn"][0] for result in ret)
        return resArray

    def getUserPrimaryGroup(self, uid):
        """
        Return the primary group of a user

        @param uid: user uid
        @type uid: unicode

        @return: the name of the group
        @rtype: unicode
        """
        if isinstance(uid, xmlrpc.client.Binary):
            uid = str(uid)
        gidNumber = int(self.getDetailedUser(uid)["gidNumber"][0])
        try:
            group = self.getDetailedGroupById(gidNumber)["cn"][0]
        except KeyError:
            import grp

            group = grp.getgrgid(gidNumber)[0]
        return group

    def getUserSecondaryGroups(self, uid):
        """
        Return the secondary groups of a user

        @param uid: user uid
        @type uid: unicode

        @return: a list of the name of the group
        @rtype: unicode
        """
        if isinstance(uid, xmlrpc.client.Binary):
            uid = str(uid)
        elif type(uid) is bytes:
            uid = uid.decode("utf-8")
        else:
            uid = uid
        primary = self.getUserPrimaryGroup(uid)
        secondary = self.getAllGroupsFromUser(uid)
        try:
            secondary.remove(primary)
        except ValueError:
            # The primary group is not listed in the secondary groups
            pass
        return secondary

    def addUserToGroup(self, cngroup, uid, base=None):
        """
        add memberUid attributes corresponding param user to an ldap posixGroup entry

        @param cngroup: name of the group (not full ldap path)
        @type cngroup: unicode

        @param uid: user uid (not full ldap path)
        @type uid: unicode
        """
        if not base:
            base = self.baseGroupsDN

        if type(cngroup) is bytes:
            cngroup = cngroup.decode("utf-8")
        if type(uid) is bytes:
            uid = uid.encode("utf-8")
        groupdn = f"cn={cngroup},{base}"
        userdn = self.searchUserDN(uid)
        r = AF().log(
            PLUGIN_NAME,
            AA.BASE_ADD_USER_TO_GROUP,
            [(groupdn, AT.GROUP), (userdn, AT.USER)],
        )

        operations = [(ldap.MOD_ADD, "memberUid", bytes(uid, "utf-8"))]
        if self.posixGroupIsRFC2307bis():
            operations.append((ldap.MOD_ADD, "uniqueMember", bytes(userdn, "utf-8")))

        try:
            self.l.modify_s(groupdn, operations)
        except ldap.TYPE_OR_VALUE_EXISTS:
            # Try to add a the user to one of his/her group
            # Can be safely ignored
            pass
        r.commit()
        return 0

    def changeUserAttributes(self, uid, attr, attrVal, log=True):
        """
        Change an user attribute.
        If an attrVal is empty, the attribute will be removed.

        @param uid: uid of this user (not full ldap path)
        @type  uid: str

        @param attr: attribute name
        @type  attr: str

        @param attrVal: attribute value
        @type  attrVal: object

        @param log: log action or not
        @type  log: boolean
        """
        userdn = self.searchUserDN(uid)

        # don't log jpeg values
        attrValue = None if attr == "jpegPhoto" else attrVal
        if attrVal:
            if log:
                r = AF().log(
                    PLUGIN_NAME,
                    AA.BASE_MOD_USER_ATTR,
                    [(userdn, AT.USER), (attr, AT.ATTRIBUTE)],
                    attrValue,
                )
            if isinstance(attrVal, str):
                attrVal = attrVal.encode("utf-8")
            elif isinstance(attrVal, xmlrpc.client.Binary):
                # Needed for binary string coming from XMLRPC
                attrVal = str(attrVal)
            try:
                self.l.modify_s(userdn, [(ldap.MOD_REPLACE, attr, attrVal)])
            except Exception as e:
                logging.getLogger().error(e)
                pass
            if log:
                r.commit()
        else:
            # Remove the attribute because its value is empty
            if log:
                r = AF().log(
                    PLUGIN_NAME,
                    AA.BASE_DEL_USER_ATTR,
                    [(userdn, AT.USER), (attr, AT.ATTRIBUTE)],
                )
            try:
                self.l.modify_s(userdn, [(ldap.MOD_DELETE, attr, None)])
                if log:
                    r.commit()
            except ldap.NO_SUCH_ATTRIBUTE:
                # The attribute has been already deleted
                pass

    def changeGroupAttributes(self, group, attr, attrVal, log=True):
        """
        Change a group's attributes

        @param group: group name (str)
        @param attr: attribute name (str)
        @param attrVal: attribute value
        @param log: log action or not (boolean)
        """
        groupdn = f"cn={group},{self.baseGroupsDN}"

        if attrVal:
            if log:
                r = AF().log(
                    PLUGIN_NAME,
                    AA.BASE_MOD_GROUP,
                    [(groupdn, AT.GROUP), (attr, AT.ATTRIBUTE)],
                    attrVal,
                )
            # Convert attrVal to bytes if it's not already
            if isinstance(attrVal, str):
                attrVal = attrVal.encode("utf-8")

            self.l.modify_s(groupdn, [(ldap.MOD_REPLACE, attr, attrVal)])
            if log:
                r.commit()
        else:
            self.l.modify_s(groupdn, [(ldap.MOD_REPLACE, attr, b"none")])
            self.l.modify_s(groupdn, [(ldap.MOD_DELETE, attr)])
        return 0

    def changeUserPasswd(self, uid, passwd, oldpasswd=None, bind=False):
        """
        Change LDAP user password (userPassword field)

        @param uid: user id
        @type  uid: str
        @param passwd: non encrypted password
        @type  passwd: str
        @param bind: bind as user
        @type  bind: bool
        """
        userdn = self.searchUserDN(uid)
        r = AF().log(PLUGIN_NAME, AA.BASE_MOD_USER_PASSWORD, [(userdn, AT.USER)])

        # bind the ldap with the user
        if bind:
            ldapConn = LDAPConnection(self.config).get()
            ldapConn.simple_bind_s(userdn, str(oldpasswd))
        # bind the ldap with admin user
        else:
            ldapConn = self.l

        if self.config.passwordscheme == "passmod":
            try:
                ldapConn.passwd_s(userdn, None, str(passwd))
            except ldap.CONSTRAINT_VIOLATION as e:
                if (
                    "info" in e.message
                    and e.message["info"] != "Password fails quality checking policy"
                ):
                    raise e
                # if the quality test pass, the password was rejected by
                # OpenLDAP because it is too short
                p = Popen(
                    ["mmc-password-helper", "-v", "-c"],
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                out, err = p.communicate(input=str(passwd))
                e.message["info"] = (
                    out.strip() if p.returncode != 0 else "The password is too short"
                )
                raise ldap.CONSTRAINT_VIOLATION(e.message)
        else:
            userpassword = self._generatePassword(passwd)
            ldapConn.modify_s(
                userdn, [(ldap.MOD_REPLACE, "userPassword", userpassword)]
            )

        # Run ChangeUserPassword hook
        self.runHook("base.changeuserpassword", uid, passwd)
        r.commit()

    def delUser(self, uid, home):
        """
        Delete an user
        @param uid: uid of the user.
        @type  uid: str

        @param home: if =1 delete home directory
        @type  home: int
        """
        userdn = self.searchUserDN(uid)
        r = AF().log(PLUGIN_NAME, AA.BASE_DEL_USER, [(userdn, AT.USER)])
        # Run delUser hook
        self.runHook("base.deluser", uid)

        if home and self.userHomeAction:
            homedir = self.getDetailedUser(uid)["homeDirectory"][0]
            if os.path.exists(homedir):
                shutil.rmtree(homedir)

        self.delRecursiveEntry(userdn)
        r.commit()
        return 0

    def delRecursiveEntry(self, path):
        """
        Delete an entry, del recursive leaf

        @param path: credential name in an ldap directory
            ex: "cn=admin, ou=Users, ou=ExObject, dc = lo2k, dc= net"
        @type path: str
        """

        # getAllLeaf and delete it
        for entry in self.getAllLeafs(path):
            self.delRecursiveEntry(entry)

        try:
            self.l.delete_s(path)
        except ldap.LDAPError as e:
            errObj = errorMessage("ldapUserGroupControl::delRecursiveEntry()")
            errObj.addMessage(f"error: deleting {path}")
            errObj.addMessage("ldap.LDAPError:")
            errObj.addMessage(e)
            return errObj.errorArray()
        return 0

    def getAllLeafs(self, path):
        """
        return all leafs of a specified path

           @param path: credential name in an ldap directory
           ex: "ou=addr, cn=admin, ou=Users, ou=ExObject, dc = lo2k, dc= net"

        """
        searchScope = ldap.SCOPE_ONELEVEL

        try:
            ldap_result_id = self.l.search(path, searchScope)
            result_set = []
            while True:
                result_type, result_data = self.l.result(ldap_result_id, 0)
                if result_data == []:
                    break
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)

        except ldap.LDAPError as e:
            print(e)

        # prepare array for processing
        resArr = []

        for item in result_set:
            resArr.extend(entry[0] for entry in item)
        resArr.sort()

        return resArr

    def delGroup(self, group):
        """
        Remove a group
        /!\ baseGroupsDN based on INI file

        @param group: group name (not full LDAP path)
        @type group: str
        """
        groupdn = f"cn={group},{self.baseGroupsDN}"
        # get gidNumber for group
        ldapObj = ldapUserGroupControl()
        gid = ldapObj.getDetailedGroup(group)["gidNumber"][0]
        # check if some users have this group as primary group
        result = self.l.search_s(
            self.baseUsersDN, ldap.SCOPE_SUBTREE, f"gidNumber={gid}"
        )
        if len(result) > 0:
            return 2
        r = AF().log(PLUGIN_NAME, AA.BASE_DEL_GROUP, [(groupdn, AT.GROUP)])
        self.l.delete_s(groupdn)
        r.commit()
        return 0

    def getEntry(self, dn):
        """
        Return a raw LDAP entry
        """
        attrs = []
        attrib = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, attrs = attrib[0]
        return copy.deepcopy(attrs)

    def getUserEntry(self, uid, base=None, operational=False):
        """
        Search a user entry and returns the raw LDAP entry content of a user.

        @param uid: user ID
        @type uid: str

        @param base: LDAP base scope where to look for
        @type base: str

        @param operational: if True, LDAP operational attributes are also returned
        @type operational: bool

        @return: full raw ldap array (dictionnary of lists)
        @type: dict
        """
        userdn = self.searchUserDN(uid)
        attrs = []
        myattrlist = ["+", "*"] if operational else None
        attrib = self.l.search_s(userdn, ldap.SCOPE_BASE, attrlist=myattrlist)
        c, attrs = attrib[0]
        newattrs = copy.deepcopy(attrs)

        if "krb5Key" in newattrs:
            del newattrs["krb5Key"]

        return newattrs

    getDetailedUser = getUserEntry

    def getUserEntryById(self, id, base=None):
        """
        Search a user entry and returns the raw LDAP entry content of a user.

        @param id: user uidNumber
        @type id: int

        @param base: LDAP base scope where to look for
        @type base: str

        @return: full raw ldap array (dictionnary of lists)
        @type: dict
        """
        if not base:
            base = self.baseUsersDN
        ret = self.search(f"uidNumber={str(id)}", base)
        newattrs = {}
        if ret:
            for result in ret:
                c, attrs = result[0]
                newattrs = copy.deepcopy(attrs)
                break

        if "krb5Key" in newattrs:
            del newattrs["krb5Key"]

        return newattrs

    getDetailedUserById = getUserEntryById

    def searchUserDN(self, uid):
        """
        Search and return the DN of the given user entry.

        @param uid: User ID (login)
        @type uid: str

        @return: the DN of the user entry, or an empty string if not found
        @rtype: str
        """
        if isinstance(uid, xmlrpc.client.Binary):
            _uid = str(uid)
        elif type(uid) is bytes:
            _uid = uid.decode("utf-8")
        else:
            _uid = uid

        if uid == "root":
            ret = self.config.username
        elif result := self.l.search_s(
            self.config.baseUsersDN, ldap.SCOPE_SUBTREE, f"uid={_uid}"
        ):
            ret, entry = result[0]
        else:
            ret = ""
        return ret

    def getDetailedGroup(self, group, base=None):
        """
        Return raw ldap info on a group

        @param group: group name
        @type group: str

        @return: full raw ldap array (dictionnary of lists)
        @type: dict

        """
        if not base:
            base = self.baseGroupsDN
        cn = f"cn={group}, {base}"
        attrs = []
        attrib = self.l.search_s(cn, ldap.SCOPE_BASE)
        c, attrs = attrib[0]
        return copy.deepcopy(attrs)

    def getDetailedGroupById(self, id, base=None):
        """
        Return raw ldap info on a group

        @param uid: gidNumber
        @type uid: int

        @return: full raw ldap array (dictionnary of lists)
        @type: dict
        """
        if not base:
            base = self.baseGroupsDN
        ret = self.search(f"gidNumber={str(id)}", base)
        newattrs = {}
        if ret:
            for result in ret:
                c, attrs = result[0]
                newattrs = copy.deepcopy(attrs)
                break

        return newattrs

    def getUserGroups(self, pattern):
        """
        return all groups who contain memberUid of this user

        @param pattern: search pattern
        @type pattern: str

        @return: return list with all groups who contain memberUid of pattern user
        @rtype: list
        """
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None

        searchFilter = f"memberUid={pattern}"

        try:
            ldap_result_id = self.l.search(
                self.baseGroupsDN, searchScope, searchFilter, retrieveAttributes
            )
            result_set = []
            while True:
                result_type, result_data = self.l.result(ldap_result_id, 0)
                if result_data == []:
                    break
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)

        except ldap.LDAPError as e:
            print(e)

        # prepare array for processing
        resArr = []

        for item in result_set:
            for entry in item:
                try:
                    cn = entry[1]["cn"][0]
                    resArr.append(cn)
                except:
                    pass

        return cSort(resArr)

    def search(
        self, searchFilter="", basedn=None, attrs=None, scope=ldap.SCOPE_SUBTREE
    ):
        """
        @param searchFilter: LDAP search filter
        @type searchFilter: unicode
        """
        # searchFilter = searchFilter.encode("utf-8")
        searchFilter = searchFilter
        if not basedn:
            basedn = self.baseDN
        result_set = []
        ldap_result_id = self.l.search(basedn, scope, searchFilter, attrs)
        while True:
            try:
                result_type, result_data = self.l.result(ldap_result_id, 0)
            except ldap.NO_SUCH_OBJECT:
                result_data = []
            if not result_data:
                break
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)

        return result_set

    def searchUser(self, pattern="", base=None):
        """
        search a user in ldapdirectory
        @param pattern : pattern for search filter
          ex: *admin*, luc*
        @type pattern : str

         if empty, return all user

        search begin at baseUsersDN (defines in INIFILE)

        @return: sorted list by uid of all users corresponding to the search filter
        @rtype: list
        """
        if pattern == "":
            pattern = "*"
        return self.searchUserAdvance(f"uid={pattern}", base)[1]

    def searchUserAdvance(self, pattern="", base=None, start=None, end=None):
        """
        search a user in ldapdirectory
        @param pattern : pattern for search filter
          ex: *admin*, luc*
        @type pattern : str

         if empty, return all user

        search begin at baseUsersDN (defines in INIFILE)

        @return: list of all users correspond criteria
        @rtype: list
        """
        if not base:
            base = self.baseUsersDN
        searchFilter = "uid=*" if pattern == "" else pattern
        monoattrs = ["uid", "sn", "givenName", "mail"]
        result_set = self.search(
            searchFilter,
            base,
            monoattrs + ["telephoneNumber", "loginShell", "objectClass"],
            ldap.SCOPE_ONELEVEL,
        )

        # prepare array for processing
        resArr = {}
        uids = []
        for i in range(len(result_set)):
            for entry in result_set[i]:
                localArr = {}
                for field in monoattrs:
                    try:
                        localArr[field] = entry[1][field][0]
                    except KeyError:
                        # If the field does not exist, put an empty value
                        localArr[field] = ""

                try:
                    localArr["telephoneNumber"] = entry[1]["telephoneNumber"]
                except KeyError:
                    localArr["telephoneNumber"] = []

                localArr["obj"] = entry[1]["objectClass"]

                enabled = 0
                try:
                    shell = entry[1]["loginShell"][0]
                    if shell != self.defaultShellDisable:
                        enabled = 1
                except KeyError:
                    pass
                localArr["enabled"] = enabled

                # Filter SAMBA machine account that ends with $
                if localArr["uid"][-1] != "$":
                    resArr[localArr["uid"]] = localArr
                    uids.append(localArr["uid"])

        uids = cSort(uids)
        total = len(uids)
        if start != None and end != None:
            uids = uids[int(start) : int(end)]
        ret = [resArr[uid] for uid in uids]
        return (total, ret)

    def getMembers(self, group):
        """
        return all member of a specified group

        @param group: group name
        @type group: str

        @return: return memberuid attribute.
        @rtype: list
        """
        result_set = self.search(
            f"cn={group}", self.baseGroupsDN, None, ldap.SCOPE_ONELEVEL
        )

        # prepare array for processing
        resArr = []

        for i in range(len(result_set)):
            for entry in result_set[i]:
                try:
                    resArr = entry[1]["memberUid"]

                except:
                    pass

        return cSort(resArr)

    def existUser(self, uid):
        """
        Test if the user exists in the LDAP.

        @param uid: user uid
        @type uid: str

        @return: return True if a user exist in the ldap BaseDN directory
        @rtype: boolean
        """
        uid = uid.strip()
        return len(self.searchUser(uid)) == 1 if len(uid) else False

    def existGroup(self, group):
        """
        Test if the group exists in the LDAP.

        @param group: group name
        @type group: str

        @return: return True if a group exist in the LDAP directory
        @rtype: boolean
        """
        group = group.strip()
        return len(self.searchGroup(group)) == 1 if len(group) else False

    def searchGroup(self, pattern="*", base=None, minNumber=0):
        if not base:
            base = self.baseGroupsDN
        result_set = self.search(f"cn={pattern}", base, None, ldap.SCOPE_ONELEVEL)

        # prepare array for processing
        resArr = {}

        for i in range(len(result_set)):
            for entry in result_set[i]:
                try:
                    try:
                        description = entry[1]["description"][0]
                    except:
                        description = ""

                    gidNumber = int(entry[1]["gidNumber"][0])

                    try:
                        numbr = len(entry[1]["memberUid"])
                    except:
                        numbr = 0

                    if gidNumber >= minNumber:
                        cn = entry[1]["cn"][0]

                        cell = [cn, description, numbr]
                        resArr[cn.lower()] = cell

                except:
                    pass

        return resArr

    def maxUID(self):
        """
        fetch maxUID

        @return: maxUid in ldap directory
        @rtype: int
        """

        self.logger.warning("API call deprecated, use freeUID instead.")

        ret = [
            self.search("uid=*", self.baseUsersDN, ["uidNumber"], ldap.SCOPE_SUBTREE)
        ]

        # prepare array for processing
        maxuid = 0
        for result_set in ret:
            for i in range(len(result_set)):
                for entry in result_set[i]:
                    try:
                        uidNumber = int(entry[1]["uidNumber"][0])
                    except KeyError:
                        uidNumber = -1

                    maxuid = max(maxuid, uidNumber)
            maxuid = max(maxuid, self.uidStart)
        return maxuid

    def freeUID(self):
        """
        Returns the first free UID available for posixAccounts
        """

        accounts = self.search(
            "objectClass=posixAccount", self.baseDN, ["uidNumber"], ldap.SCOPE_SUBTREE
        )
        uidNumbers = [int(account[0][1]["uidNumber"][0]) for account in accounts]
        uid = self.uidStart
        while uid in uidNumbers:
            uid = uid + 1

        return uid

    def removeUserObjectClass(self, uid, className):
        # Create LDAP path
        userdn = self.searchUserDN(uid)
        attrs = []
        attrib = self.l.search_s(userdn, ldap.SCOPE_BASE)

        # fetch attributes
        c, attrs = attrib[0]
        # copy new attrs
        newattrs = copy.deepcopy(attrs)

        if className in newattrs["objectClass"]:
            indexRm = newattrs["objectClass"].index(className)
            del newattrs["objectClass"][indexRm]

        # For all element we can try to delete
        for entry in self.getAttrToDelete(userdn, className):
            for k in list(newattrs.keys()):
                if k.lower() == entry.lower():
                    del newattrs[k]  # delete it

        # Apply modification
        mlist = ldap.modlist.modifyModlist(attrs, newattrs)
        self.l.modify_s(userdn, mlist)

    def removeGroupObjectClass(self, group, className):
        # Create LDAP path
        group = group.encode("utf-8")
        cn = f"cn={group}, {self.baseGroupsDN}"
        attrs = []
        attrib = self.l.search_s(cn, ldap.SCOPE_BASE)

        # fetch attributes
        c, attrs = attrib[0]
        # copy new attrs
        newattrs = copy.deepcopy(attrs)

        if className in newattrs["objectClass"]:
            indexRm = newattrs["objectClass"].index(className)
            del newattrs["objectClass"][indexRm]

        # For all element we can try to delete
        for entry in self.getAttrToDelete(cn, className):
            for k in list(newattrs.keys()):
                if k.lower() == entry.lower():
                    del newattrs[k]  # delete it

        # Apply modification
        mlist = ldap.modlist.modifyModlist(attrs, newattrs)
        self.l.modify_s(cn, mlist)

    def getAttrToDelete(self, dn, className):
        """retrieve all attributes to delete wich correspond to param schema"""

        arrObjectList = self.getEntry(dn)["objectClass"]
        indexRm = arrObjectList.index(className)

        # Remove deleting objectList from getSchema routine
        del arrObjectList[indexRm]

        attrList = self.getSchema(className)

        badList = set()
        for schemaName in arrObjectList:
            badList = badList | self.getSchema(schemaName)

        attrList = attrList - badList

        return attrList

    def getSchema(self, schemaName):
        """
         return schema corresponding schemaName
        @param schemaName: schema name
            ex: person, account, OxUserObject
        @type schemaName: str

        @return: schema parameters
        @type list

        for more info on return type, reference to ldap.schema
        """
        subschemasubentry_dn, schema = ldap.schema.urlfetch(self.config.ldapurl)
        schemaAttrObj = schema.get_obj(ldap.schema.ObjectClass, schemaName)
        if schemaAttrObj is not None:
            return set(schemaAttrObj.must) | set(schemaAttrObj.may)
        else:
            return set()

    def posixGroupIsRFC2307bis(self):
        """
        Test if posixGroup is from RFC2307bis schema

        @return: True if posixGroup is from RFC2307bis schema False otherwise
        @type boolean
        """
        subschemasubentry_dn, schema = ldap.schema.urlfetch(self.config.ldapurl)
        schemaAttrObj = schema.get_obj(ldap.schema.ObjectClass, "posixGroup")
        return schemaAttrObj.kind == 2 if schemaAttrObj is not None else False

    def maxGID(self):
        """
        fetch maxGID

        @return: maxGid in ldap directory
        @rtype: int
        """
        result_set = self.search("cn=*", self.baseGroupsDN, None, ldap.SCOPE_ONELEVEL)
        maxgid = 0
        for i in range(len(result_set)):
            for entry in result_set[i]:
                try:
                    gidNumber = int(entry[1]["gidNumber"][0])
                except KeyError:
                    gidNumber = -1
                maxgid = max(maxgid, gidNumber)
        return max(maxgid, self.gidStart)

    def moveHome(self, uid, newHome):
        """
        Move an home directory.

        @param uid: user name
        @type uid: str

        @param newHome: new home path
        ex: /home/coin
        @type newHome: str
        """
        oldHome = self.getDetailedUser(uid)["homeDirectory"][0]
        if newHome != oldHome:
            userdn = self.searchUserDN(uid)
            r = AF().log(PLUGIN_NAME, AA.BASE_MOVE_USER_HOME, [(userdn, AT.USER)])
            self.changeUserAttributes(uid, "homeDirectory", newHome)
            if self.userHomeAction:
                shutil.move(oldHome, newHome)
            r.commit()

    def addOu(self, ouname, ldappath):
        """
        add an organizational Unit to an ldap entry

        @param ouname: organizational unit name
        @type ouname: str

        @param ldappath: ldap full path
        @type ldappath: str
        """
        addrdn = f"ou={ouname}, {ldappath}"
        addr_info = {
            "ou": bytes(ouname, encoding="utf8"),
            "objectClass": (
                bytes("organizationalUnit", encoding="utf8"),
                bytes("top", encoding="utf8"),
            ),
        }
        attributes = list(list(addr_info.items()))
        try:
            self.l.add_s(addrdn, attributes)
            self.logger.info(f"Created OU {addrdn}")
        except ldap.ALREADY_EXISTS:
            pass
        else:
            r = AF().log(
                PLUGIN_NAME, AA.BASE_ADD_OU, [(addrdn, AT.ORGANIZATIONAL_UNIT)]
            )
            r.commit()

    def createAuthToken(self, user, server, lang):
        if "@" in user:
            ldapUsers = self.searchUserAdvance(f"mail={user}")
        else:
            ldapUsers = self.searchUserAdvance(f"uid={user}")

        if ldapUsers[0] == 1:
            uid = ldapUsers[1][0]["uid"]
        else:
            return False

        tokensdb = shelve.open(os.path.join(localstatedir, "lib", "mmc", "tokens.db"))
        token = f"{str(uuid1())}#{uid}#{server}#{lang}#{time.time()}"
        encoded_token = base64.urlsafe_b64encode(token)
        self.logger.debug(f"Created token for {uid} : {encoded_token}")
        tokensdb[uid] = encoded_token
        tokensdb.close()

        self.runHook("base.usertoken", uid, encoded_token)

        return True

    def validateAuthToken(self, user, token):
        current_timestamp = time.time()
        try:
            decoded_token = base64.urlsafe_b64decode(token)
            uuid, uid, server, lang, timestamp = decoded_token.split("#")
        except:
            return False

        if user != uid:
            return False

        # 15 min expiration
        if current_timestamp - float(timestamp) > 900:
            return False

        tokensdb = shelve.open(os.path.join(localstatedir, "lib", "mmc", "tokens.db"))
        if uid in tokensdb and tokensdb[uid] == token:
            self.logger.debug("User token is valid")
            del tokensdb[uid]
            tokensdb.close()
            return True

        tokensdb.close()
        return False


ldapUserGroupControl = LdapUserGroupControl
###########################################################################################
############## ldap authentification
###########################################################################################


class BaseLdapAuthenticator(AuthenticatorI):
    def __init__(self, conffile=INI, name="baseldap"):
        AuthenticatorI.__init__(self, conffile, name)

    def authenticate(self, user, password):
        ldapObj = ldapAuthen(user, password)
        ret = AuthenticationToken()
        if ldapObj.isRightPass():
            userentry = ldapObj.getUserEntry()
            # Check that the login string exactly matches LDAP content
            if userentry and user != "root":
                _user = userentry[0][1]["uid"][0]
                if isinstance(_user, bytes):
                    _user = _user.decode("utf-8")
                if _user == user:
                    ret = AuthenticationToken(True, user, password, userentry[0])
            else:
                ret = AuthenticationToken(True, user, password, None)
        return ret

    def validate(self):
        return True


class ldapAuthen:
    """
    class for LDAP authentification

    bind with constructor parameters to an ldap directory.
    bind return error if login/password give to constructor isn't valid
    """

    def __init__(self, login, password, conffile=None):
        """
        Initialise LDAP connection

        @param login: login
        @type login: str

        @param password: not encrypted password
        @type password: str

        Try a LDAP bind.

        self.result is True if the bind is successful
        If there are any error, self.result is False and a ldap
        exception will be raised.
        """
        config = PluginConfigFactory.new(BasePluginConfig, "base", conffile)
        conn = LDAPConnection(config)
        l = conn.get()

        # if login == root, try to connect as the LDAP manager
        if login == "root":
            username = config.username
        else:
            username = LdapUserGroupControl().searchUserDN(login)
        self.userdn = username

        # If the passwd has been encoded in the XML-RPC stream, decode it
        if isinstance(password, xmlrpc.client.Binary):
            password = str(password)

        self.result = False
        try:
            l.simple_bind_s(username, password)
            self.result = True
        except ldap.INVALID_CREDENTIALS:
            pass
        self.l = l

    def isRightPass(self):
        """
        @return: Return True if the class constructor has successfully
        authenticated the user.
        @rtype: bool
        """
        return self.result

    def getUserEntry(self):
        """
        Use the LDAP administrator account to get the user entry, because the
        user account may now have sufficient rights to read her entry.
        """
        lugc = ldapUserGroupControl()
        try:
            ret = lugc.l.search_s(self.userdn, ldap.SCOPE_BASE)
        except ldap.NO_SUCH_OBJECT:
            # If the user is defined in OpenLDAP slapd.conf, we may bind even
            # if the user has no LDAP entry.
            ret = None
        return ret


class GpoManager:
    def __init__(self, service, conffile=None, gpoCreate=True):
        """
        @param service: name of the service (sub ou of the GPO root)
        @param gpoCreate: If True, create the needed OU for GPO management of the service
        """
        self.l = ldapUserGroupControl(conffile)
        self.service = service
        if gpoCreate:
            self.addServiceOuGPO()

    def _getDN(self):
        return f"ou={self.service},{self.l.gpoDN}"

    def _getGpoDN(self, gpoName):
        return f"cn={gpoName},{self._getDN()}"

    def addRootGpoOu(self):
        """
        Add a main GPO organizational unit
        """
        try:
            self.l.addOu(self.l.gpoDN)
        except ldap.ALREADY_EXISTS:
            # The Ou already exists
            pass

    def addServiceOuGPO(self):
        """
        Add a main ou for the current service under main GPO ou.
        """
        try:
            self.l.addOu(self.service, self.l.gpoDN)
        except ldap.ALREADY_EXISTS:
            # The Ou already exists
            pass
        except ldap.STRONG_AUTH_REQUIRED:
            # We have this error if we try to write into a replicat
            # Just ignore
            pass

    def add(self, gpoName, ACLs):
        """
        Add a GPO

        @param gpoName: Name of the GPO
        @param ACLs: ACLs dict
        @type ACLs: dict
        """
        # creating group skel
        group_info = {"cn": gpoName, "objectclass": ("GroupPolicy", "top"), "ACL": []}
        for aclname in ACLs:
            group_info["ACL"].append(f"{aclname}:{ACLs[aclname]}")
        entry = f"cn={gpoName},{self._getDN()}"
        attributes = list(list(group_info.items()))
        self.l.l.add_s(entry, attributes)

    def delete(self, gpoName):
        """
        Delete a GPO

        @param gpoName: Name of the GPO
        """
        entry = f"cn={gpoName},{self._getDN()}"
        self.l.l.delete_s(entry)

    # User GPO management methods

    def addUserToGPO(self, uid, gpoName):
        """
        Add an user to a GPO.

        The DN of the user is put in a member field of the GPO.

        @param gpoName: name of the GPO
        @uid: uid of the user name
        """
        userdn = self.searchUserDN(uid)
        try:
            self.l.l.modify_s(
                self._getGpoDN(gpoName), [(ldap.MOD_ADD, "member", userdn)]
            )
        except ldap.TYPE_OR_VALUE_EXISTS:
            # Value already set
            pass

    def delUserFromGPO(self, uid, gpoName):
        """
        Del an user from a GPO.

        @param gpoName: name of the GPO
        @param uid: uid of the user name
        """
        userdn = self.searchUserDN(uid)
        try:
            self.l.l.modify_s(
                self._getGpoDN(gpoName), [(ldap.MOD_DELETE, "member", userdn)]
            )
        except ldap.NO_SUCH_ATTRIBUTE:
            # Value already deleted
            pass

    def getUsersFromGPO(self, gpoName):
        """
        Return all members of a GPO
        """
        ret = self.l.search(
            searchFilter=f"cn={gpoName}", basedn=self._getDN(), attrs=["member"]
        )
        members = []
        for item in ret:
            attrs = item[0][1]
            try:
                members.extend(
                    member for member in attrs["member"] if member.startswith("uid=")
                )
            except KeyError:
                # There is no member in this group
                pass
        return members

    # Group GPO management methods

    def addGroupToGPO(self, group, gpoName):
        """
        Add a group to a GPO.

        The DN of the group is put in a member field of the GPO.

        @param group: group name
        @param gpoName: name of the GPO
        """
        dn = f"cn={group},{self.l.baseGroupsDN}"
        try:
            self.l.l.modify_s(self._getGpoDN(gpoName), [(ldap.MOD_ADD, "member", dn)])
        except ldap.TYPE_OR_VALUE_EXISTS:
            # Value already set
            pass

    def delGroupFromGPO(self, group, gpoName):
        """
        Del n group from a GPO.

        @param group: group name
        @param gpoName: name of the GPO
        """
        dn = f"cn={group},{self.l.baseGroupsDN}"
        try:
            self.l.l.modify_s(
                self._getGpoDN(gpoName), [(ldap.MOD_DELETE, "member", dn)]
            )
        except ldap.NO_SUCH_ATTRIBUTE:
            # Value already deleted
            pass

    def getGroupsFromGPO(self, gpoName):
        """
        Return all group members of a GPO
        """
        ret = self.l.search(
            searchFilter=f"cn={gpoName}", basedn=self._getDN(), attrs=["member"]
        )
        members = []
        for item in ret:
            attrs = item[0][1]
            try:
                members.extend(
                    member for member in attrs["member"] if member.startswith("cn=")
                )
            except KeyError:
                # There is no member in this group
                pass
        return members

    # Other methods

    def getResourceGpo(self, dn, gpoName):
        """
        Return the resources name to which an user is member

        @param dn: user name or group name to search for(full DN)
        @param gpoName: name of the GPO to search for
        """
        ret = self.l.search(
            searchFilter=f"cn={gpoName}_*", basedn=self._getDN(), attrs=["member"]
        )
        resources = []
        for item in ret:
            cn = item[0][0]
            attrs = item[0][1]
            try:
                if dn in attrs["member"]:
                    resource = cn.split(",")[0].split("_")[1]
                    resources.append(resource)
            except KeyError:
                pass
        return resources


### Computer


class Computers(ldapUserGroupControl, ComputerI):
    def __init__(self, conffile=None):
        ldapUserGroupControl.__init__(self, conffile)
        config = PluginConfigFactory.new(BasePluginConfig, "base")
        self.baseComputersDN = config.baseComputersDN

    def getComputer(self, ctx, filt=None, empty_macs=False):
        """ """
        pass  # TODO...

    def getMachineMac(self, ctx, filt=None):
        pass  # TODO...

    def getMachineIP(self, ctx, filt=None):
        pass  # TODO...

    def getComputersList(self, ctx, filt=None):
        """
        Return a list of computers

        @param filter: computer name filter
        @type filter: str

        @return: LDAP results
        @rtype:
        """
        # in ldap we only filter on names for the moment
        filt = filt["name"]
        filt = f"*{filt}*" if filt else "*"
        return self.l.search_s(
            self.baseComputersDN,
            ldap.SCOPE_SUBTREE,
            f"(&(objectClass=computerObject)(|(cn={filt})(displayName={filt})))",
            None,
        )

    def getTotalComputerCount(self):
        return 0

    def getComputerCount(self, ctx, params):
        """
        Never return the number of computers, we are in a LDAP, so we can't acces to a limited host list
        """
        return 0

    def getRestrictedComputersListLen(self, ctx, filt):
        """ """
        return len(self.getComputersList(filt))

    def getRestrictedComputersList(self, ctx, min, max, filt, advanced, justid):
        """
        we can't do that directly in ldap, so we do it in python, just to return less xml...
        """
        ret = []
        retour = self.getComputersList(filt)
        i = 0
        for computer in retour:
            if i >= min and i < max:
                ret.append(computer)
            if i == max:
                break
            i += 1
        return ret

    def canAddComputer(self):
        return True

    def addComputer(self, ctx, params):
        """
        Add a computer in the main computer list

        @param name: name of the computer. It should be a fqdn
        @type name: str

        @param comment: a comment for the computer list
        @type comment: str

        @return: the machine uuuid
        @rtype: str
        """
        name = params["computername"]
        comment = params["computerdescription"].encode("utf-8")
        uuid = str(uuid1())
        data = {
            "objectUUID": [uuid],
            "cn": [name],
            "objectClass": ["computerObject"],
        }
        dn = f"objectUUID={uuid},{self.baseComputersDN}"
        if comment:
            data["displayName"] = [comment]
        logging.getLogger().info("adding a computer")
        logging.getLogger().info(dn)
        logging.getLogger().info(data)
        self.l.add_s(dn, ldap.modlist.addModlist(data))
        return uuid

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid, backup):
        """
        Remove a computer, given its uuid
        """
        dn = f"objectUUID={uuid},{self.baseComputersDN}"
        return self.l.delete_s(dn)


class ContextMaker(ContextMakerI):
    """
    Create security context for the base plugin.
    """

    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.userdn = LdapUserGroupControl().searchUserDN(self.userid)
        return s


class RpcProxy(RpcProxyI):
    def authenticate(self, uiduser, passwd):
        """
        Authenticate an user with her/his password against a LDAP server.
        Return a Deferred resulting to true if the user has been successfully
        authenticated, else false.
        """
        d = defer.maybeDeferred(
            AuthenticationManager().authenticate, uiduser, passwd, self.session
        )
        d.addCallback(ProvisioningManager().doProvisioning)
        d.addCallback(self._cbAuthenticate)
        return d

    ldapAuth = authenticate

    def tokenAuthenticate(self, user, token):
        d = defer.maybeDeferred(LdapUserGroupControl().validateAuthToken, user, token)
        d.addCallback(self._cbTokenAuthenticate)
        return d

    def _cbAuthenticate(self, token):
        """
        Callback for authentication.
        """
        ret = token.isAuthenticated()
        if ret:
            userdn = LdapUserGroupControl().searchUserDN(token.login)
            record = AF().log(PLUGIN_NAME, AA.BASE_AUTH_USER, [(userdn, AT.USER)])
            record.commit()
        return ret

    def _cbTokenAuthenticate(self, result):
        return result

    def hasComputerManagerWorking(self):
        """
        Returns True if the ComputerManager can effectively handle computers.
        If the driver is none, it can't be use to manage computers.
        """
        return ComputerManager().main != "none"

    def canAddComputer(self):
        return ComputerManager().canAddComputer()

    def canAssociateComputer2Location(self):
        return ComputerManager().canAssociateComputer2Location()

    def addComputer(self, params):
        ctx = self.currentContext
        ComputerManager().addComputer(ctx, params)

    def neededParamsAddComputer(self):
        return ComputerManager().neededParamsAddComputer()

    def checkComputerName(self, name):
        return ComputerManager().checkComputerName(name)

    def isComputerNameAvailable(self, locationUUID, name):
        ctx = self.currentContext
        return ComputerManager().isComputerNameAvailable(ctx, locationUUID, name)

    def canDelComputer(self):
        return ComputerManager().canDelComputer()

    def delComputer(self, uuid, backup):
        ctx = self.currentContext
        ComputerManager().delComputer(ctx, uuid, backup)

    def getComputer(self, filt=None, empty_macs=False):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getComputer(ctx, filt, empty_macs))

    def getComputersNetwork(self, filt=None):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getComputersNetwork(ctx, filt))

    def getMachineMac(self, filt=None):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getMachineMac(ctx, filt))

    def getMachineIp(self, filt=None):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getMachineIp(ctx, filt))

    def getComputerByHostnameAndMacs(self, hostname, macs):
        ctx = self.currentContext
        return xmlrpcCleanup(
            ComputerManager().getComputerByHostnameAndMacs(ctx, hostname, macs)
        )

    def getComputersName(self, filt=None):
        ctx = self.currentContext
        ret = ComputerManager().getComputersList(ctx, filt)
        if isinstance(ret, list):  # inventory
            ret = [ret[x][1]["cn"][0] for x in range(len(ret))]
        elif isinstance(ret, dict):  # glpi
            ret = [ret[x][1]["cn"][0] for x in ret]
        else:
            raise Exception("Error when parsing ComputerList result")
        # ret.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return xmlrpcCleanup(ret)

    def getComputersOS(self, uuids):
        return xmlrpcCleanup(ComputerManager().getComputersOS(uuids))

    def getComputersList(self, filt=None):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getComputersList(ctx, filt))

    def getRestrictedComputersName(self, min=0, max=-1, filt=None):
        ctx = self.currentContext
        ret = ComputerManager().getRestrictedComputersList(ctx, min, max, filt)
        ret = [ret[x][1]["cn"][0] for x in ret]
        # ret.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return xmlrpcCleanup(ret)

    def getRestrictedComputersListLen(self, filt=None):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getRestrictedComputersListLen(ctx, filt))

    def getRestrictedComputersList(
        self, min=0, max=-1, filt=None, advanced=True, justid=False
    ):
        ctx = self.currentContext
        return xmlrpcCleanup(
            ComputerManager().getRestrictedComputersList(
                ctx, min, max, filt, advanced, justid
            )
        )

    def getComputerCount(self, filt={}):
        # Mutable dict extra_css used as default argument to a method or function
        # filt = filt or {}
        ctx = self.currentContext
        return ComputerManager().getComputerCount(ctx, filt)

    def simple_computer_count(self):
        return ComputerManager().simple_computer_count()

    def getComputersListHeaders(self):
        ctx = self.currentContext
        return ComputerManager().getComputersListHeaders(ctx)


################################################################################
###### LOG VIEW CLASS
################################################################################


class LogView:
    """
    LogView class. Provide accessor to show log content
    """

    def __init__(self, logfile=f"{localstatedir}/log/ldap.log", pattern=None):
        config = PluginConfig("base")
        try:
            self.logfile = config.get("ldap", "logfile")
        except (NoSectionError, NoOptionError):
            self.logfile = logfile
        try:
            self.maxElt = config.get("LogView", "maxElt")
        except (NoSectionError, NoOptionError):
            self.maxElt = 200
        if pattern:
            self.pattern = pattern
        else:
            self.pattern = {
                "slapd-syslog": "^(?P<b>[A-z]{3}) *(?P<d>[0-9]+) (?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .* conn=(?P<conn>[0-9]+)\ (?P<opfd>op|fd)=(?P<opfdnum>[0-9]+) (?P<op>[A-Za-z]+) (?P<extra>.*)$",
                "fds-accesslog": "^\[(?P<d>[0-9]{2})/(?P<b>[A-z]{3})/(?P<y>[0-9]{4}):(?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .*\] conn=(?P<conn>[0-9]+)\ (?P<opfd>op|fd)=(?P<opfdnum>[0-9]+) (?P<op>[A-Za-z]+)(?P<extra> .*|)$",
            }

    def isLogViewEnabled(self):
        # Disable logview module if the plugin services is enabled
        return "services" not in PluginManager().getEnabledPluginNames()

    def revReadlines(self, arg, bufsize=8192):
        """
        Reversed readlines
        Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496941/index_txt
        """
        f = open(arg.encode("utf-8"), "rb")
        f.seek(0, 2)  # go to the end
        leftover = ""
        while f.tell():
            if f.tell() < bufsize:
                bufsize = f.tell()
            f.seek(-bufsize, 1)
            in_memory = f.read(bufsize) + leftover
            f.seek(-bufsize, 1)
            lines = in_memory.split("\n")
            reversed = lines[1:]
            reversed.reverse()
            yield from reversed
            leftover = lines[0]
        yield leftover

    def getLog(self, filter=""):
        """
        Parse the log lines containing the filter string and matching the given patterns.
        Try to return a list containing self.maxElt
        """
        ret = []
        count = 0
        for line in self.revReadlines(self.logfile):
            if filter in line:
                if parsed := self.parseLine(line):
                    ret.append(parsed)
                    count = count + 1
                    if count > self.maxElt:
                        break
        return ret

    def parseLine(self, line):
        ret = None
        patternKeys = sorted(self.pattern.keys())
        # We try each pattern until we found one that works
        for pattern in patternKeys:
            if sre := re.search(self.pattern[pattern], line):
                if res := sre.groupdict():
                    # Use current year if not set
                    if "Y" not in res:
                        res["Y"] = str(localtime()[0])
                    timed = strptime(
                        f'{res["b"]} {res["d"]} {res["Y"]} {res["H"]} {res["M"]} {res["S"]}',
                        "%b %d %Y %H %M %S",
                    )
                    res["time"] = mktime(timed)
                    ret = res
                    break
        return ret
