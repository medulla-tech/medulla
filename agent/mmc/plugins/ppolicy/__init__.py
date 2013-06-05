# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
MMC agent password policy plugin

This plugin allows to manage LDAP password policy related attributes.
See: http://tools.ietf.org/html/draft-behera-ldap-password-policy

The device object class will be used as the structural class holding the
pwdPolicy auxiliary object class (as done in OpenLDAP ppolicy smoke test).
"""

import copy
import ldap
import logging
import time
import calendar
from ldap import modlist
from mmc.plugins.base import ldapUserGroupControl
from mmc.support.config import PluginConfig
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory as AF
from mmc.plugins.ppolicy.audit import AT, AA, PLUGIN_NAME


VERSION = "3.1.0"
APIVERSION = "0:1:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION


def activate():
    ldapObj = ldapUserGroupControl()
    logger = logging.getLogger()

    config = PPolicyConfig("ppolicy")
    if config.disabled:
        logger.warning("Plugin ppolicy: disabled by configuration.")
        return False

    ppolicySchema = ['pwdPolicy', 'device']

    for objectClass in ppolicySchema:
        schema = ldapObj.getSchema(objectClass)
        if not len(schema):
            logger.error("LDAP Password Policy schema is not included in LDAP directory: %s objectClass is not available" % objectClass);
            return False

    # Register default password policy into the LDAP if it does not exist
    PPolicy().addPPolicy()

    return True


class PPolicyConfig(PluginConfig):

    """
    Class for objects that read the ppolicy plugin configuration file.
    """

    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        """
        PluginConfig.readConf(self)
        # Read LDAP Password Policy configuration
        self.ppolicyAttributes = {}
        self.ppolicydn = self.get('ppolicy', 'ppolicyDN')
        self.ppolicydefault = self.get('ppolicy', 'ppolicyDefault')
        self.ppolicydefaultdn = "cn=" + self.ppolicydefault + "," + self.ppolicydn
        for attribute in self.items('ppolicyattributes'):
            if attribute[1] == 'True':
                self.ppolicyAttributes[attribute[0]] = True
            elif attribute[1] == 'False':
                self.ppolicyAttributes[attribute[0]] = False
            else:
                self.ppolicyAttributes[attribute[0]] = attribute[1]

