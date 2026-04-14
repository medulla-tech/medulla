# SPDX-FileCopyrightText:2008 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI
from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.glpi.auth import GlpiAuthenticator
from mmc.plugins.glpi.database import Glpi
from mmc.support.mmctools import getConfigFile


class GlpiProvisionerConfig(ProvisionerConfig):
    def readConf(self):
        ProvisionerConfig.readConf(self)
        try:
            self.doauth = self.getboolean(self.section, "doauth")
        except:
            pass

    def setDefault(self):
        ProvisionerConfig.setDefault(self)
        self.doauth = True


class GlpiProvisioner(ProvisionerI):
    """
    This provisioner can connect to the GLPI login page to force a GLPI user
    creation/sync, and update MMC user right according to the user GLPI profile
    """

    def __init__(self, conffile=None, name="glpi"):
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
            self.logger.warning(
                "User authentication with GLPI web interface failed, but going on with provisioning"
            )
        profiles = Glpi().getUserProfiles(authtoken.getLogin())
        self.logger.debug(
            "User '%s' GLPI's profiles: %s" % (authtoken.getLogin(), str(profiles))
        )
        selected = None
        # Get profiles from DB
        try:
            from pulse2.database.admin import AdminDatabase
            profiles_order = AdminDatabase().get_acl_profiles()
        except Exception as e:
            self.logger.error("Could not get profiles from DB: %s" % e)
            profiles_order = []
        for profile in profiles_order:
            if profile in profiles:
                selected = profile
                break
        if not selected:
            self.logger.info("User GLPI's profile can't be applied")
        else:
            self.logger.debug("Selected GLPI profile is %s" % selected)
            acls = None
            try:
                acls = AdminDatabase().build_acl_string_for_profile(selected)
            except Exception as e:
                self.logger.error("ACL build failed for profile %s: %s" % (selected, e))
            if not acls:
                self.logger.info("No ACL to apply for the GLPI profile %s" % selected)
            else:
                l = ldapUserGroupControl()
                self.logger.info("Setting MMC ACL corresponding to GLPI profile %s: %s", selected, acls)

                uid = authtoken.getLogin()
                entry = l.getDetailedUser(uid)

                obj_classes = [v if isinstance(v, bytes) else str(v).encode("utf-8")
                            for v in entry.get("objectClass", [])]
                if b"lmcUserObject" not in obj_classes:
                    obj_classes.append(b"lmcUserObject")
                    l.changeUserAttributes(uid, "objectClass", obj_classes)

                l.changeUserAttributes(uid, "lmcACL", [acls.encode("utf-8")])
        return authtoken

    def doProvisioning(self, authtoken):
        """
        @return: Deferred resulting to authtoken
        """
        # Perform auth to sync user
        d = GlpiAuthenticator().authenticate(
            authtoken.getLogin(), authtoken.getPassword()
        )
        # get GLPI user profile, and sync it
        d.addCallback(self._cbProvisioning, authtoken)
        return d
