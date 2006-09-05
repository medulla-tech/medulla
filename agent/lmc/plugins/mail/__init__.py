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
import lmc
import ldap
import copy
import logging


VERSION = "1.1.0"
APIVERSION = "1:0:0"
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

    return True

def changeMail(uid,mail):
    MailControl().changeMail(uid,mail)

def changeMailEnable(uid, enabled):
    MailControl().changeMailEnable(uid, enabled)

def changeMaildrop(uid, maildroplist):
    MailControl().changeMaildrop(uid, maildroplist)

def changeMailalias(uid, mailaliaslist):
    MailControl().changeMailalias(uid, mailaliaslist)

def removeMail(uid):
    MailControl().removeUserObjectClass(uid, 'mailAccount')
    #WARNING: remove mail field if mail account disable
    MailControl().changeUserAttributes(uid, 'mail', '')

def hasMailObjectClass(uid):
    return MailControl().hasMailObjectClass(uid)


class MailControl(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        lmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)

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

        if len(maildroplist)==0:
            return

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

    def changeMail(self, uid, mail):
        """
        Change the user mail aliases.

        @param uid: user name
        @type uid: str
        @param mailaliaslist: a list of all mail aliases
        @type mailaliaslist: list
        """
        if not self.hasMailObjectClass(uid): self.addMailObjectClass(uid)
        self.changeUserAttributes(uid, 'mail', mail)

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
        if maildrop == None:
            maildrop = uid
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
