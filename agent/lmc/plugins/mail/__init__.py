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

#
# Mail plugin
#

from lmc.plugins.base import ldapUserGroupControl
from lmc.support.config import *
import lmc
import ldap
import copy
import logging


VERSION = "1.1.1"
APIVERSION = "2:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    ldapObj = ldapUserGroupControl()
    logger = logging.getLogger()

    schema = ldapObj.getSchema("mailAccount")
    if len(schema) <= 0:
        logger.error("mailAccount schema is not included in LDAP directory");
        return False
    
    config = MailConfig("mail")
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

def removeMail(uid):
    MailControl().removeUserObjectClass(uid, 'mailAccount')

def hasMailObjectClass(uid):
    return MailControl().hasMailObjectClass(uid)

def hasVDomainSupport():
    return MailControl().hasVDomainSupport()

def addVDomain(domain):
    MailControl().addVDomain(domain)

def delVDomain(domain):
    MailControl().delVDomain(domain)

def setVDomainDescription(domain, description):
    MailControl().setVDomainDescription(domain, description)

def getVDomain(domain):
    return MailControl().getVDomain(domain)    

def getVDomains(filt):
    return MailControl().getVDomains(filt)

def getVDomainUsersCount(domain):
    return MailControl().getVDomainUsersCount(domain)

def getVDomainUsers(domain, filt):
    return MailControl().getVDomainUsers(domain, filt)

class MailConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        try: self.vDomainSupport = self.getboolean("main", "vDomainSupport")
        except: pass
        if self.vDomainSupport:
            self.vDomainDN = self.get("main", "vDomainDN")
        # FIXME: could be factorized
        USERDEFAULT = "userDefault"            
        if self.has_section(USERDEFAULT):
            for option in self.options(USERDEFAULT):
                self.userDefault[option] = self.get(USERDEFAULT, option)

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.vDomainSupport = False
        self.userDefault = {}

class MailControl(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        lmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)
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
        if not mailbox:
            # FIXME: should be factorized and put elsewhere
            # Get current user entry
            dn = 'uid=' + uid + ',' + self.baseUsersDN
            s = self.l.search_s(dn, ldap.SCOPE_BASE)
            c, old = s[0]
            new = old.copy()
            # Modify attributes
            for attribute, value in self.configMail.userDefault.items():
                if "%" in value:
                    for a, v in old.items():
                        v = v[0]
                        if type(v) == str:
                            value = value.replace("%" + a + "%", v)
                found = False
                for key in new.keys():
                    if key.lower() == attribute:
                        new[key] = value
                        found = True
                        break
                if not found: new[attribute] = value                

            # Update LDAP
            modlist = ldap.modlist.modifyModlist(old, new)
            self.l.modify_s(dn, modlist)
        else:
            self.changeUserAttributes(uid, 'mailbox', mailbox)

    def hasMailObjectClass(self, uid):
        """
        Return true if the user owns the mailAccount objectClass.

        @param uid: user name
        @type uid: str

        @return: return True if the user owns the mailAccount objectClass.
        @rtype: boolean
        """
        return "mailAccount" in self.getDetailedUser(uid)["objectClass"]

    def addMailObjectClass(self, uid, maildrop = None):
        if maildrop == None: maildrop = uid
        cn = 'uid=' + uid + ', ' + self.baseUsersDN
        attrs = []
        attrib = self.l.search_s(cn, ldap.SCOPE_BASE)

        c, attrs = attrib[0]
        newattrs = copy.deepcopy(attrs)

        if not 'mailAccount' in newattrs["objectClass"]:
            newattrs["objectClass"].append('mailAccount')

        newattrs['maildrop'] = maildrop
        mlist = ldap.modlist.modifyModlist(attrs, newattrs)

        self.l.modify_s(cn, mlist)

    def getVDomainUsersCount(self, domain):
        return len(self.search("(&(objectClass=mailAccount)(mail=*@%s))" % domain, self.baseUsersDN, [""]))
        
    def getVDomainUsers(self, domain, filt = ""):
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"
        return self.l.search_s(self.baseUsersDN, ldap.SCOPE_SUBTREE, "(&(objectClass=mailAccount)(mail=*@%s)(|(uid=%s)(givenName=%s)(sn=%s)(mail=%s)))" % (domain, filt, filt, filt, filt), ["uid", "givenName", "sn", "mail"])
    
