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

from os.path import isfile

from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI
from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.glpi.auth import GlpiAuthenticator
from mmc.plugins.glpi.database import Glpi
from mmc.support.mmctools import getConfigFile

class GlpiProvisionerConfig(ProvisionerConfig):

    def readConf(self):
        PROFILEACL = "profile_acl_"
        ProvisionerConfig.readConf(self)
        try:
            self.doauth = self.getboolean(self.section, "doauth")
        except:
            pass
        for option in self.options(self.section):
            if option.startswith(PROFILEACL):
                value = self.get(self.section, option)
                if isfile(value):
                    acls = open(value, 'r').read().split('\n')
                    # Clean empty lines, and join them by :
                    value = ':' + (':'.join([x for x in acls if x.strip() and x[0] != '#']))
                else:
                    self.profilesAcl[option.replace(PROFILEACL, "")] = value
        self.profilesOrder = self.get(self.section, "profiles_order").split()

    def setDefault(self):
        ProvisionerConfig.setDefault(self)
        self.doauth = True
        self.profilesAcl = {}
        self.profilesOrder = []


class GlpiProvisioner(ProvisionerI):
    """
    This provisioner can connect to the GLPI login page to force a GLPI user
    creation/sync, and update MMC user right according to the user GLPI profile
    """

    def __init__(self, conffile = None, name = "glpi"):
        if not conffile:
            conffile = getConfigFile(name)
        ProvisionerI.__init__(self, conffile, name, GlpiProvisionerConfig)

    def validate(self):
        return True

    def _cbProvisioning(self, auth, authtoken):
        """
        Provision the MMC user account with ACLs
        """
        if not auth:
            self.logger.warning("User authentication with GLPI web interface failed, but going on with provisioning")
        profiles = Glpi().getUserProfiles(authtoken.getLogin())
        self.logger.debug("User '%s' GLPI's profiles: %s" % (authtoken.getLogin(), str(profiles)))
        self.logger.debug("Profiles order (from ini configuration): %s" % (self.config.profilesOrder))
        selected = None
        for profile in self.config.profilesOrder:
            if profile in profiles:
                selected = profile
                break
        if not selected:
            self.logger.info("User GLPI's profile can't be applied")
        else:
            self.logger.debug("Selected GLPI profile is %s" % selected)
            try:
                acls = self.config.profilesAcl[selected.lower()]
            except KeyError:
                acls = None
            if not acls:
                self.logger.info("No ACL to apply for the GLPI profile %s" % selected)
            else:
                l = ldapUserGroupControl()
                self.logger.info("Setting MMC ACL corresponding to GLPI profile %s: %s" % (selected, acls))
                uid = authtoken.getLogin()
                entry = l.getDetailedUser(uid)
                if not "lmcUserObject" in entry["objectClass"]:
                    entry["objectClass"].append("lmcUserObject")
                    l.changeUserAttributes(uid, "objectClass", entry["objectClass"])
                l.changeUserAttributes(authtoken.getLogin(), "lmcAcl", acls)
        return authtoken

    def doProvisioning(self, authtoken):
        """
        @return: Deferred resulting to authtoken
        """
        # Perform auth to sync user
        d = GlpiAuthenticator().authenticate(authtoken.getLogin(), authtoken.getPassword())
        # get GLPI user profile, and sync it
        d.addCallback(self._cbProvisioning, authtoken)
        return d
