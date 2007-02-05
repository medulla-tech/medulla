# -*- coding: utf-8; -*-
#
# (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of LMC.
#
# LMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import os.path
import re
import logging
import ldap.modlist
import fileinput
import tempfile
from lmc.plugins.base import ldapUserGroupControl
from time import mktime, strptime

# Try to import module posix1e
try:
    from posix1e import *
except ImportError:
    logger = logging.getLogger()
    logger.error("\nPython module pylibacl not found...\nPlease install :\n  * python-pylibacl on Debian/Ubuntu\n  * python-libacl on CentOS 4.3\n  * pylibacl on Mandriva 2006\n")
    raise

from lmc.support.errorObj import errorMessage
from lmc.support.lmcException import *
from lmc.support import lmctools
import lmc.plugins.base
from lmc.support.config import *
from lmc.plugins.base import ldapUserGroupControl

from lmc.support.lmctools import shProcessProtocol
from lmc.support.lmctools import generateBackgroundProcess
from twisted.internet import reactor

INI = "/etc/lmc/plugins/samba.ini"

VERSION = "1.1.1"
APIVERSION = "2:0:1"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
     this function define if the module "base" can be activated.
     @return: return True if this module can be activate
     @rtype: boolean
    """
    configParser = lmctools.getConfigParser("samba")
    logger = logging.getLogger()

    if (configParser.get("main","disable")=="1"):
        logger.info("samba plugin disabled by configuration.")
        return False

    try:
        ldapObj = ldapUserGroupControl()
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False

    # Test if the Samba LDAP schema is available in the directory
    try:
         schema = ldapObj.getSchema("sambaSamAccount")
         if len(schema) <= 0:
             logger.error("Samba schema are not included in LDAP directory");
             return False
    except:
        logger.exception("invalid schema")
        return False

    # Verify if init script exist
    config = SambaConfig("samba")
    init = config.samba_init_script
    if not os.path.exists(init):
        logger.error(init + " does not exist")
        return False

    # Verify if samba conf file exist
    conf = config.samba_conf_file
    if not os.path.exists(conf):
        logger.error(conf + " does not exist")
        return False

    # If SAMBA is defined as a PDC, make extra checks
    smbconf = smbConf()
    if smbconf.isPdc():
        # Check that a sambaDomainName entry is in LDAP directory
        samba = sambaLdapControl()
        domainInfos = samba.getDomain()
        if not domainInfos:
            logger.error("Can't find sambaDomainName entry in LDAP for domain %s. Please check your SAMBA LDAP configuration." % smbconf.getContent("global", "workgroup"));
            return False
        # Check that Domain Computers group exists
        # We need it to put a machine account in the right group when joigning it to the domain
        if not samba.getDomainComputersGroup():
            logger.error("Can't find sambaGroupMapping entry in LDAP corresponding to 'Domain Computers' group. Please check your SAMBA LDAP configuration.");
            return False
        # Check that Domain Admins group exists
        if not samba.getDomainAdminsGroup():
            logger.error("Can't find sambaGroupMapping entry in LDAP corresponding to 'Domain Admins' group. Please check your SAMBA LDAP configuration.");
            return False
        # Check that Domain Guests group exists
        if not samba.getDomainGuestsGroup():
            logger.error("Can't find sambaGroupMapping entry in LDAP corresponding to 'Domain Guests' group. Please check your SAMBA LDAP configuration.");
            return False
        # Check that Domain Users group exists
        if not samba.getDomainUsersGroup():
            logger.error("Can't find sambaGroupMapping entry in LDAP corresponding to 'Domain Users' group. Please check your SAMBA LDAP configuration.");
            return False

    return True

def isSmbAntiVirus():
    return os.path.exists(SambaConfig("samba").clam_av_so)

def getDetailedShares():
    """Get a complete array of information about all shares"""
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    resList=smbObj.getDetailedShares()
    return resList

def getACLOnShare(name):
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    return smbObj.getACLOnShare(name)

def getAdminUsersOnShare(name):
    return smbConf(SambaConfig("samba").samba_conf_file).getAdminUsersOnShare(name)

def getDomainAdminsGroup():
    return sambaLdapControl().getDomainAdminsGroup()

def isBrowseable(name):
    return smbConf(SambaConfig("samba").samba_conf_file).isBrowseable(name)

def addShare(name, comment, usergroups, permAll, admingroups, browseable = True, av = 0):
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    smbObj.addShare(name, comment, usergroups, permAll, admingroups, browseable, av)
    smbObj.save()

def delShare(name, file):
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    smbObj.delShare(name, file)
    smbObj.save()
    return 0

def shareInfo(name):
    """get an array of information about a share"""
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    return smbObj.shareInfo(name)

def getSmbInfo():
    """get main information of global section"""
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    return smbObj.getSmbInfo()

def smbInfoSave(pdc, homes, options):
    """save information about global section"""
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    return smbObj.smbInfoSave(pdc, homes, options)

def isPdc():
    try: smbObj = smbConf(SambaConfig("samba").samba_conf_file)
    except: raise lmcException('cannot open conffile')
    return smbObj.isPdc()

def backupShare(share, media, login):
    smbObj = smbConf(SambaConfig("samba").samba_conf_file)

    configParser = lmctools.getConfigParser("base")
    path = configParser.get("backup-tools", "path")
    destpath = configParser.get("backup-tools", "destpath")

    cmd = os.path.join(path, "backup.sh")

    if share == "homes": savedir = "/home/" # FIXME
    else: savedir = os.path.join(smbObj.sharespath, share)

    # FIXME: check for error
    lmctools.shlaunchBackground(cmd+" "+share+" "+savedir+" "+destpath+" "+login+" "+media+" "+path,"backup share "+share,lmctools.progressBackup)
    return 0

def restartSamba():
    lmctools.shlaunchBackground(SambaConfig("samba").samba_init_script+' restart')
    return 0;

def addSmbAttr(uid, password):
    return sambaLdapControl().addSmbAttr(uid, password)

def isSmbUser(uid):
    return sambaLdapControl().isSmbUser(uid)

def changeUserPasswd(uid, password):
    return sambaLdapControl().changeUserPasswd(uid, password)

def changeSambaAttributes(uid, attributes):
    return sambaLdapControl().changeSambaAttributes(uid, attributes)

def changeUserPrimaryGroup(uid, groupName):
    return sambaLdapControl().changeUserPrimaryGroup(uid, groupName)

def delSmbAttr(uid):
    return sambaLdapControl().delSmbAttr(uid)

def isEnabledUser(uid):
    return sambaLdapControl().isEnabledUser(uid)

def isLockedUser(uid):
    return sambaLdapControl().isLockedUser(uid)

def enableUser(uid):
    return sambaLdapControl().enableUser(uid)

def disableUser(uid):
    return sambaLdapControl().disableUser(uid)

def lockUser(uid):
    return sambaLdapControl().lockUser(uid)

def unlockUser(uid):
    return sambaLdapControl().unlockUser(uid)

def makeSambaGroup(group):
    return sambaLdapControl().makeSambaGroup(group)

def getSmbStatus():
    return smbConf().getSmbStatus()

def getConnected():
    return smbConf().getConnected()

# create a machine account
def addMachine(name, comment, addMachineScript = False):
    return sambaLdapControl().addMachine(name, comment, addMachineScript)


class SambaConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        try: self.samba_conf_file = self.get("main", "sambaConfFile")
        except: pass
        try: self.samba_init_script = self.get("main", "sambaInitScript")
        except: pass
        try: self.clam_av_so = self.get("main", "sambaClamavSo")
        except: pass

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.samba_conf_file = '/etc/samba/smb.conf'
        self.samba_init_script = '/etc/init.d/samba'
        self.clam_av_so = "/usr/lib/samba/vfs/vscan-clamav.so"

class sambaLdapControl(lmc.plugins.base.ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        lmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)

        if conffile: configFile = conffile
        else: configFile = INI
        cp = ConfigParser()
        cp.read(configFile)

        self.userDefault["samba"] = {}
        USERDEFAULT = "userDefault"
        if cp.has_section(USERDEFAULT):
            for option in cp.options(USERDEFAULT):
                self.userDefault["samba"][option] = cp.get(USERDEFAULT, option)

        # Fill dictionnary of hooks from config
        if cp.has_section("hooks"):
            for option in cp.options("hooks"):
                self.hooks["samba." + option] = cp.get("hooks", option)

    def getDomainAdminsGroup(self):
        """
        Return the LDAP posixGroup entry corresponding to the 'Domain Admins' group.

        @return: a posixGroup entry
        @rtype: dict
        """
        domain = self.getDomain()
        sambaSID = domain["sambaSID"][0]
        result = self.search("(&(objectClass=sambaGroupMapping)(sambaSID=%s-512))" % sambaSID)
        if len(result): ret = result[0][0][1]
        else: ret = {}
        return ret

    def getDomainUsersGroup(self):
        """
        Return the LDAP posixGroup entry corresponding to the 'Domain Users' group.

        @return: a posixGroup entry
        @rtype: dict
        """
        domain = self.getDomain()
        sambaSID = domain["sambaSID"][0]
        result = self.search("(&(objectClass=sambaGroupMapping)(sambaSID=%s-513))" % sambaSID)
        if len(result): ret = result[0][0][1]
        else: ret = {}
        return ret

    def getDomainGuestsGroup(self):
        """
        Return the LDAP posixGroup entry corresponding to the 'Domain Guests' group.

        @return: a posixGroup entry
        @rtype: dict
        """
        domain = self.getDomain()
        sambaSID = domain["sambaSID"][0]
        result = self.search("(&(objectClass=sambaGroupMapping)(sambaSID=%s-514))" % sambaSID)
        if len(result): ret = result[0][0][1]
        else: ret = {}
        return ret

    def getDomainComputersGroup(self):
        """
        Return the LDAP posixGroup entry corresponding to the 'Domain Computers' group.

        @return: a posixGroup entry
        @rtype: dict
        """
        domain = self.getDomain()
        sambaSID = domain["sambaSID"][0]
        result = self.search("(&(objectClass=sambaGroupMapping)(sambaSID=%s-515))" % sambaSID)
        if len(result): ret = result[0][0][1]
        else: ret = {}
        return ret

    def getDomain(self):
        """
        Return the LDAP sambaDomainName entry corresponding to the domain specified in smb.conf

        @return: the sambaDomainName entry
        @rtype: dict
        """
        conf = smbConf()
        domain = conf.getContent("global", "workgroup")
        result = self.search("(&(objectClass=sambaDomain)(sambaDomainName=%s))" % domain)
        if len(result): ret = result[0][0][1]
        else: ret = {}
        return ret

    def addMachine(self, uid, comment, addMachineScript = False):
        """
        Add a PosixAccount for a machine account.
        if addMachineScript is False, we run smbpasswd to create the needed LDAP attributes.

        @param uid: name of new machine (no space)
        @type uid: str

        @param comment: comment of machine (full string accept)
        @type comment: str
        """
        origuid = uid
        uid = uid + '$'
        uidNumber = self.maxUID()+1;

        if not comment:
            comment = "Machine account"

        comment_UTF8 = str(lmc.plugins.base.delete_diacritics((comment.encode("UTF-8"))))
        gidNumber = self.getDomainComputersGroup()["gidNumber"][0]
        # creating machine skel
        user_info = {
            'objectclass':('account', 'posixAccount', 'top'),
            'uid':uid,
            'cn':uid,
            'uidNumber':str(uidNumber),
            'gidNumber': str(gidNumber),
            'gecos':str(comment_UTF8),
            'homeDirectory':'/dev/null',
            'loginShell':'/bin/false'
            }
        
        ident = 'uid=' + uid + ',' + self.baseComputersDN
        attributes=[ (k,v) for k,v in user_info.items() ]
        self.l.add_s(ident,attributes)

        if not addMachineScript:
            cmd = 'smbpasswd -a -m ' + uid
            shProcess = generateBackgroundProcess(cmd)
            ret = shProcess.getExitCode()

            if ret:
                self.delMachine(origuid) # Delete machine account we just created
                raise Exception("Failed to add computer entry\n" + shProcess.stdall)

        return 0
        
    def delMachine(self, uid):
        """
        Remove a computer account from LDAP

        @param uidUser: computer name
        @type  uidUser: str
        """
        uid = uid + "$"
        self.l.delete_s('uid=' + uid + ',' + self.baseComputersDN)
        return 0

    def addSmbAttr(self, uid, password):
        cmd = 'smbpasswd -s -a '+uid
        shProcess = generateBackgroundProcess(cmd)
        shProcess.write(password+"\n")
        shProcess.write(password+"\n")
        ret = shProcess.getExitCode()

        if ret != 0:
            raise Exception("Failed to modify password entry\n"+shProcess.stdall)

        if not ret:
            # Command was successful, now set default attributes
            # Get current user entry
            dn = 'uid=' + uid + ',' + self.baseUsersDN
            s = self.l.search_s(dn, ldap.SCOPE_BASE)
            c, old = s[0]
            new = old.copy()
            # Modify attributes
            for attribute, value in self.userDefault["samba"].items():
                if value == "DELETE":
                    for key in new.keys():
                        if key.lower() == attribute:
                            del new[key]
                            break
                else:
                    for key in new.keys():
                        if key.lower() == attribute:
                            new[key] = value
                            break
            # Update LDAP
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        self.runHook("samba.addsmbattr", uid, password)
        return 0

    def isSmbUser(self, uid):
        ret = False
        if self.existUser(uid): ret = "sambaSamAccount" in self.getDetailedUser(uid)["objectClass"]
        return ret

    def changeSambaAttributes(self, uid, attributes):
        """
        Change the SAMBA attributes for an user.
        If an attribute is an empty string, it is deleted.

        @param uid: login of the user
        @type uid: str
        @param attributes: dictionnary of the SAMBA attributes
        @type attributes: dict
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]

        # We update the old attributes array with the new SAMBA attributes
        new = old.copy()
        for key in attributes.keys():
            if key.startswith("samba"):
                value = attributes[key]
                if value == "":
                    # Maybe delete this SAMBA LDAP attribute
                    try:
                        del new[key]
                    except KeyError:
                        pass
                else:
                    if value.startswith("\\\\\\\\"):
                        value = value.replace("\\\\", "\\")
                    # Update this SAMBA LDAP attribute
                    new[key] = value
        modlist = ldap.modlist.modifyModlist(old, new)
        if modlist: self.l.modify_s(dn, modlist)
        self.runHook("samba.changesambaattributes", uid)
        return 0

    def changeUserPrimaryGroup(self, uid, group):
        """
        Change the SAMBA primary group of a user, if the sambaPrimaryGroupSID
        of this user is defined. Else do nothing.

        @param uid: login of the user
        @type uid: unicode

        @param group: new primary group
        @type uid: unicode
        """
        try:
            spg = self.getDetailedUser(uid)["sambaPrimaryGroupSID"]
        except KeyError:
            # This user has no sambaPrimaryGroupSID set
            # So nothing to do
            return
        gidNumber = self.getDetailedGroup(group)["gidNumber"][0]
        sid = self.gid2sid(gidNumber)
        if sid:
            self.changeUserAttributes(uid, "sambaPrimaryGroupSID", sid)

    def gid2sid(self, gidNumber):
        """
        Return the SID corresponding to a gid number.

        @param gidNumber: gid number of a group
        @type gidNumber: int

        @return: SID number, or None if no corresponding SID found
        @rtype: str
        """        
        group = self.getDetailedGroupById(gidNumber)
        try:
            sid = group["sambaSID"][0]
        except KeyError:
            sid = None
        return sid

    def delSmbAttr(self, uid):
        """remove smb attributes via smbpasswd cmd"""
        return lmctools.shlaunch("/usr/bin/smbpasswd -x " + uid)

    def changeUserPasswd(self, uid, passwd):
        """
        change SAMBA user password

        @param uid: user name
        @type  uid: str

        @param passwd: non encrypted password
        @type  passwd: str
        """
        cmd = 'smbpasswd -s -a '+uid
        shProcess = generateBackgroundProcess(cmd)
        shProcess.write(passwd+"\n")
        shProcess.write(passwd+"\n")
        ret = shProcess.getExitCode()

        if ret != 0:
            raise Exception("Failed to modify password entry\n" + shProcess.stdall)

        self.runHook("samba.changeuserpasswd", uid, passwd)
        return 0

    def isEnabledUser(self, uid):
        """
        Return True if the SAMBA user is enabled
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        flags = flags.strip("[]")
        flags = flags.strip()
        return not flags.startswith("D")

    def isLockedUser(self, uid):
        """
        Return True if the SAMBA user is locked
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        flags = flags.strip("[]")
        flags = flags.strip()
        return "L" in flags

    def enableUser(self, uid):
        """
        Enable the SAMBA user
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        flags = flags.strip("[]")
        flags = flags.strip()
        if not flags.startswith("D"):
            # Huh ? User has been already enabled
            # Do nothing
            pass
        else:
            flags = flags[1:]
            flags = "[" + flags.ljust(11) + "]"
            new["sambaAcctFlags"] = [flags]
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        return 0

    def disableUser(self, uid):
        """
        Disable the SAMBA user
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        # flags should be something like "[U          ]"
        flags = flags.strip("[]")
        flags = flags.strip()
        if flags.startswith("D"):
            # Huh ? User has been already disabled
            # Do nothing
            pass
        else:
            flags = "D" + flags
            flags = "[" + flags.ljust(11) + "]"
            new["sambaAcctFlags"] = [flags]
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        return 0

    def unlockUser(self, uid):
        """
        Unlock the SAMBA user
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        # flags should be something like "[U          ]"
        if "L" in flags:
            flags = flags.strip("[]")
            flags = flags.strip()
            flags = flags.replace("L", "")
            flags = "[" + flags.ljust(11) + "]"
            new["sambaAcctFlags"] = [flags]
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        return 0

    def lockUser(self, uid):
        """
        Lock the SAMBA user
        """
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = old.copy()
        flags = new["sambaAcctFlags"][0]
        # flags should be something like "[U          ]"
        if not "L" in flags:
            flags = flags.strip("[]")
            flags = flags.strip()
            flags = flags + "L"
            flags = "[" + flags.ljust(11) + "]"
            new["sambaAcctFlags"] = [flags]
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        return 0

    def makeSambaGroup(self, group):
        """
        Transform a POSIX group as a SAMBA group.
        It adds in the LDAP the necessary attributes to the group.

        @param group: the group name
        @type group: str
        """
        lmctools.shLaunch("net groupmap add unixgroup='%s'" % group)

    def isSambaGroup(self, group):
        ret = False
        if self.existGroup(group): ret = "sambaGroupMapping" in self.getDetailedGroup(group)["objectClass"]
        return ret


##########################################################################
# Class de gestion de smbConf
##########################################################################

class smbConf:

    def __init__(self, smbconffile = "/etc/samba/smb.conf", conffile = None, conffilebase = None):
        """
        Constructor for object that read/write samba conf file.

        We use the testparm command on the smb configuration file to sanitize it,
        and to replace all keyword synonyms with the preferred keywords:
         - 'write ok', 'writeable', 'writable' -> 'read only'
         - 'public' -> 'guest ok'
         ...

        In SAMBA source code, parameters are defined in param/loadparm.c
        """
        if not conffile: configParser = lmctools.getConfigParser("samba")
        else:
            configParser = ConfigParser()
            configParser.read(conffile)
        self.sharespath = configParser.get("main", "sharespath")

        self.conffilebase = conffilebase
        self.smbConfFile = smbconffile
        smbConfVerbose = self.getVerboseTestparmOutput()
        smbConf = self.getTestparmOutput()

        self.contentArrVerbose = self._parseSmbConfFile(smbConfVerbose)
        self.contentArr = self._parseSmbConfFile(smbConf)

    def _parseSmbConfFile(self, confString):
        """
        Parse SAMBA configuration file content
        """
        contentArr = {}
        for a in confString.split("["):
            b = a.split("]")

            for i in range(len(b)/2):
                listArg = b.pop()
                localArgArr = {}

                sectionName = b.pop()
                contentArr[sectionName] = {}
                for c in listArg.split("\n"):

                    if '=' in c:
                        arg = c.split("=", 1)
                        localArgArr[arg.pop().strip()] = arg.pop().strip()

                contentArr[sectionName] = localArgArr

        return contentArr

    def outputSmbConfFile(self):
        """
        Output as a string smb.conf file content
        """
        if self.getContent("global","unix charset") == "UTF-8":
            encode_method = "utf8"
        else:
            encode_method = "iso-8859-1"

        out = ""
        # Begin by the [global] section
        k = "global"
        out = out + '[' + k + ']\n'
        for (k2,v2) in self.contentArr[k].items():
            encodeS='\t'+k2+' = '+v2+'\n'
            if isinstance(encodeS,str) :
                encodeS = unicode(encodeS,'utf8',"replace")
            encodeS = encodeS.encode(encode_method,'replace')
            out = out + encodeS
        out = out + "\n"

        # Do the rest
        del self.contentArr[k]
        for (k,v) in self.contentArr.items():
            out = out + '[' + k + ']\n'
            for (k2,v2) in v.items():
                encodeS='\t'+k2+' = '+v2+'\n'
                if isinstance(encodeS,str) :
                    encodeS = unicode(encodeS,"utf8","replace")
                encodeS = encodeS.encode(encode_method,'replace')
                out = out + encodeS
            out = out + "\n"
        return out

    def validate(self, conffile = "/etc/samba/smb.conf"):
        """
        Validate SAMBA configuration file with testparm.

        @return: Return True if smb.conf has been validated, else return False
        """
        cmd = lmctools.shLaunch("/usr/bin/testparm -s %s" % conffile)
        if cmd.exitCode:
            ret = False
        elif "Unknown" in cmd.err or "ERROR:" in cmd.err or "Ignoring badly formed line" in cmd.err:
            ret = False
        else: ret = True
        return ret

    def getVerboseTestparmOutput(self, conffile = "/etc/samba/smb.conf"):
        """
        Get verbose SAMBA configuration file with testparm.

        @return: Return the smb.conf file formatted by testparm in verbose mode
        """
        cmd = lmctools.shLaunch("/usr/bin/testparm -v -s %s" % conffile)
        return cmd.out

    def getTestparmOutput(self, conffile = "/etc/samba/smb.conf"):
        """
        Get SAMBA configuration file with testparm.

        @return: Return the smb.conf file formatted by testparm
        """
        cmd = lmctools.shLaunch("/usr/bin/testparm -s %s" % conffile)
        return cmd.out

    def isValueTrue(self, string):
        """
        @param string: a string
        @type string: str
        @return: Return 1 if string is yes/true/1 (case insensitive), return 0 if string is no/false/0 (case insensitive), else return -1
        $rtype: int
        """
        string = str(string).lower()
        if string in ["yes", "true", "1"]: return 1
        elif string in ["no", "false", "0"]: return 0
        else: return -1

    def isValueAuto(self, string):
        """
        @param string: a string
        @type string: str
        @return: Return True if string is 'auto' (case insensitive), else return False
        $rtype: int
        """
        string = string.lower()
        return string == "auto"

    def getBooleanValue(self, section, option):
        """
        Return the boolean value of an option in a section.

        """
        pass

    def getSmbInfo(self):
        """
        return main information about global section
        """
        resArray = {}
        resArray['logons'] = self.isValueTrue(self.getContent('global','domain logons'))
        resArray['master'] = self.isValueTrue(self.getContent('global','domain master'))
        if resArray['master'] == -1:
            resArray["master"] = self.isValueAuto(self.getContent('global','domain master'))
        resArray['homes'] = self.contentArr.has_key('homes')
        resArray['pdc'] = (resArray['logons']) and (resArray['master'])
        for option in ["workgroup", "netbios name", "logon path", "logon drive", "logon home", "logon script"]:
            resArray[option] = self.getContent("global", option)
        return resArray

    def isPdc(self):
        ret = self.getSmbInfo()
        return ret["pdc"]

    def getContent(self, section, content):
        """get information from self.contentArr[section][content]"""
        # FIXME: shouldn't return -1 but keep the exception raised
        try:
            return self.contentArrVerbose[section][content]
        except KeyError:
            return -1

    def setContent(self, section, content, value):
        """set a content in self.contentArr[section][content]=value"""
        try:
            self.contentArr[section][content]=value;
        except KeyError:
            self.contentArr[section] = {}
            self.setContent(section,content,value)

    def remove(self, section, option):
        """
        Remove an option from a section.
        """
        try:
            del self.contentArr[section][option]
        except KeyError:
            pass

    def smbInfoSave(self, pdc, homes, options):
        """
        Set information in global section:
         @param pdc: Is it a PDC ?
         @param homes: Do we share users' home ?
         @param options: dict with global options
        """
        current = self.getSmbInfo()

        # For this two smb.conf global option, we put a space and not an empty
        # value in smb.conf, else a value by default is set by Samba
        for option in ["logon path", "logon home"]:
            if not options[option]: options[option] = " "

        # We update only what has changed from the current configuration
        for option in ["workgroup", "netbios name", "logon path", "logon drive", "logon home", "logon script"]:
            if options[option]:
                if options[option] != current[option]:
                    self.setContent("global", option, options[option])
                # else do nothing, the option is already set
            else:
                self.remove("global", option)

        if current["pdc"] != pdc:
            if pdc: self.setContent('global','domain logons','yes')
            else: self.setContent('global','domain logons','no')
            # Default value of domain master (auto) is sufficient
            self.remove("global", "domain master")

        if current["homes"] != homes:
            if homes:
                self.setContent('homes','comment','Repertoires utilisateurs')
                self.setContent('homes','browseable','no')
                self.setContent('homes','read only','no')
                self.setContent('homes','create mask','0700')
                self.setContent('homes','directory mask','0700')
                # Set the vscan-clamav plugin if available
                if os.path.exists(SambaConfig("samba").clam_av_so):
                    self.setContent("homes", "vfs objects", "vscan-clamav")
            else:
                try:
                    self.delShare('homes',0)
                except lmcException:
                    pass
        # Save file
        self.save()
        return 0

    def getDetailedShares(self):
        """return detailed list of shares"""
        resList = []
        #foreach element in smb.conf
        # so for each element in self.contentArr
        for section in self.getSectionList():
            if not section in ["global", "printers", "print$"]:
                localArr = []
                localArr.append(section)
                comment = self.getContent(section, 'comment' )
                if (comment != -1):
                    localArr.append(comment)
                resList.append(localArr)

        resList.sort()
        return resList

    def getSectionList(self):
        returnArr = list()
        for (k,v) in self.contentArr.items():
            returnArr.append(k)
        return returnArr

    def save(self):
        """
        Write SAMBA configuration file (smb.conf) to disk
        """
        handle, tmpfname = tempfile.mkstemp("lmc")
        f = os.fdopen(handle, "w")
        f.write(self.outputSmbConfFile())
        f.close()
        if not self.validate(tmpfname): raise LmcException("smb.conf file is not valid")
        lmctools.shlaunch("cp %s %s" % (tmpfname, self.smbConfFile))
        lmctools.shlaunch("rm %s" % tmpfname)

    def delShare(self, name, remove):
        """
        Delete a share from SAMBA configuration, and maybe delete the share
        directory from disk.
        The save method must be called to update smb.conf.

        @param name: Name of the share
        @param remove: If true, we physically remove the directory
        """
        try:
            path = self.getContent(name, 'path')
            del self.contentArr[name]
        except KeyError:
            raise lmcException('share "'+ name+'" does not exist')

        if remove: lmctools.shlaunch('rm -fr '+ path)

    def shareInfo(self, name):
        """
        Get information about a share
        """
        returnArr = {}
        returnArr['desc'] = self.getContent(name,'comment')
        if returnArr['desc'] == -1: returnArr['desc'] = ""
        if self.isValueTrue(self.getContent(name,'public')) == 1:
            returnArr['permAll'] = 1
        elif self.isValueTrue(self.getContent(name,'guest ok')) == 1:
            returnArr['permAll'] = 1
        else: returnArr['permAll'] = 0

        # If we cannot find it
        if (self.getContent(name, 'vfs objects') == -1):
            returnArr['antivirus'] = 0
        else:
            returnArr['antivirus'] = 1

        if self.getContent(name, 'browseable') == -1:
            returnArr["browseable"] = 1
        elif self.isValueTrue(self.getContent(name, 'browseable')):
            returnArr["browseable"] = 1
        else:
            returnArr["browseable"] = 0
            
        # Get the directory group owner
        # FIXME: ???
        try:
            path = os.path.join(self.sharespath, name)
            ps = os.popen('stat %s | grep Access: | head -n 1' % path, 'r')
            # more matching regex
            # 'Gid: *\( *[0-9]*/ *([^/]*)\)$'
            groupArr= re.findall('/ *([^/]*)\)$', ps.read())
            for group in groupArr:
                returnArr['group']=group
        except:
            #raise lmcException('cannot retrieve group attribute')
            pass
        return returnArr


    def addShare(self, name, comment, usergroups, permAll, admingroups, browseable = True, av = False):
        """
        add a share in smb.conf
        and create it physicaly
        """
        if self.contentArr.has_key(name):
            raise Exception('This share already exist')

        # create samba share directory
        path = os.path.join(self.sharespath, name)

        # FIXME: we should test os.system return value, and in fact not use os.system !
        os.system("mkdir -p '%s'" % path)
        os.system("chown 'root:root' %s" % (path))

        # create table and fix permission
        tmpInsert = {}
        tmpInsert['comment'] = comment
        if permAll:
            lmctools.shlaunch("setfacl -b "+path)
            tmpInsert['public'] = 'yes'
            os.system("chmod 0777 '%s'" % path)
        else:
            tmpInsert['public'] = 'no'
            os.system("chmod 0770 '%s'" % path)
            lmctools.shlaunch("setfacl -b "+path)
            acl1 = ACL(file=path)
            # Add and set default mask to rwx
            # This is needed by the ACL system, else the ACLs won't be valid
            e = acl1.append()
            e.permset.add(ACL_READ)
            e.permset.add(ACL_WRITE)
            e.permset.add(ACL_EXECUTE)
            e.tag_type = ACL_MASK

            # For each specified group, we add rwx access
            for group in usergroups:
                e = acl1.append()
                e.permset.add(ACL_READ)
                e.permset.add(ACL_WRITE)
                e.permset.add(ACL_EXECUTE)
                e.tag_type = ACL_GROUP
                # Search the gid number corresponding to the given group
                ldapobj = lmc.plugins.base.ldapUserGroupControl(self.conffilebase)
                gidNumber = ldapobj.getDetailedGroup(group)['gidNumber'][0]
                e.qualifier = int(gidNumber)
            # Test if our ACLs are valid
            if acl1.valid():
                acl1.applyto(path)
            else:
                logger = logging.getLogger()
                logger.error("cannot save acl on folder " + path)

        tmpInsert['writeable'] = 'yes'
        if not browseable: tmpInsert['browseable'] = 'No'
        tmpInsert['path'] = path

        # Set the vscan-clamav plugin if available
        if av: tmpInsert['vfs objects'] = 'vscan-clamav'

        # Set the admin groups for the share
        if admingroups:
            tmpInsert["admin users"] = ""
            for group in admingroups:
                tmpInsert["admin users"] = tmpInsert["admin users"] + '"+' + group + '", '

        self.contentArr[name] = tmpInsert

        return 'partage ' + name +' ajoute' # FIXME: Should return 0

    def getACLOnShare(self, name):
        """
        Return a list with all the groups that have rwx access to the share.

        @param name: name of the share (last component of the path)
        @type name: str

        @rtype: list
        @return: list of groups that have rwx access to the share.
        """
        path = os.path.join(self.sharespath, name)
        ret= []
        ldapobj = lmc.plugins.base.ldapUserGroupControl(self.conffilebase)
        acl1 = ACL(file=path)
        for e in acl1:
            if e.permset.write:
                if e.tag_type == ACL_GROUP:
                    res = ldapobj.getDetailedGroupById(str(e.qualifier))
                    ret.append(res['cn'][0])
        return ret

    def getAdminUsersOnShare(self, name):
        """
        Return a list of all the groups in the admin users option of the given share.

        @param name: name of the share
        @type name: str

        @rtype: list
        @return: list of administrator groups of the share
        """
        adminusers = self.getContent(name, "admin users")
        ret = []
        if adminusers != -1:
            for item in adminusers.split(","):
                item = item.strip().strip('"')
                if item.startswith("+"):
                    item = item[1:]
                    # Remove the SAMBA domain part
                    if "\\" in item:
                        item = item.split("\\")[1]
                    ret.append(item)
        return ret

    def isBrowseable(self, name):
        """
        Return true if the share is browseable
        
        @param name: name of the share (last component of the path)
        @type name: str

        @rtype: bool
        @return: False if browseable = No
        """
        state = self.getContent(name, "browseable")
        if state == -1: ret = True
        else: ret = bool(self.isValueTrue(state))
        return ret

    def getSmbStatus(self):
        """
        Return SAMBA shares connection status
        """
        output = lmctools.shlaunch('/usr/bin/net status shares parseable')
        section = "none"
        service = dict()
        user = dict()

        for line in output:
            tab = line.split('\\',7)
            serviceitem = dict()
            serviceitem['pid'] = tab[0]

            # Create unix timestamp
            serviceitem['lastConnect'] = mktime(strptime(tab[6]))

            serviceitem['machine'] = tab[4]

            if tab[2]:
                serviceitem['useruid'] = tab[2]
                serviceitem['ip'] = tab[5]
            else:
                serviceitem['useruid'] = 'anonymous'

            if tab[0]==tab[2]:
                indIndex = "homes"
            else:
                indIndex = tab[0]

            if not indIndex in service:
                service[indIndex] = list()

            service[indIndex].append(serviceitem)

        return service

    def getConnected(self):
        """
        Return all opened SAMBA sessions
        """
        output = lmctools.shlaunch('/usr/bin/net status sessions parseable')
        result = []
        for line in output:
            #7727\useruid\Domain Users\machine\192.168.0.17
            # 0    1    2             3          4
            tab = line.split('\\',5)
            sessionsitem = {}
            sessionsitem['pid'] = tab[0]
            sessionsitem['useruid'] = tab[1]
            sessionsitem['machine'] = tab[3]
            sessionsitem['ip'] = tab[4]
            result.append(sessionsitem)
        return result



class sambaLog:

    def __init__(self, logs = ["/var/log/samba/log.nmbd", "/var/log/samba/log.smbd"]):
        self.logs = logs
        self.rex = {
            "PDC" : "Samba server (\S+) is now a domain master browser for workgroup (\S+) on subnet (\S+)",
            "LOGON" : "Samba is now a logon server for workgroup (\S+) on subnet (\S+)",
            "STOP" : "going down...",
            "START" : "Netbios nameserver version (\S+) started.",
            "AUTHSUCCESS" : "authentication for user \[(\S+)\] -> \[(\S+)\] -> \[(\S+)\] succeeded",
            "AUTHFAILED" :  "Authentication for user \[(\S+)\] -> \[(\S+)\] FAILED with error (\S+)"
            }

    def get(self):
        return self.filterLog(self.parse())

    def filterLog(self, logs):
        filteredLogs = []
        for log in logs:
            for key in self.rex:
                m = re.search(self.rex[key], log["msg"])
                if m:
                    l = {}
                    l["day"] = log["day"]
                    l["hour"] = log["hour"]
                    l["msg"] = key
                    filteredLogs.append(l.copy())
        return filteredLogs

    def parse(self):
        logs = {}
        for logFile in self.logs:
            l = {}
            firstdate = 0
            f = file(logFile)
            for line in f:
                if line.startswith("["):
                    firstdate = 1
                    if l: logs.append(l.copy())
                    l = {}
                    l["msg"] = ""
                    m = re.match("\[(.*)\].*", line)
                    day, hour, num = m.group(1).split()
                    hour = hour[:-1]
                    l["day"] = day
                    l["hour"] = hour
                else:
                    if firstdate:
                        line = line.strip()
                        line = line.strip("*")
                        if len(line): l["msg"] = l["msg"] + line
            f.close()
        return logs