class PPolicy(ldapUserGroupControl):

    """
    Class for objects that manages the default LDAP password policy.
    """

    def __init__(self, conffile = None):
        ldapUserGroupControl.__init__(self, conffile)
        self.configPPolicy = PPolicyConfig("ppolicy", conffile)

    def checkPPolicy(self, ppolicyName = None):
        '''
        Check the presence of a Password Policy

        @returns: True if it exists
        @rtype: bool
        '''
        if not ppolicyName:
            ppolicyDN = self.configPPolicy.ppolicydefaultdn
        else:
            ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn
        ret = False
        try:
            self.l.search_s(ppolicyDN, ldap.SCOPE_BASE)
            ret = True
        except ldap.NO_SUCH_OBJECT:
            pass
        return ret

    def addPPolicy(self, ppolicyName = None, ppolicyDesc = None):
        """
        Add a password policy in LDAP if not available.
        """
        if not self.checkPPolicy(ppolicyName):

            if not ppolicyName:
                ppolicyName = self.configPPolicy.ppolicydefault
                ppolicyDesc = "Default password policy"
                ppolicyDN = self.configPPolicy.ppolicydefaultdn
                head, path = self.configPPolicy.ppolicydn.split(",", 1)
                ouName = head.split("=")[1]
                self.addOu(ouName, path)
            else:
                ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn

            # set common attributes for all ppolicies
            attrs = {}
            attrs['objectClass'] = ['pwdPolicy', 'device']
            attrs['cn'] = ppolicyName
            if ppolicyDesc:
                attrs['description'] = ppolicyDesc
            attrs['pwdattribute'] = self.configPPolicy.ppolicyAttributes['pwdattribute']
            if 'pwdcheckmodule' in self.configPPolicy.ppolicyAttributes:
                attrs['objectClass'].append('pwdPolicyChecker')
                attrs['pwdcheckmodule'] = self.configPPolicy.ppolicyAttributes['pwdcheckmodule']

            # set default attributes for default password policy
            if ppolicyName == self.configPPolicy.ppolicydefault:
                for k in self.configPPolicy.ppolicyAttributes:
                    if type(self.configPPolicy.ppolicyAttributes[k]) == bool:
                        self.configPPolicy.ppolicyAttributes[k] = str(self.configPPolicy.ppolicyAttributes[k]).upper()
                    attrs[k] = str(self.configPPolicy.ppolicyAttributes[k])

            attributes = modlist.addModlist(attrs)
            self.l.add_s(ppolicyDN, attributes)
            self.logger.info("Password policy registered at: %s" % ppolicyDN)

    def removePPolicy(self, ppolicyName):
        """
        Remove a password policy entry from LDAP
        Disallow to remove the default password policy
        """
        if ppolicyName == self.configPPolicy.ppolicydefault:
            return False

        if self.checkPPolicy(ppolicyName):
            ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn
            self.delRecursiveEntry(ppolicyDN)
            # remove ppolicy applied to users
            s = self.l.search_s(self.baseUsersDN, ldap.SCOPE_SUBTREE, "(&(objectClass=pwdPolicy)(pwdPolicySubentry=%s))" % ppolicyDN)
            for user in s:
                uid = user[1]['uid'][0]
                UserPPolicy(uid).removePPolicy()
            return True

        return False

    def updateGroupPPolicy(self, groupName, ppolicyName):
        """
        Set the ppolicy to all group users
        """
        for uid in self.getMembers(groupName):
            UserPPolicy(uid).updatePPolicy(ppolicyName)
        return True

    def getDefaultPPolicy(self):
        """
        Return the default ppolicy entry
        """
        return self.getPPolicy(self.configPPolicy.ppolicydefault)

    def getPPolicy(self, ppolicyName):
        """
        Return a ppolicy entry
        """
        ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn
        res = self.l.search_s(ppolicyDN, ldap.SCOPE_BASE)
        if res:
            return res[0]
        else:
            raise ldap.NO_SUCH_OBJECT

    def listPPolicy(self, filt = ''):
        """
        Get ppolicy list from directory

        @rtype: list
        """
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"
        return self.l.search_s(self.configPPolicy.ppolicydn, ldap.SCOPE_SUBTREE, "(&(objectClass=pwdPolicy)(cn=%s))" % filt)

    def getAttribute(self, nameattribute = None, ppolicyName = None):
        """
        Get the given attribute value of the default password policies.

        @param nameattribute: LDAP attribute name
        @type nameattribute: str

        @returns: the attribute value
        @rtype: str
        """
        if not ppolicyName:
            ppolicyDN = self.configPPolicy.ppolicydefaultdn
        else:
            ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn
        try:
            result = (self.l.search_s(ppolicyDN, ldap.SCOPE_BASE))[0][1]
            if nameattribute == None:
                return result
            elif nameattribute in result:
                return result[nameattribute]
            else:
                return None
        except KeyError:
            return None

    def setAttribute(self, nameattribute, value, ppolicyName = None):
        """
        Set value to the given attribute.

        @param nameattribute: LDAP attribute name
        @type nameattribute: str

        @param value: LDAP attribute value
        @type value: str
        """
        if not ppolicyName:
            ppolicyDN = self.configPPolicy.ppolicydefaultdn
        else:
            ppolicyDN = "cn=" + ppolicyName + "," + self.configPPolicy.ppolicydn

        r = AF().log(PLUGIN_NAME, AA.PPOLICY_MOD_ATTR, [(ppolicyDN, AT.PPOLICY), (nameattribute, AT.ATTRIBUTE)], value)
        if value != None:
            if type(value) == bool:
                value = str(value).upper()
            elif type(value) == int:
                value = str(value)
        try:
            self.l.modify_s(ppolicyDN, [(ldap.MOD_REPLACE,nameattribute,value)])
        except ldap.UNDEFINED_TYPE:
            logging.getLogger().error("Attribute %s isn't defined on ldap" % nameattribute)
        except ldap.INVALID_SYNTAX:
            logging.getLogger().error("Invalid Syntax from the attribute value of %s on ldap" % nameattribute)
        r.commit()

    def getDefaultAttributes (self):
        """
        Returns the list of LDAP password policies attributes.

        @returns: A list of attributes name
        @rtype: list
        """
        ret = []
        for k in self.configPPolicy.ppolicyAttributes:
            ret.append(k)
        return ret

    def setDefaultConfigAttributes (self, ppolicyName = None):
        """
        Set all the password policies attributes to the value specified in the
        plugin configuration file.
        """
        for attribute in self.configPPolicy.ppolicyAttributes:
            self.setAttribute(attribute, self.configPPolicy.ppolicyAttributes[attribute], ppolicyName)


