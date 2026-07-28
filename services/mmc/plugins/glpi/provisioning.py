# SPDX-FileCopyrightText:2008 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import xmlrpc.client

from twisted.internet import threads

from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI
from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.glpi.auth import GlpiAuthenticator
from mmc.plugins.glpi.database import Glpi
from mmc.support.mmctools import getConfigFile
from mmc.support.apirest.glpi import GLPIClient, GLPIClientApiV1, GLPIAPIError

logger = logging.getLogger()


def _build_glpi_client():
    """
    Build a GLPI REST client with an open session, using the connection
    parameters stored in admin.saas_application. Same resolution logic as
    Glpi().delMachine() (apirest.php / api.php/v1 fallback).

    @return: a connected GLPIClient/GLPIClientApiV1, or None on failure.
    """
    from pulse2.database.admin import AdminDatabase

    initparametre = AdminDatabase().get_CONNECT_API()
    for cle in ["glpi_mmc_app_token", "glpi_url_base_api", "glpi_root_user_token"]:
        if not initparametre.get(cle):
            logger.error(
                "GLPI provisioning: clé '%s' manquante/vide dans saas_application" % cle
            )
            return None

    base = (initparametre.get("glpi_url_base_api") or "").rstrip("/")
    if base.endswith("/api.php/v1"):
        attempts = [
            (GLPIClientApiV1, base),
            (GLPIClient, base[: -len("/api.php/v1")] + "/apirest.php"),
        ]
    elif base.endswith("/apirest.php"):
        attempts = [
            (GLPIClient, base),
            (GLPIClientApiV1, base[: -len("/apirest.php")] + "/api.php/v1"),
        ]
    else:
        attempts = [
            (GLPIClient, base + "/apirest.php"),
            (GLPIClientApiV1, base + "/api.php/v1"),
        ]

    for client_class, candidate_base in attempts:
        try:
            client = client_class(
                app_token=initparametre.get("glpi_mmc_app_token"),
                url_base=candidate_base,
                user_token=initparametre.get("glpi_root_user_token"),
            )
            client.init_session()
            if getattr(client, "SESSION_TOKEN", None):
                return client
        except GLPIAPIError as e:
            logger.error(
                "GLPI init failed with %s on %s: %s"
                % (client_class.__name__, candidate_base, e.feedback.to_dict())
            )
        except Exception as e:
            logger.error(
                "GLPI init failed with %s on %s: %s"
                % (client_class.__name__, candidate_base, e)
            )
    logger.error("GLPI provisioning: impossible d'ouvrir une session API GLPI")
    return None


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
                from mmc.plugins.admin import _get_install_type
                acls = AdminDatabase().build_acl_string_for_profile(selected, _get_install_type())
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

    def _ensure_glpi_user(self, authtoken):
        """
        Blocking call (runs in a thread): make sure the user exists in GLPI.

        If the user is missing, it is created via the GLPI REST API in the
        root entity (0) with the Self-Service profile. A super-admin can then
        refine profile/ACL from the GLPI UI. Idempotent: an existing user
        (e.g. already auto-created on a GLPI web login) is left untouched.

        @return: True if the user exists/was created in GLPI, else False.
        """
        login = authtoken.getLogin()
        client = _build_glpi_client()
        if not client:
            self.logger.error(
                "GLPI provisioning: no REST client, user '%s' not created" % login
            )
            return False
        try:
            users = client.get_list_users() or []
            if any((u.get("name") or "") == login for u in users):
                self.logger.debug("GLPI user '%s' already exists" % login)
                return True

            # Take firstname/lastname from the external LDAP entry
            infos = authtoken.getInfos()[1] or {}

            def _first(attr):
                val = infos.get(attr)
                if isinstance(val, (list, tuple)) and val:
                    val = val[0]
                if isinstance(val, bytes):
                    val = val.decode("utf-8", "ignore")
                return val or None

            password = authtoken.getPassword()
            if isinstance(password, xmlrpc.client.Binary):
                password = password.data.decode("utf-8", "ignore")
            if isinstance(password, bytes):
                password = password.decode("utf-8", "ignore")

            client.create_user(
                identifier=login,
                firstname=_first("givenName"),
                lastname=_first("sn"),
                password=password,
                id_entity=0,        # entité racine
                id_profile=None,    # None => profil Self-Service par défaut
            )
            self.logger.info(
                "GLPI user '%s' created (root entity, Self-Service profile)" % login
            )
            return True
        except Exception as e:
            self.logger.exception(e)
            return False
        finally:
            try:
                client.kill_session()
            except Exception:
                pass

    def doProvisioning(self, authtoken):
        """
        @return: Deferred resulting to authtoken
        """
        # Ensure the user exists in GLPI (REST API), off the reactor thread
        d = threads.deferToThread(self._ensure_glpi_user, authtoken)
        # get GLPI user profile, and sync it
        d.addCallback(self._cbProvisioning, authtoken)
        return d
