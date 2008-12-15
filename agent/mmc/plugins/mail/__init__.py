# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#
# Mail plugin
#

from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.base import delete_diacritics
from mmc.support.config import *
import mmc
import ldap
import copy
import logging


VERSION = "2.3.2"
APIVERSION = "6:1:4"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    ldapObj = ldapUserGroupControl()
    logger = logging.getLogger()

    config = MailConfig("mail")
    if config.disabled:
        logger.warning("Plugin mail: disabled by configuration.")
        return False

    mailSchema = {
        "mailAccount" : ["mail", "mailalias", "maildrop", "mailenable", "mailbox", "mailuserquota", "mailhost"],
        "mailGroup" : ["mail"],
        "mailDomain" : ["virtualdomain", "virtualdomaindescription", "mailuserquota"],
        }

    for objectClass in mailSchema:
        schema = ldapObj.getSchema(objectClass)
        if not len(schema):
            logger.error("LDAP mail schema is not up to date: %s objectClass is not included in LDAP directory" % objectClass);
            return False        
        for attribute in mailSchema[objectClass]:
            if not attribute in schema:
                logger.error("LDAP mail schema is not up to date: %s attribute is not included in LDAP directory" % attribute);
                return False

    if config.vDomainSupport:        
        # Create required OU
        head, path = config.vDomainDN.split(",", 1)
        ouName = head.split("=")[1]
        try:
            ldapObj.addOu(ouName, path)
            logger.info("Created OU " + config.vDomainDN)
        except ldap.ALREADY_EXISTS:
            pass        

    return True

def changeMail(uid,mail):
    MailControl().changeMail(uid,mail)

def changeMailEnable(uid, enabled):
    MailControl().changeMailEnable(uid, enabled)

def changeMaildrop(uid, maildroplist):
    MailControl().changeMaildrop(uid, maildroplist)

def changeMailalias(uid, mailaliaslist):
    MailControl().changeMailalias(uid, mailaliaslist)

def changeMailbox(uid, mailbox):
    MailControl().changeMailbox(uid, mailbox)

def changeMailhost(uid, mailhost):
    MailControl().changeMailhost(uid, mailhost)

def removeMail(uid):
    MailControl().removeUserObjectClass(uid, 'mailAccount')

def removeMailGroup(group):
    MailControl().removeGroupObjectClass(group, 'mailGroup')

def addMailGroup(group, mail):
    MailControl().addMailGroup(group, mail)

def hasMailObjectClass(uid):
    return MailControl().hasMailObjectClass(uid)

def hasMailGroupObjectClass(uid):
    return MailControl().hasMailGroupObjectClass(uid)

def hasVDomainSupport():
    return MailControl().hasVDomainSupport()

def addVDomain(domain):
    MailControl().addVDomain(domain)

def delVDomain(domain):
    MailControl().delVDomain(domain)

def setVDomainDescription(domain, description):
    MailControl().setVDomainDescription(domain, description)

def setVDomainQuota(domain, quota):
    MailControl().setVDomainQuota(domain, quota)

def resetUsersVDomainQuota(domain):
    MailControl().resetUsersVDomainQuota(domain)

def getVDomain(domain):
    return MailControl().getVDomain(domain)    

def getVDomains(filt):
    return MailControl().getVDomains(filt)

def getVDomainUsersCount(domain):
    return MailControl().getVDomainUsersCount(domain)

def getVDomainUsers(domain, filt):
    return MailControl().getVDomainUsers(domain, filt)

def computeMailGroupAlias(group):
    return MailControl().computeMailGroupAlias(group)

def deleteMailGroupAliases(group):
    return MailControl().deleteMailGroupAliases(group)

def syncMailGroupAliases(group, foruser = "*"):
    return MailControl().syncMailGroupAliases(group, foruser)

class MailConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        try: self.vDomainSupport = self.getboolean("main", "vDomainSupport")
        except: pass
        if self.vDomainSupport:
            self.vDomainDN = self.get("main", "vDomainDN")

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.vDomainSupport = False
        self.userDefault = {}