class UserPPolicy(ldapUserGroupControl):

    """
    Class for objects that manage user password policies attributes.
    """

    def __init__(self, uid, conffile = None):
        """
        Class constructor.

        @param uid: user id of the LDAP user entry to manage
        @type uid: str
        """
        ldapUserGroupControl.__init__(self, conffile)
        self.configPPolicy = PPolicyConfig("ppolicy", conffile)
        self.userUid = uid
        self.dn = 'uid=' + uid + ',' + self.baseUsersDN

    def getPPolicyAttribute(self, name = None):
        """
        Get value of the given LDAP attribute.

        @param name: LDAP attribute name
        @type name: str

        @returns: the attribute value
        @rtype: str
        """
        result = self.getUserEntry(self.userUid, operational = True)
        if name == None:
            ret = result
        elif name in result:
            ret = result[name]
        else:
            ret = None
        return ret

    def setPPolicyAttribute(self, nameattribute, value):
        """
        Set the value of the given LDAP attribute.
        Del the attribute if value is None

        @param nameattribute: LDAP attribute name
        @type nameattribute: str

        @param value: LDAP attribute value
        @type value: str
        """
        if value != None:
            r = AF().log(PLUGIN_NAME, AA.PPOLICY_MOD_USER_ATTR, [(self.dn, AT.USER), (nameattribute, AT.ATTRIBUTE)], value)
            if type(value) == bool:
                value = str(value).upper()
            elif type(value) == int:
                value = str(value)
            mode = ldap.MOD_REPLACE
            logging.getLogger().debug('Setting %s to %s' % (nameattribute, value))
        else:
            r = AF().log(PLUGIN_NAME, AA.PPOLICY_DEL_USER_ATTR, [(self.dn, AT.USER), (nameattribute, AT.ATTRIBUTE)], value)
            mode = ldap.MOD_DELETE
            logging.getLogger().debug('Removing %s' % nameattribute)
        try:
            self.l.modify_s(self.dn, [(mode, nameattribute, value)])
        except ldap.UNDEFINED_TYPE:
            logging.getLogger().error("Attribute %s isn't defined on LDAP" % nameattribute)
        except ldap.INVALID_SYNTAX:
            logging.getLogger().error("Invalid Syntax from the attribute value of %s on ldap" % nameattribute)
        r.commit()

    def hasPPolicy(self):
        """
        Returns true if the user owns the pwdPolicy objectClass.

        @returns: return True if the user owns the pwdPolicy objectClass.
        @rtype: boolean
        """
        return "pwdPolicy" in self.getPPolicyAttribute()["objectClass"]

    def getPPolicy(self):
        """
        Return the ppolicy name applied to the user if any
        """
        if self.hasPPolicy():
            ret = self.getPPolicyAttribute("pwdPolicySubentry")
            if ret and ret[0]:
                return ldap.dn.str2dn(ret[0])[0][0][1]
        return False

    def addPPolicy(self, ppolicyName):
        """
        Add the pwdPolicy and pwdPolicySubentry objectClass to the current user,
        and set the pwdPolicySubentry attribute to the select ppolicy DN
        """
        if not self.hasPPolicy():
            r = AF().log(PLUGIN_NAME, AA.PPOLICY_ADD_USER_PPOLICY, [(self.dn, AT.USER)])
            # Get current user entry
            s = self.l.search_s(self.dn, ldap.SCOPE_BASE, attrlist = ['+', '*'])
            c, old = s[0]
            new = copy.deepcopy(old)
            if not "pwdPolicy" in new["objectClass"]:
                new["objectClass"].append("pwdPolicy")
                new["pwdAttribute"] = "userPassword"
                new['pwdPolicySubentry'] = PPolicy().getPPolicy(ppolicyName)[0]
            # Update LDAP
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(self.dn, modlist)
            r.commit()
            return True
        return False

    def updatePPolicy(self, ppolicyName):
        """
        Update the pwdPolicySubentry attribute of the current user
        """
        if self.hasPPolicy():
            if not ppolicyName:
                return self.removePPolicy()
            else:
                # get the ppolicy dn
                ppolicyDN = PPolicy().getPPolicy(ppolicyName)[0]
                r = AF().log(PLUGIN_NAME, AA.PPOLICY_MOD_USER_PPOLICY, [(self.dn, AT.USER)])
                try:
                    self.l.modify_s(self.dn, [(ldap.MOD_REPLACE, 'pwdPolicySubentry', ppolicyDN)])
                except ldap.UNDEFINED_TYPE:
                    logging.getLogger().error("Attribute %s isn't defined on ldap" % 'pwdPolicySubentry')
                except ldap.INVALID_SYNTAX:
                    logging.getLogger().error("Invalid Syntax from the attribute value of %s on ldap" % 'pwdPolicySubentry')
                r.commit()
                return True
        else:
            return self.addPPolicy(ppolicyName)

        return False

    def removePPolicy(self):
        """
        Remove the pwdPolicy objectClass from the current
        user, and the pwdPolicySubentry attribute.
        """
        r = AF().log(PLUGIN_NAME, AA.PPOLICY_DEL_USER_PPOLICY, [(self.dn, AT.USER)])
        # Remove pwdPolicy object class
        self.removeUserObjectClass(self.userUid, 'pwdPolicy')
        # Remove pwdPolicySubentry attribute from current user entry
        s = self.l.search_s(self.dn, ldap.SCOPE_BASE, attrlist = ['+', '*'])
        c, old = s[0]
        new = copy.deepcopy(old)
        if 'pwdPolicySubentry' in new:
            del new['pwdPolicySubentry']
        # Update LDAP
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(self.dn, modlist)
        r.commit()
        return True

    def _strpTime(self, value):
        """
        Common stripping time value tool
        """
        if value.endswith('Z'):
            # Remove trailing Z
            value = value[:-1]
        return calendar.timegm(time.strptime(value, '%Y%m%d%H%M%S'))

    def isAccountLocked(self):
        """
        Check if the user account is locked.

        @returns: -1 if the user account has been locked permanently, 0 if not, else the lock timestamp
        @rtype: int
        """
        user = self.getUserEntry(self.userUid, operational = True)
        if 'pwdAccountLockedTime' in user:
            try:
                ret = self._strpTime(user['pwdAccountLockedTime'][0])
            except ValueError:
                ret = -1
        else:
            ret = 0
        return ret

    def lockAccount(self):
        """
        Lock a LDAP account
        """
        # man slapo-ppolicy
        self.setPPolicyAttribute('pwdAccountLockedTime', '000001010000Z')

    def unlockAccount(self):
        """
        Unlock a LDAP account
        """
        if self.getPPolicyAttribute("pwdAccountLockedTime"):
            self.setPPolicyAttribute("pwdAccountLockedTime", None)

    def passwordHasBeenReset(self):
        """
        @return: True if pwdReset is set (password has been reset)
        @rtype: bool
        """
        pwdReset = self.getPPolicyAttribute("pwdReset")
        return pwdReset == ['TRUE']

    def passwordMustChange(self):
        """
        @return: True if pwdMustChange is set (password must be changed)
        @rtype: bool
        """
        pwdReset = self.getPPolicyAttribute("pwdMustChange")
        return pwdReset == ['TRUE']

    def userMustChangePassword(self):
        """
        if pwdReset is set on the user entry, and ppolicy and pwdMustChange is
        enabled on the user entry, or pwdMustChange is enabled on the default
        password policy, the user must change her password.

        @return: True if the user must change her password
        @rtype: bool
        """
        if self.passwordHasBeenReset():
            # Check user attribute
            if self.passwordMustChange():
                return True
            # Check the user password policy
            elif self.getPPolicy():
                val = PPolicy().getAttribute('pwdMustChange', self.getPPolicy())
                return val == ['TRUE']
            # Else get the default password policy
            else:
                val = PPolicy().getAttribute('pwdMustChange')
                return val == ['TRUE']
        return False

    def isAccountInGraceLogin(self):
        """
        @returns: -1 if the user account in not in grace login, else returns the number of remaining grace logins. 0 means the user can no more bind to the LDAP.
        @rtype int:
        """
        ret = -1
        user = self.getUserEntry(self.userUid, operational = True)

        if 'pwdGraceUseTime' in user:
            count = len(user['pwdGraceUseTime'])
            if 'pwdGraceAuthNLimit' in user:
                ppolicygracelimit = user['pwdGraceAuthNLimit']
            elif self.getPPolicy():
                ppolicygracelimit = PPolicy().getAttribute('pwdGraceAuthNLimit', self.getPPolicy())
            else:
                ppolicygracelimit = PPolicy().getAttribute('pwdGraceAuthNLimit')
            if ppolicygracelimit:
                ret = int(ppolicygracelimit[0]) - count
        return ret

    def isPasswordExpired(self):
        """
        @returns: True if the password is expired
        @rtype: bool
        """
        user = self.getUserEntry(self.userUid, operational = True)
        ret = False
        if 'pwdChangedTime' in user:
            pwdChangedTime = user['pwdChangedTime'][0]
            if 'pwdMaxAge' in user:
                pwdMaxAge = user['pwdMaxAge'][0]
            elif self.getPPolicy():
                pwdMaxAge = PPolicy().getAttribute('pwdMaxAge', self.getPPolicy())[0]
            else:
                pwdMaxAge = PPolicy().getAttribute('pwdMaxAge')[0]
            if pwdMaxAge == "0" or pwdMaxAge == None:
                ret = False
            else:
                last = calendar.timegm(time.strptime(pwdChangedTime[:-1], '%Y%m%d%H%M%S'))
                ret = (time.time() - last) > int(pwdMaxAge)
        return ret

