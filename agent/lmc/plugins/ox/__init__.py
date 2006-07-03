#!/usr/bin/python
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

import ldap
import ldap.modlist
import copy
# PostgreSQL connection
import psycopg
from lmc.support import lmctools
from lmc.support.lmcException import lmcException
import lmc.plugins.base
from lmc.plugins.base import ldapUserGroupControl
import logging
import os
import ConfigParser

VERSION = "1.0.0"
APIVERSION = "1:0:0"
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
    configParser = lmctools.getConfigParser("ox")

    logger = logging.getLogger()
    ret = False
    if (configParser.get("main","disable")=="1"):
        logger.info("ox plugin disabled by configuration.")
    else:
        oxcontrol = None
        try:
            oxcontrol = oxControl()
        except Exception, e:
            logger.info("ox plugin can't be enabled: error: " + str(e))

        if oxcontrol:
            if os.path.exists(oxcontrol.oxroot):
                ret = True
                if oxcontrol.version == "0.8.0-6":
                    logger.info("Migrating users to Open-Xchange " + configParser.get("main","version"))
                    migrateUser()
            else:
                logger.error("Open-Xchange is not installed.")

    ### verify is schema is present
    try:
        ldapObj = ldapUserGroupControl()
        ret = True
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False

    # Test if the OX LDAP schema is available in the directory
    try:
         schema =  ldapObj.getSchema("OXUserObject")
         if len(schema) <= 0:
             logger.error("OX schema seems not be include in LDAP directory");
             return False
    except:
        logger.exception("invalid schema")
        return False



    return ret

def isOxUser(uid):
    """
    return if it's an OXUser or not

    @param uid: user name
    @type uid: str

    @return: return True if it's an OxUser
    @rtype: boolean
    """
    logger = logging.getLogger()
    logger.info( "debug :"+str(uid))
    logger.info(lmc.plugins.base.getUserAttributes(uid,"objectClass"))

    #if lmc.plugins.base.existUser(uid):
    return "OXUserObject" in lmc.plugins.base.getUserAttributes(uid,"objectClass")
    #else: return False

def addOxAttr(uid,domain,lang,timezone):
    """
    add OxAttributes
    @param uid: user name
    @param cn = uid+baseDN
    @param domain: mail domain for ox
    @param lang: lang (EN,FR)
    @param timezone: timezone for ox

    add OxAttributes in ldap.
    create ou=addr
    Insert in postgresql
    launch java applet, creating ox entities
    """
    oxc = oxControl()
    return oxc.addOxAttr(uid,domain,lang,timezone)

def delOxAttr(uid):
    """
    remove ox Attributes
    @param uid: user name

    deleting all OxAttributes from ldap, referencing Ox Ldap Schema
    delete ou=addr
    delete postgresql line
    launch java applet, deleting ox entities
    """
    oxc = oxControl()
    return oxc.delOxAttr(uid)

#change main UserAttributes
def changeUserOxAttributes(uid,domain,lang,timezone):
    """
    change OxAttributes
    @param uid: user name
        cn = uid+baseDN
    @param domain: mail domain for ox
    @param lang: lang (EN,FR)
    @param timezone: timezone for ox

    use ldapObj.changeUserAttributes to change ldap attributes
    """
    ldapObj = lmc.plugins.base.ldapUserGroupControl()
    ldapObj.changeUserAttributes(uid,"mail",uid+"@"+domain)
    ldapObj.changeUserAttributes(uid,"mailDomain",domain)
    ldapObj.changeUserAttributes(uid,"preferredLanguage",lang)
    ldapObj.changeUserAttributes(uid,"OXTimeZone",timezone)
    return 0