class MailControl(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        mmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)
        self.configMail = MailConfig("mail", conffile)

    def hasVDomainSupport(self):
        return self.configMail.vDomainSupport

    def addVDomain(self, domain):
        """
        Add a virtual mail domain name entry in directory

        @param domain: virtual mail domain name
        @type domain: str
        """
        dn = "virtualdomain=" + domain + ", " + self.configMail.vDomainDN
        entry = {
            "virtualdomain" : domain,
            "objectClass" :  ("mailDomain", "top")
            }
        modlist = ldap.modlist.addModlist(entry)
        self.l.add_s(dn, modlist)        

    def delVDomain(self, domain):
        """
        Del a virtual mail domain name entry from directory

        @param domain: virtual mail domain name
        @type domain: str
        """
        dn = "virtualdomain=" + domain + ", " + self.configMail.vDomainDN
        self.delRecursiveEntry(dn)

    def setVDomainDescription(self, domain, description):
        """
        Set the virtualdomaindescription of a virtual mail domain name

        @param domain: virtual mail domain name
        @type domain: str

        @param description: description
        @type description: unicode
        """        
        dn = "virtualdomain=" + domain + ", " + self.configMail.vDomainDN
        description = description.encode("utf-8")
        if description:
            self.l.modify_s(dn, [(ldap.MOD_REPLACE, "virtualdomaindescription", description)])
        else:
            self.l.modify_s(dn, [(ldap.MOD_REPLACE, "virtualdomaindescription", "null")])
            self.l.modify_s(dn, [(ldap.MOD_DELETE, "virtualdomaindescription", "null")])

    def setVDomainQuota(self, domain, quota):
        """
        Set the quota of a virtual mail domain name

        @param domain: virtual mail domain name
        @type domain: str

        @param quota: created user quota in the virtual domain
        @type description: unicode
        """        
        dn = "virtualdomain=" + domain + ", " + self.configMail.vDomainDN
        try:
            int(quota)
        except ValueError:
            quota = None
        if quota:
            self.l.modify_s(dn, [(ldap.MOD_REPLACE, "mailuserquota", quota)])
        else:
            self.l.modify_s(dn, [(ldap.MOD_DELETE, "mailuserquota", None)])

    def resetUsersVDomainQuota(self, domain):
        """
        Reset the quota of all users in the given virtual mail domain

        @param domain: virtual mail domain name
        @type domain: str
        """
        vdomain = self.getVDomain(domain)
        mailuserquota = vdomain[0][1]["mailuserquota"][0]
        for user in self.getVDomainUsers(domain):
            self.changeUserAttributes(user[1]["uid"][0], "mailuserquota", mailuserquota)

    def getVDomain(self, domain):
        """
        Get a virtual mail domain name entry from directory

        @param domain: virtual mail domain name
        @type domain: str

        @rtype: dict
        """
        dn = "virtualdomain=" + domain + ", " + self.configMail.vDomainDN
        return self.l.search_s(dn, ldap.SCOPE_BASE)

    def getVDomains(self, filt = ""):
        """
        Get virtual mail domain name list from directory

        @rtype: dict
        """
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"        
        return self.l.search_s(self.configMail.vDomainDN, ldap.SCOPE_SUBTREE, "(&(objectClass=mailDomain)(virtualdomain=%s))" % filt)

    def changeMailEnable(self, uid, enabled):
        """
        Set the user mailenable attribute.
        This tells if the user receive mail or not.

        @param uid: user name
        @type uid: str
        @param mailenable: Boolean to specify if mail is enabled or not
        @type mailenable: bool
        """
        if not self.hasMailObjectClass(uid):
            self.addMailObjectClass(uid)
        if enabled:
            self.changeUserAttributes(uid, 'mailenable', 'OK')
        else:
            self.changeUserAttributes(uid, 'mailenable', 'NONE')

    def changeMaildrop(self, uid, maildroplist):
        """
        Change the user mail drop.

        @param uid: user name
        @type uid: str
        @param maildroplist: a list of all mail drop
        @type maildroplist: list
        """
        if not self.hasMailObjectClass(uid): self.addMailObjectClass(uid)
        self.changeUserAttributes(uid, 'maildrop', maildroplist)

    def changeMailalias(self, uid, mailaliaslist):
        """
        Change the user mail aliases.

        @param uid: user name
        @type uid: str
        @param mailaliaslist: a list of all mail aliases
        @type mailaliaslist: list
        """
        if not self.hasMailObjectClass(uid): self.addMailObjectClass(uid)
        self.changeUserAttributes(uid, 'mailalias', mailaliaslist)

    def changeMailbox(self, uid, mailbox):
        """
        Change the user mailbox attribute (mail delivery directory).

        @param uid: user name
        @type uid: str
        @param mailbox: a list of all mail aliases
        @type mailbox: mailbox value
        """
        if not self.hasMailObjectClass(uid): self.addMailObjectClass(uid)
        if mailbox: self.changeUserAttributes(uid, 'mailbox', mailbox)

    def changeMailhost(self, uid, mailhost):
        """
        Change the user mailhost attribute (mail delivery server).

        @param uid: user name
        @type uid: str
        @param mailhost: the FQDN or IP of the mail server
        @type mailhost: str
        """
        if not self.hasMailObjectClass(uid): self.addMailObjectClass(uid)
        self.changeUserAttributes(uid, 'mailhost', mailhost)

    def hasMailObjectClass(self, uid):
        """
        Return true if the user owns the mailAccount objectClass.

        @param uid: user name
        @type uid: str

        @return: return True if the user owns the mailAccount objectClass.
        @rtype: boolean
        """
        return "mailAccount" in self.getDetailedUser(uid)["objectClass"]

    def hasMailGroupObjectClass(self, group):
        """
        Return true if the group owns the mailGroup objectClass.

        @param group: group name
        @type group: str

        @return: return True if the user owns the mailGroup objectClass.
        @rtype: boolean
        """
        return "mailGroup" in self.getDetailedGroup(group)["objectClass"]

    def addMailObjectClass(self, uid, maildrop = None):
        # Get current user entry
        dn = 'uid=' + uid + ',' + self.baseUsersDN
        s = self.l.search_s(dn, ldap.SCOPE_BASE)
        c, old = s[0]
        new = self._applyUserDefault(old, self.configMail.userDefault)

        if not "mailAccount" in new["objectClass"]:
            new["objectClass"].append("mailAccount")

        if maildrop == None: maildrop = uid
        new["maildrop"] = maildrop

        if self.hasVDomainSupport():
            # If the user has her/his mail address in a VDomain, set quota according to domain policy
            maildomain = new["mail"][0].split("@")[1]
            try:
                vdomain = self.getVDomain(maildomain)
                new["mailuserquota"] = vdomain[0][1]["mailuserquota"]
            except ldap.NO_SUCH_OBJECT:
                pass
            except KeyError:
                pass

        # Update LDAP
        modlist = ldap.modlist.modifyModlist(old, new)
        self.l.modify_s(dn, modlist)

    def getVDomainUsersCount(self, domain):
        return len(self.search("(&(objectClass=mailAccount)(mail=*@%s))" % domain, self.baseUsersDN, [""]))
        
    def getVDomainUsers(self, domain, filt = ""):
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"
        return self.l.search_s(self.baseUsersDN, ldap.SCOPE_SUBTREE, "(&(objectClass=mailAccount)(mail=*@%s)(|(uid=%s)(givenName=%s)(sn=%s)(mail=%s)))" % (domain, filt, filt, filt, filt), ["uid", "givenName", "sn", "mail"])

    def addMailGroup(self, group, mail):
        group = group.encode("utf-8")
        cn = 'cn=' + group + ', ' + self.baseGroupsDN
        attrs = []
        attrib = self.l.search_s(cn, ldap.SCOPE_BASE)
        c, attrs = attrib[0]
        newattrs = copy.deepcopy(attrs)
        if not 'mailGroup' in newattrs["objectClass"]:
            newattrs["objectClass"].append('mailGroup')
        newattrs['mail'] = mail
        mlist = ldap.modlist.modifyModlist(attrs, newattrs)
        self.l.modify_s(cn, mlist)

    def searchMailGroupAlias(self, mail):
        ret = self.search("(&(cn=*)(mail=%s@*))" % mail, self.baseGroupsDN, ["cn"])
        return len(ret) > 0
    
    def computeMailGroupAlias(self, group):
        """
        Find a mail alias that fits for a group.

        Non ASCII characters are replaced, and spaces are replaced with hyphens

        @param group: group name
        @type group: str

        @return: return the computed mail alias, or an empty string if it already exists
        @rtype: str
        """
        group = group.lower()
        group = delete_diacritics(group)
        group = group.replace(" ", "-")
        if self.searchMailGroupAlias(group):
            # This alias already exists
            return ""
        else:
            return group

    def deleteMailGroupAliases(self, group):
        """
        Remove the alias of this group from all user entries
        """ 
        if hasMailGroupObjectClass(group):
            mailgroup = self.getDetailedGroup(group)["mail"][0]
            users = self.search("(&(uid=*)(mailalias=%s))" % mailgroup, self.baseUsersDN, ["uid", "mailalias"])
            for user in users:
                uid = user[0][1]["uid"][0]
                mailaliases = user[0][1]["mailalias"]
                mailaliases.remove(mailgroup)
                self.changeMailalias(uid, mailaliases)

    def syncMailGroupAliases(self, group, foruser = "*"):
        """
        Sync all users mail aliases for this group
        """
        if hasMailGroupObjectClass(group):
            mailgroup = self.getDetailedGroup(group)["mail"][0]
            groupusers = self.getMembers(group)
            allusers = self.search("(&(uid=%s)(objectClass=mailAccount))" % foruser, self.baseUsersDN, ["uid", "mailalias"])
            for user in allusers:
                uid = user[0][1]["uid"][0]
                try:
                    mailaliases = user[0][1]["mailalias"]
                except KeyError:
                    mailaliases = []
                if uid in groupusers:
                    # Add group mail alias for users of the group that don't have it
                    if not mailgroup in mailaliases:
                        mailaliases.append(mailgroup)
                        self.changeMailalias(uid, mailaliases)
                else:
                    # Remove group mail alias for users that have it but are not in the group
                    if mailgroup in mailaliases:
                        mailaliases.remove(mailgroup)
                        self.changeMailalias(uid, mailaliases)