# XML-RPC methods

# for PPolicys management
def checkPPolicy(ppolicyName = None):
    return PPolicy().checkPPolicy(ppolicyName)

def getDefaultPPolicy():
    return PPolicy().getDefaultPPolicy()

def getPPolicy(ppolicyName):
    return PPolicy().getPPolicy(ppolicyName)

def addPPolicy(ppolicyName = None, ppolicyDesc = None):
    return PPolicy().addPPolicy(ppolicyName, ppolicyDesc)

def removePPolicy(ppolicyName):
    return PPolicy().removePPolicy(ppolicyName)

def listPPolicy(filt = ''):
    return PPolicy().listPPolicy(filt)

def getPPolicyAttribute(nameAttribute, ppolicyName = None):
    return PPolicy().getAttribute(nameAttribute, ppolicyName)

def getAllPPolicyAttributes (ppolicyName = None):
    return PPolicy().getAttribute(None, ppolicyName)

def setPPolicyAttribute (nameAttribute, value, ppolicyName = None):
    if value == '': value = None
    return PPolicy().setAttribute(nameAttribute, value, ppolicyName)

def getDefaultPPolicyAttributes ():
    return PPolicy().getDefaultAttributes()

def setPPolicyDefaultConfigAttributes (ppolicyName = None):
    return PPolicy().setDefaultConfigAttributes(ppolicyName)