class oxControl(ldapUserGroupControl):

    def __init__(self, conffile = "/etc/lmc/plugins/ox.ini", conffilebase = "/etc/lmc/plugins/base.ini"):
        """
        Object for managing OX users
        """
        ldapUserGroupControl.__init__(self, conffilebase)
        self._setDefaultOXConfig()
        self._readOxConfig(conffile)

    def _setDefaultOXConfig(self):
        """
        Set default config options for OX plugin
        """
        self.oXorganization = "Linbox"
        self.version = "0.8.0-5"

    def _readOxConfig(self, conffile):
        """
        Read OX plugin conf file
        """
        cp = ConfigParser.ConfigParser()
        cp.read(conffile)
        self.oxroot = cp.get("main", "oxroot")
        self.oxdbname = cp.get("main", "oxdbname")
        self.oxdbuser = cp.get("main", "oxdbuser")
        self.oxdbpassword = cp.get("main", "oxdbpassword")
        self.javapath = cp.get("main", "javapath")
        self.jarpath = cp.get("main", "jarpath")
        try: self.oXorganization = cp.get("main", "organization")
        except: pass
        try: self.version = cp.get("main", "version")
        except: pass

    def addOxAttr(self,uid,domain,lang,timezone):
        """Give attributes to an OXUser"""
        cn='uid='+uid+', '+ self.baseUsersDN
        attrs= []
        attrib = self.l.search_s(cn, ldap.SCOPE_BASE)

        c,attrs=attrib[0]
        newattrs = copy.deepcopy(attrs)

        if (not 'OXUserObject' in newattrs["objectClass"]):
            newattrs["objectClass"].append('OXUserObject')

        if not "OpenLDAPaci" in newattrs:
            newattrs["OpenLDAPaci"]='1#entry#grant;r,w,s,c;cn,initials,mail,title,ou,l,birthday,description,street,postalcode,st,c,oxtimezone,homephone,mobile,pager,facsimiletelephonenumber,telephonenumber,labeleduri,jpegphoto,loginDestination,sn,givenname,;r,s,c;[all]#self#"'

        configParser = lmctools.getConfigParser("ox")

        if (self.version=="0.8.0-6"):
            newattrs["lnetMailAccess"]="TRUE"
            newattrs["mailEnabled"]="OK"
        else:
            newattrs["lnetMailAccess"]="5"
            newattrs["mailEnabled"]="TRUE"

        newattrs["mail"]=uid+"@"+domain
        newattrs["mailDomain"]=domain
        newattrs["o"]=self.oXorganization
        newattrs["preferredLanguage"]=lang
        newattrs["userCountry"]="Tuxworld"


        newattrs["OXAppointmentDays"]="5"
        newattrs["OXGroupID"]="500"
        newattrs["OXTaskDays"]="5"
        newattrs["OXTimeZone"]=timezone

        # add OX attributes
        mlist = ldap.modlist.modifyModlist(attrs, newattrs)

        try:
            self.l.modify_s(cn, mlist)
            # if there's an error, surely link to openLdapaciProblem
        except ldap.LDAPError, error:
            del newattrs["OpenLDAPaci"]
            mlist = ldap.modlist.modifyModlist(attrs, newattrs)
            try:
                self.l.modify_s(cn, mlist)
            except ldap.LDAPError, e:
                raise lmcException(e)

        # Add addresses ou for user
        addrdn= 'ou=addr, '+cn
        addr_info = {'ou':'addr',
                    'objectClass':('organizationalUnit','top')}
        attributes=[ (k,v) for k,v in addr_info.items() ]

        try:
            self.l.add_s(addrdn,attributes)
        except ldap.LDAPError, e:
            raise lmcException(e)

        # Add correct rights to pgsql
        o = psycopg.connect("dbname=%s user=%s password=%s" % (self.oxdbname, self.oxdbuser, self.oxdbpassword))
        c = o.cursor()
        query="INSERT INTO usr_general_rights SELECT creating_date, created_from, changing_date, changed_from,text('"+uid+"'), addr_u, addr_r, addr_d, cont_u, cont_r, cont_d, data_u, data_r, data_d, serie_u, serie_r, serie_d, task_u, task_r, task_d, refer, proj_u, proj_r, proj_d, dfolder_u, dfolder_r, dfolder_d, doc_u, doc_r, doc_d, knowl_u, knowl_r, knowl_d, bfolder_u, bfolder_r, bfolder_d, bookm_u, bookm_r, bookm_d, pin_u, pin_r, pin_d, forum_n, fentrie_n, setup, pin_public, internal, int_groups, kfolder_u, kfolder_r, kfolder_d, webmail FROM sys_gen_rights_template WHERE login LIKE 'default_template'"
        c.execute(query)
        o.commit()
        o.close()

        # Executing folder creation
        lmctools.shlaunch('%(javapath)s -Dopenexchange.propfile=%(oxroot)s/etc/groupware/system.properties -classpath %(oxroot)s/lib/comfiretools.jar:%(oxroot)s/lib/nas.jar:%(jarpath)s/postgresql.jar com.openexchange.tools.oxfolder.OXFolderAction addUser ' % {"javapath" : self.javapath, "oxroot" : self.oxroot, "jarpath" : self.jarpath} + uid + ' ' + lang + ' 2>&1 >/dev/null')

        return 0


    def delOxAttr(self,uid):
        """
        delete oxattribute for an user

        @param uid: login name
        @type uid: str
        """

        cn='uid='+uid+', '+self.baseUsersDN
        ldapObj = lmc.plugins.base.ldapUserGroupControl()
        ldapObj.removeUserObjectClass(uid,'OXUserObject')
        # remove right in pgsql
        o = psycopg.connect("dbname=%s user=%s password=%s" % (self.oxdbname, self.oxdbuser, self.oxdbpassword))
        c = o.cursor()
        query="DELETE FROM usr_general_rights WHERE login LIKE '"+uid+"'"
        c.execute(query)
        o.commit()
        o.close()

        # remove ou=addr
        ldapObj = lmc.plugins.base.ldapUserGroupControl()
        ldapObj.delRecursiveEntry("ou=addr, "+cn)

        # launch java applet
        lmctools.shlaunch('%(javapath)s -Dopenexchange.propfile=%(oxroot)s/etc/groupware/system.properties -classpath %(oxroot)s/lib/intranet.jar:%(oxroot)s/lib/comfiretools.jar:%(oxroot)s/lib/nas.jar:%(jarpath)s/postgresql.jar com.openexchange.groupware.deleteUserGroups deleteUser ' % {"javapath" : self.javapath, "oxroot" : self.oxroot, "jarpath" : self.jarpath} + uid)

        return 0

def migrateUser():
    """
    Migrate user LDAP attributes from Open-Xchange 0.8.0-5 to 0.8.0-6
    """
    logger = logging.getLogger()
    arr = []
    arr = lmc.plugins.base.getUsersLdap()

    userOx = []

    for user in arr:
        if 'OXUserObject' in user['obj']:
	    userOx.append(user['uid'])

    migrateUser = []

    for userid in userOx:
        attr = lmc.plugins.base.getUserAttributes(userid,"mailEnabled")
        if 'TRUE' in attr:
            logger.info("migrating "+userid)
            ldapObj = lmc.plugins.base.ldapUserGroupControl()
            ldapObj.changeUserAttributes(userid,"mailEnabled","OK")
            ldapObj.changeUserAttributes(userid,"lnetMailAccess","TRUE")
            migrateUser.append(userid)
