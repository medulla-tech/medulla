# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
MMC agent SSH public key plugin.

This plugin allows to add SSH public keys to LDAP user entries.
These keys can then be retrieved by OpenSSH with the LDAP Public Key patch. See
http://code.google.com/p/openssh-lpk/
"""

import copy
import ldap
import logging

from ldap import modlist
from mmc.plugins.base import ldapUserGroupControl
from mmc.support.config import PluginConfig

VERSION = "2.3.2"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

class UserSshKeyConfig(PluginConfig):
    pass

def activate():
    ldapObj = ldapUserGroupControl()
    logger = logging.getLogger()

    config = UserSshKeyConfig("sshlpk")
    if config.disabled:
        logger.warning("Plugin sshlpk: disabled by configuration.")
        return False
    
    sshkeySchema = ['posixAccount', 'ldapPublicKey']

    for objectClass in sshkeySchema:
        schema = ldapObj.getSchema(objectClass)
        if not len(schema):
            logger.error("OpenSSH LDAP public key schema is not available: %s objectClass is not included in LDAP directory" % objectClass);
            return False

    return True


class UserSshKey(ldapUserGroupControl):

    """
    Class to manage the LDAP public keys attributes of a user
    """
    
    def __init__(self, uid, conffile = None):
        """
        Class constructor.
        
        @param uid: User id
        @type uid: str
        """
        ldapUserGroupControl.__init__(self, conffile)
        self.configSshKey = UserSshKeyConfig("sshlpk", conffile)
        self.userUid = uid
        self.dn = 'uid=' + uid + ',' + self.baseUsersDN
    
    def getSshKey(self, number = None):
        """
        Returns all the public SSH keys of a user, or just one if number is
        set.

        @param number: if sets, return the key at this index
        @type number: int

        @returns: the list of all SSH public keys, or only one if number is set
        @rtype: list or str
        """
        try:
            result = self.getDetailedUser(self.userUid)["sshPublicKey"]
            logging.getLogger().debug(str(result))
            if number == None:
                return result
            elif number < len(result) and number > -1:
                return result[number]
            else:
                return None
        except KeyError:
            return []
        
    def addSshKey(self, value):
        """
        Store a new public SSH key to the current user.

        @param value: public SSH key
        @type value: str
        """
        if value != None:
            try:
                self.l.modify_s(self.dn, [(ldap.MOD_ADD, "sshPublicKey", value)])
            except ldap.UNDEFINED_TYPE:
                logging.getLogger().error("Attribute sshPublicKey isn't defined on LDAP")
            except ldap.INVALID_SYNTAX:
                logging.getLogger().error("Invalid syntax for the attribute value of sshPublicKey on LDAP")
            
    
    def delSshKey(self, value):
        """
        Delete a public SSH key from the current user.

        @param value: public SSH key
        @type value: str        
        """
        if value != None:
            try:
                self.l.modify_s(self.dn, [(ldap.MOD_DELETE, "sshPublicKey", value)])
            except ldap.UNDEFINED_TYPE:
                logging.getLogger().error("Attribute sshPublicKey isn't defined on LDAP")
            except ldap.INVALID_SYNTAX:
                logging.getLogger().error("Invalid syntax from the attribute value of sshPublicKey on LDAP")
    
    def updateSshKeys(self, sshKeysList):
        """
        Add a list of public SSH keys to the current user.

        @param sshKeysList: 
        @type: list of public SSH keys
        """
        if not self.hasSshKeyObjectClass():
           self.addSshKeyObjectClass()
        # Get current user entry
        s = self.l.search_s(self.dn, ldap.SCOPE_BASE)
        c, old = s[0]
        
        new = copy.deepcopy(old)

        new['sshPublicKey'] = sshKeysList
        
        # Update LDAP
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(self.dn, modlist)
            
    def hasSshKeyObjectClass(self):
        """
        Return true if the user owns the ldapPublicKey objectClass.

        @return: return True if the user owns the ldapPublicKey objectClass.
        @rtype: boolean
        """
        return "ldapPublicKey" in self.getDetailedUser(self.userUid)["objectClass"]
        
    def addSshKeyObjectClass(self):
        """
        Add the ldapPublicKey object class to the current user.
        """
        # Get current user entry
        s = self.l.search_s(self.dn, ldap.SCOPE_BASE)
        c, old = s[0]
        
        new = copy.deepcopy(old)

        if not "ldapPublicKey" in new["objectClass"]:
            new["objectClass"].append("ldapPublicKey")
        if not "posixAccount" in new["objectClass"]:
            new["objectClass"].append("posixAccount")

        # Update LDAP
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(self.dn, modlist)

    def delSSHKeyObjectClass(self):
        """
        Remove the ldapPublicKey object class from the current user.
        """
        self.removeUserObjectClass(self.userUid, 'ldapPublicKey')


# XML-RPC function
def hasSshKeyObjectClass(uid):
    return UserSshKey(uid).hasSshKeyObjectClass()
    
def addSshKeyObjectClass(uid):
    UserSshKey(uid).addSshKeyObjectClass()

def getSshKey (uid, number):
    return UserSshKey(uid).getSshKey(number)
    
def getAllSshKey (uid):
    return UserSshKey(uid).getSshKey(None)
    
def addSshKey (uid, value):
    UserSshKey(uid).addSshKey(value)
    
def updateSshKeys (uid, keylist):
    UserSshKey(uid).updateSshKeys(keylist)
    
def delSshKey (uid, value):
    UserSshKey(uid).delSshKey(value)

def delSSHKeyObjectClass(uid):
    UserSshKey(uid).delSSHKeyObjectClass()


if __name__ == "__main__":
    if not hasSshKeyObjectClass("user1"):
        addSshKeyObjectClass("user1")
    print getAllSshKey("user1")
    