def updateGroupPPolicy(groupName, ppolicyName = None):
    return PPolicy().updateGroupPPolicy(groupName, ppolicyName)

# for user PPolicy management
def hasUserPPolicy(uid):
    return UserPPolicy(uid).hasPPolicy()

def getUserPPolicy(uid):
    return UserPPolicy(uid).getPPolicy()

def updateUserPPolicy(uid, ppolicyName):
    return UserPPolicy(uid).updatePPolicy(ppolicyName)

def removeUserPPolicy(uid):
    return UserPPolicy(uid).removePPolicy()

def getUserPPolicyAttribut(uid, nameAttribut):
    if nameAttribut == '': nameAttribut = None
    return UserPPolicy(uid).getPPolicyAttribute(nameAttribut)

def setUserPPolicyAttribut(uid, nameAttribut, value):
    if value == '': value = None
    return UserPPolicy(uid).setPPolicyAttribute(nameAttribut, value)

def isAccountLocked(uid):
    return UserPPolicy(uid).isAccountLocked()

def lockAccount(uid):
    return UserPPolicy(uid).lockAccount()

def unlockAccount(uid):
    return UserPPolicy(uid).unlockAccount()

def passwordHasBeenReset(uid):
    return UserPPolicy(uid).passwordHasBeenReset()

def passwordMustBeChanged(uid):
    return UserPPolicy(uid).passwordMustBeChanged()

def userMustChangePassword(uid):
    return UserPPolicy(uid).userMustChangePassword()

def isAccountInGraceLogin(uid):
    return UserPPolicy(uid).isAccountInGraceLogin()

def isPasswordExpired(uid):
    return UserPPolicy(uid).isPasswordExpired()


if __name__ == "__main__":
    #print ldapUserGroupControl().getDetailedUserIntAttr("user1")
    print isPasswordExpired("testpass")
