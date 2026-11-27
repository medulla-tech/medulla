# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Plugin to manage the interface with Kiosk
"""
import base64
import logging
import re
import subprocess
import tempfile
import threading

from mmc.core.version import getMedullaVersion as getVersion, getMedullaRevision as getRevision

from mmc.support.config import PluginConfigFactory
from mmc.plugins.kiosk.config import KioskConfig
from mmc.plugins.kiosk.TreeOU import TreeOU
from mmc.plugins.base.config import BasePluginConfig
from mmc.plugins.xmppmaster.master.lib.utils import name_random

from mmc.support.mmctools import (
    RpcProxyI,
    ContextMakerI,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_optional_xmpp_context,
                              user_entity_scope,
                              check_user_entity,
                              log_entity_refusal)
# Database
from pulse2.database.kiosk import KioskDatabase, PROFILE_SOURCES
from pulse2.database.kiosk.schema import Profiles
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.pkgs import PkgsDatabase
from mmc.plugins.glpi.database import Glpi
from pulse2.utils import normalize_entity

VERSION = "1.0.0"
APIVERSION = "4:1:3"

LDAP_SECTION = "authentication_externalldap"
OU_SOURCES = ("ou_user", "ou_machine")

logger = logging.getLogger()


# The XML-RPC dispatcher serves every callable of this module, whatever its
# name and without a session: the helpers live in RpcProxy, which refuses the
# names starting with an underscore.


def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    config = KioskConfig("kiosk")

    if config.disable:
        logger.warning("Plugin kiosk: disabled by configuration.")
        return False

    if not KioskDatabase().activate(config):
        logger.error(
            "Plugin kiosk: an error occurred during the database initialization"
        )
        return False
    return True


def activate_2():
    """Once every plugin is loaded: gives an entity to the profiles without one."""
    try:
        left = KioskDatabase().adopt_profiles(RpcProxy._owner_entities)
        if left:
            logger.warning(f"Plugin kiosk: {left} profile(s) without entity")
    except Exception as e:
        logger.error(f"Plugin kiosk: profiles not given an entity: {e}")
    return True


class ContextMaker(ContextMakerI):
    def getContext(self):
        """EnhancedSecurityContext of the current user, request and session."""
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s


class RpcProxy(RpcProxyI):
    def getFunction(self, funcname):
        # The helpers trust their arguments: only the public methods are callable
        if funcname.startswith("_"):
            raise AttributeError(funcname)
        return RpcProxyI.getFunction(self, funcname)

    ##
    # helpers
    ##

    @staticmethod
    def _login(ctx):
        if ctx is None:
            return None
        return (ctx.get_session_info() or {}).get("userid") or getattr(ctx, "userid", None)

    @staticmethod
    def _allowed_entity(ctx, action, entity_id):
        """GLPI id of the entity when the user has it, else None."""
        entity = None if isinstance(entity_id, bool) else normalize_entity(entity_id, defaut=None)
        if entity is None or entity < 0 or not check_user_entity(ctx, entity):
            log_entity_refusal(ctx, action, entity_id)
            return None
        return entity

    @staticmethod
    def _allowed_profiles(ctx, ids):
        """{profile id: entity id} of the existing profiles of ids the user has;
        a profile without entity belongs to the unrestricted users only."""
        wanted = []
        for profile_id in ids if isinstance(ids, (list, tuple)) else [ids]:
            try:
                wanted.append(int(profile_id))
            except (TypeError, ValueError):
                continue
        return {
            profile_id: entity_id
            for profile_id, entity_id in KioskDatabase().get_profile_entities(wanted).items()
            if check_user_entity(ctx, entity_id)
        }

    @staticmethod
    def _owner_entities(login):
        """GLPI ids of the entities of a user, [] when they cannot be read."""
        try:
            return [int(location.id) for location in Glpi().getUserLocations(login) or []]
        except Exception as e:
            logger.warning(f"kiosk: entities of {login!r} not read: {e}")
            return []

    @staticmethod
    def _visible_packages(login):
        """uuids of the packages the user sees."""
        sharing = PkgsDatabase().pkgs_search_share({"login": login})
        packages = PkgsDatabase().get_all_packages(
            login, sharing["config"]["centralizedmultiplesharing"]
        )
        return set(packages["datas"]["uuid"])

    @staticmethod
    def _notify_substitute(action, entity_ids):
        """Tells the master substitute that the profiles of these GLPI entities
        changed; it computes and pushes the packages of the machines."""
        entity_ids = sorted({int(entity_id) for entity_id in entity_ids if entity_id is not None})
        if not entity_ids:
            return
        data = {
            "subaction": "profiles_changed",
            "entity_ids": entity_ids,
            "sessionid": name_random(8, "kiosk_"),
        }

        def send():
            try:
                # Imported here: at module level it would be callable by XML-RPC
                from mmc.plugins.xmppmaster.master.agentmaster import callXmppPlugin
                callXmppPlugin("kiosk", data)
            except Exception as e:
                logger.warning(f"{action}: substitute not notified ({data}): {e}")

        threading.Thread(target=send, daemon=True).start()

    @staticmethod
    def _ldapsearch(base, ldap_filter):
        """DNs of the entries of the external directory under base, [] when it
        is not configured or does not answer."""
        config = PluginConfigFactory.new(BasePluginConfig, "base")
        if not config.has_section(LDAP_SECTION):
            return []
        try:
            with tempfile.NamedTemporaryFile("w") as secret:
                secret.write(config.get(LDAP_SECTION, "bindpasswd"))
                secret.flush()
                result = subprocess.run(
                    ["ldapsearch", "-o", "ldif-wrap=no",
                     "-H", config.get(LDAP_SECTION, "ldapurl"),
                     "-x", "-b", base,
                     "-D", config.get(LDAP_SECTION, "bindname"),
                     "-y", secret.name,
                     "-LLL", ldap_filter, "dn"],
                    capture_output=True, text=True, timeout=60, check=False,
                )
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning(f"kiosk: ldapsearch failed: {e}")
            return []
        if result.returncode != 0:
            logger.warning(f"kiosk: ldapsearch failed: {result.stderr.strip()}")
            return []
        dns = []
        for line in result.stdout.splitlines():
            if line.startswith("dn:: "):
                dns.append(base64.b64decode(line[len("dn:: "):]).decode("utf-8", "replace"))
            elif line.startswith("dn: "):
                dns.append(line[len("dn: "):])
        return dns

    @classmethod
    def _ldap_ous(cls):
        config = PluginConfigFactory.new(BasePluginConfig, "base")
        if not config.has_section(LDAP_SECTION):
            return []
        ous = []
        for dn in cls._ldapsearch(config.get(LDAP_SECTION, "suffix_ou"),
                                  "(objectClass=organizationalUnit)"):
            ou = dn.replace(",OU=", " < ").replace("OU=", "")
            ou = re.sub(",DC=(.+)", "", ou).split(" < ")
            ou.reverse()
            ous.append(">>".join(ou))
        return ous

    @staticmethod
    def _ou_list(ous):
        if isinstance(ous, str):
            ous = [ous]
        return [str(ou) for ou in ous or [] if ou]

    @staticmethod
    def _ou_parents(ou):
        """OUs above an OU: A and A/B for A/B/C."""
        parts = ou.split("/")
        return ["/".join(parts[:depth]) for depth in range(1, len(parts))]

    @classmethod
    def _source_values(cls, source, entity):
        """Values a profile of this source may take in the entity."""
        if source == "ldap":
            return cls._ldap_ous()
        return XmppMasterDatabase().get_ou_list_from_machines(source, [entity])

    def _checked_profile(self, ctx, action, entity, name, source, ous, packages, profile_id=None):
        """(name, source, ous, packages, visible packages) ready to be stored,
        None when the profile is refused."""
        name = str(name).strip()
        source = str(source).lower()
        if not name or len(name) > Profiles.name.type.length or source not in PROFILE_SOURCES:
            logger.warning(f"{action}: name {name!r} or source {source!r} refused")
            return None
        if KioskDatabase().profile_name_exists(name, entity, exclude_id=profile_id):
            logger.warning(f"{action}: name {name!r} already used in entity {entity}")
            return None

        ous = self._ou_list(ous)
        if source == "entity":
            ous = []
        elif source in XmppMasterDatabase.MACHINE_OU_SOURCES:
            known = set(self._source_values(source, entity))
            if source in OU_SOURCES:
                for value in list(known):
                    known.update(self._ou_parents(value))
            if profile_id is not None:
                stored = KioskDatabase().get_profile_by_id(profile_id) or {}
                if stored.get("source") == source and stored.get("entity_id") == entity:
                    known.update(stored["ous"])
            refused = [ou for ou in ous if ou not in known]
            if refused or not ous:
                logger.warning(f"{action}: {source} {refused or ous} refused in entity {entity} "
                               f"for user {self._login(ctx)!r}")
                return None

        if isinstance(packages, dict):
            packages = list(packages.values())
        uuids = [package.get("uuid") if isinstance(package, dict) else package
                 for package in packages or []]
        visible = self._visible_packages(self._login(ctx))
        return name, source, ous, [uuid for uuid in uuids if uuid in visible], visible

    @staticmethod
    def _active(active):
        if isinstance(active, str):
            return 1 if active.strip().lower() in ("1", "true", "active") else 0
        return 1 if active else 0

    ##
    # profiles
    ##

    @with_optional_xmpp_context
    def get_profiles_list(self, entity="", start=0, limit=-1, filter="", ctx=None):
        """Profiles of the entity ("UUIDn" or n), of every entity of the user
        when it is "" or -1: {"total": n, "datas": [{"id", "name", "entity_id",
        "source", "active", "creation_date", "owner"}]}."""
        return KioskDatabase().get_profiles_list(
            user_entity_scope(ctx, entity), start, limit, filter
        )

    @with_optional_xmpp_context
    def get_profile_by_id(self, id, ctx=None):
        """The profile with "ous": [str] and "packages": [{"uuid", "name"}], the
        packages the user sees only; False when it does not exist or is out of
        the entities of the user."""
        allowed = self._allowed_profiles(ctx, [id])
        if not allowed:
            return False
        profile = KioskDatabase().get_profile_by_id(next(iter(allowed)))
        if profile is None:
            return False
        visible = self._visible_packages(self._login(ctx))
        profile["packages"] = [package for package in profile["packages"]
                               if package["uuid"] in visible]
        return profile

    @with_optional_xmpp_context
    def create_profile(self, name, entity_id, source, ous, active, packages, ctx=None):
        """Returns the id of the new profile, False when it is refused.

        ous: values of the source, ignored for "entity". packages: uuids."""
        action = "kiosk.create_profile"
        entity = self._allowed_entity(ctx, action, entity_id)
        if entity is None:
            return False
        checked = self._checked_profile(ctx, action, entity, name, source, ous, packages)
        if checked is None:
            return False
        name, source, ous, packages, _ = checked
        profile_id = KioskDatabase().create_profile(
            name, entity, source, ous, self._active(active), packages, self._login(ctx)
        )
        if profile_id is False:
            return False
        self._notify_substitute(action, [entity])
        return profile_id

    @with_optional_xmpp_context
    def update_profile(self, id, name, entity_id, source, ous, active, packages, ctx=None):
        """Returns True when the profile is updated. The packages the user does
        not see stay as they are."""
        action = "kiosk.update_profile"
        allowed = self._allowed_profiles(ctx, [id])
        if not allowed:
            return False
        profile_id, previous_entity = next(iter(allowed.items()))
        entity = self._allowed_entity(ctx, action, entity_id)
        if entity is None:
            return False
        checked = self._checked_profile(ctx, action, entity, name, source, ous, packages,
                                        profile_id)
        if checked is None:
            return False
        name, source, ous, packages, visible = checked
        if not KioskDatabase().update_profile(
            profile_id, name, entity, source, ous, self._active(active), packages, visible
        ):
            return False
        self._notify_substitute(action, [previous_entity, entity])
        return True

    @with_optional_xmpp_context
    def delete_profiles(self, ids, ctx=None):
        """Returns the ids of the profiles actually deleted."""
        allowed = self._allowed_profiles(ctx, ids)
        deleted = KioskDatabase().delete_profiles(list(allowed))
        self._notify_substitute("kiosk.delete_profiles",
                                [allowed[profile_id] for profile_id in deleted])
        return deleted

    ##
    # sources
    ##

    @with_optional_xmpp_context
    def get_ou_list(self, source, entity_id, ctx=None):
        """Tree (TreeOU.recursive_json) of the values of a source in the entity
        and its sub-entities; [] when the entity is refused. The source
        "entity" has no value."""
        source = str(source).lower()
        if source == "entity" or source not in PROFILE_SOURCES:
            return []
        entity = self._allowed_entity(ctx, "kiosk.get_ou_list", entity_id)
        if entity is None:
            return []
        tree = TreeOU()
        if source in OU_SOURCES:
            for value in self._source_values(source, entity):
                tree.create_recursively(value, separator="/")
            return tree.recursive_json("/")
        for value in self._source_values(source, entity):
            tree.create_recursively(value)
        return tree.recursive_json()

    @with_optional_xmpp_context
    def count_machines_of_ous(self, source, ous, entity_id, ctx=None):
        """Number of machines of the entity and of its sub-entities a profile
        restricted to these OUs (A/B/C) applies to; 0 when the entity is
        refused or the source is not an OU."""
        source = str(source).lower()
        if source not in OU_SOURCES:
            return 0
        entity = self._allowed_entity(ctx, "kiosk.count_machines_of_ous", entity_id)
        if entity is None:
            return 0
        ous = set(self._ou_list(ous))
        ous = sorted(ou for ou in ous if ous.isdisjoint(self._ou_parents(ou)))
        return XmppMasterDatabase().count_machines_in_ous(source, ous, [entity])

    @with_optional_xmpp_context
    def get_conf_kiosk(self, ctx=None):
        return {"use_external_ldap": KioskConfig("kiosk").use_external_ldap}
