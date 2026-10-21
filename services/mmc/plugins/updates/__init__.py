# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/mmc/plugins/updates/__init__.py

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.support.mmctools import (
    RpcProxyI,
    ContextMakerI,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_optional_xmpp_context,
                              user_entity_ids,
                              user_entity_scope,
                              check_user_entity,
                              log_entity_refusal)

from mmc.plugins.updates.config import UpdatesConfig

# import pour la database
from pulse2.database.updates import UpdatesDatabase, WINDOWS_UPDATE_DEPLOY_TITLE

from pulse2.database.xmppmaster import XmppMasterDatabase

from pulse2.database.pkgs import PkgsDatabase
from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.msc.database import MscDatabase
from pulse2.utils import normalize_entity

from mmc.plugins.xmppmaster import callrestart
from mmc.plugins.xmppmaster.master.agentmaster import send_message_json
from mmc.plugins.xmppmaster.master.lib.utils import name_random

import logging
import re
import traceback
from datetime import datetime, timedelta

VERSION = "1.0.0"
APIVERSION = "1:0:0"

UPDATES_SUBSTITUTE_JID = "master_upd@pulse"
# Same title as the automatic deployments of the substitute
LINUX_UPDATE_DEPLOY_TITLE = "Linux updates"
WINDOWS_UPDATE_DEPLOY_HOURS = 24
# machine_upgrades.run_error
UPGRADE_RUN_ERROR_LENGTH = 255
# machine_reports.os
UPGRADE_SYSTEMS = ("windows", "linux")

# Upgrade categories shown to the admin, in list order (to act on first)
UPGRADE_CATEGORIES = ("ready", "in_progress", "reboot_pending", "not_eligible", "no_report",
                      "undetermined", "up_to_date", "not_concerned")


def _reboot_pending(machine):
    """Same count as the reboot_pending of get_windows_summary."""
    return machine["evaluated"] and machine["reboot_pending"]


def _history_title(title):
    """Deployment title without its filing marker: « label -@upd@- date », or
    « hostname--@upd@--label » for the deployments of the former engine."""
    title = title or ""
    if " -@upd@- " in title:
        return title.split(" -@upd@- ")[0].strip()
    if "--@upd@--" in title:
        return title.split("--@upd@--", 1)[1].strip()
    return title.strip()


def _during_deployment(date, spans):
    """True when date ("YYYY-MM-DD HH:MM:SS") is inside one of the (start, end)
    spans of deployments."""
    return any(start <= str(date) <= end for start, end in spans)


def _upgrade_category(machine):
    """Category of a get_upgrade_machines row."""
    if machine["launched_at"]:
        if not machine["step_running"] and _reboot_pending(machine):
            return "reboot_pending"
        return "in_progress"
    # A stopped upgrade is still to do: the cause is in its deployments
    state = machine["state"] or "no_report"
    if state in ("ready", "up_to_date") and _reboot_pending(machine):
        return "reboot_pending"
    return state if state in UPGRADE_CATEGORIES else "undetermined"


def _deploy_refusal(machine, pending):
    """Why the machine cannot receive a deployment now, None when it can.
    pending: glpi uuids with a command of the package waiting."""
    if machine.get("offer") == "esu":
        return "esu_required"
    if machine.get("offer") and not machine["approved"]:
        return "not_approved"
    if not machine["known"]:
        return "unknown_machine"
    if machine["deploying"] or machine["glpi_uuid"] in pending:
        return "already_deploying"
    if machine["awaiting_report"] or machine.get("deployed_pending_report"):
        return "awaiting_report"
    if machine["running"]:
        return "deployment_running"
    if machine.get("upgrading"):
        return "upgrade_running"
    if machine.get("release_to_resume"):
        return "upgrade_to_resume"
    # The precheck of a KB package stops on it (code 20); offer is empty for an
    # uninstallation and for Linux
    if machine.get("offer") and machine.get("reboot_pending"):
        return "reboot_pending"
    return None


logger = logging.getLogger()


def _read_failed(action, error, empty=None):
    """Answer of a read that intercepted an exception: its empty form plus "error": True."""
    logger.error(f"{action}: {error}")
    logger.error(traceback.format_exc())
    return dict(empty or {}, error=True)


def _sizes_for_xmlrpc(rows):
    """XML-RPC integers stop at 2^31-1, under the size of a cumulative update: the
    agent would answer a fault for the whole list. Sizes travel as decimal strings."""
    for row in rows:
        if row.get("size") is not None:
            row["size"] = str(row["size"])
    return rows


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UpdatesConfig("updates")

    if config.disable:
        logger.warning("Plugin updates: disabled by configuration.")
        return False

    if not UpdatesDatabase().activate(config):
        logger.error(
            "Plugin updates: an error occurred during the database initialization"
        )
        return False
    return True


class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s


class RpcProxy(RpcProxyI):
    ##
    # machines
    ##

    @staticmethod
    def _dashboard_scope(location, ctx):
        """Entites demandees restreintes a celles de l'utilisateur ; vide = toutes les siennes."""
        scope = user_entity_scope(ctx, location)
        if scope is None:
            # Non restreint (root) : les entites de sa session.
            session_entities = (ctx.get_session_info().get('mondict') or {}).get('liste_entities_user')
            scope = user_entity_scope(None, session_entities) if session_entities else []
        return scope

    @with_optional_xmpp_context
    def get_upgrade_summary(self, location=None, system="windows", ctx=None):
        """Upgrade counters of the visible machines of the system: {"total",
        "categories": {key: n}, "reboot_pending": machines waiting for a restart,
        upgrade or not}."""
        try:
            entity_ids = self._dashboard_scope(location, ctx)
            machines = UpdatesDatabase().get_upgrade_machines(
                entity_ids, self._system(system)) if entity_ids else []
            counts = {key: 0 for key in UPGRADE_CATEGORIES}
            for machine in machines:
                counts[_upgrade_category(machine)] += 1
            return {"total": len(machines), "categories": counts,
                    "reboot_pending": sum(1 for machine in machines if _reboot_pending(machine))}
        except Exception as e:
            return _read_failed("get_upgrade_summary", e, {
                "total": 0, "categories": {key: 0 for key in UPGRADE_CATEGORIES},
                "reboot_pending": 0})

    @with_optional_xmpp_context
    def get_upgrade_machine_list(self, location=None, start=0, limit=-1, filter="",
                                 only="", system="windows", ctx=None):
        """Visible machines of the system with their upgrade; only = one category of
        UPGRADE_CATEGORIES or "reboot_pending". "last_deployment": fields of the log
        page of its latest upgrade deployment, absent when it never had one."""
        try:
            entity_ids = self._dashboard_scope(location, ctx)
            machines = UpdatesDatabase().get_upgrade_machines(
                entity_ids, self._system(system)) if entity_ids else []
            needle = str(filter or "").strip().lower()
            rows = []
            for machine in machines:
                machine["category"] = _upgrade_category(machine)
                if only == "reboot_pending":
                    if not _reboot_pending(machine):
                        continue
                elif only and machine["category"] != only:
                    continue
                if needle and needle not in machine["hostname"].lower():
                    continue
                rows.append(machine)
            rows.sort(key=lambda m: (UPGRADE_CATEGORIES.index(m["category"]), m["hostname"].lower()))
            start, limit = int(start or 0), int(limit if limit is not None else -1)
            page = rows[start:] if limit < 0 else rows[start:start + limit]
            deployments = UpdatesDatabase().get_last_upgrade_deployments(
                [machine["glpi_uuid"] for machine in page])
            for machine in page:
                deployment = deployments.get(machine["glpi_uuid"])
                if deployment:
                    machine["last_deployment"] = dict(deployment,
                                                      machine_name=machine["hostname"])
            return {"total": len(rows), "rows": page}
        except Exception as e:
            return _read_failed("get_upgrade_machine_list", e, {"total": 0, "rows": []})

    @with_optional_xmpp_context
    def launch_upgrades(self, entity_id, glpi_uuids, ctx=None):
        """Launch the upgrade of the ready machines among glpi_uuids of the entity.
        Returns {"launched": n}, plus "error" when refused."""
        try:
            entity = self._writable_entity(ctx, "launch_upgrades", entity_id)
            if entity is None:
                return {"launched": 0, "error": "entity_refused"}
            entity_ids = self._dashboard_scope([entity], ctx)
            login = self._ctx_login(ctx) or "root"
            launched = UpdatesDatabase().launch_upgrades(entity_ids, list(glpi_uuids or []), login)
        except Exception as e:
            logger.error(f"launch_upgrades: {e}")
            logger.error(traceback.format_exc())
            return {"launched": 0, "error": "internal_error"}
        logger.info(f"launch_upgrades: {launched} machine(s) of entity {entity} by {login}")
        if launched:
            self._notify_substitute("launch_upgrades", {"upgrades_launched": entity})
        return {"launched": launched}

    @with_optional_xmpp_context
    def cancel_upgrade(self, jid, ctx=None):
        """Abandon the launched upgrade of the machine jid. Returns {"error": ""}, or
        "not_launched", "step_running", "reboot_pending" (Windows: the prepared upgrade
        applies at the next restart anyway), "forbidden", "internal_error"."""
        try:
            jid = str(jid or "").strip()
            database = UpdatesDatabase()
            upgrade = database.get_upgrade_to_cancel(jid)
            if upgrade is None:
                logger.warning(f"cancel_upgrade: machine {jid!r} refused "
                               f"for user {self._ctx_login(ctx)!r}")
                return {"error": "forbidden"}
            if self._writable_entity(ctx, "cancel_upgrade", upgrade["entity_id"]) is None:
                return {"error": "forbidden"}
            if not upgrade["launched_at"]:
                return {"error": "not_launched"}
            if upgrade["step_running"]:
                return {"error": "step_running"}
            if upgrade["os"] == "windows" and _upgrade_category(upgrade) == "reboot_pending":
                return {"error": "reboot_pending"}
            login = self._ctx_login(ctx) or "root"
            if upgrade["os"] == "linux":
                # "release:" holds the machine for the resumption, once its sources may have changed
                step = "release" if upgrade["release_started"] else None
            else:
                step = upgrade["steps"][0] if upgrade["steps"] else "upgrade"
            error = f"{step}: abandoned by {login}"[:UPGRADE_RUN_ERROR_LENGTH] if step else None
            if not database.cancel_upgrade(jid, error):
                return {"error": "not_launched"}
        except Exception as e:
            logger.error(f"cancel_upgrade: {e}")
            logger.error(traceback.format_exc())
            return {"error": "internal_error"}
        logger.info(f"cancel_upgrade: {jid} by {login}")
        return {"error": ""}

    @with_optional_xmpp_context
    def restart_machine(self, jid, ctx=None):
        """Restart the machine jid waiting for a restart, as the quick action of
        xmppmaster. Returns {"sent": bool, "reason": ""}, reason when not sent:
        "not_found", "forbidden", "not_waiting", "offline", "already_requested",
        "send_failed", "internal_error"."""
        try:
            jid = str(jid or "").strip()
            database = UpdatesDatabase()
            machine = database.get_windows_machine(jid) if jid else None
            if machine is None:
                return {"sent": False, "reason": "not_found"}
            if self._writable_entity(ctx, "restart_machine", machine["entity_id"]) is None:
                return {"sent": False, "reason": "forbidden"}
            if not machine["reboot_pending"] or machine["running"]:
                return {"sent": False, "reason": "not_waiting"}
            if not machine["online"]:
                return {"sent": False, "reason": "offline"}
            if machine["restart_requested"]:
                return {"sent": False, "reason": "already_requested"}
            login = self._ctx_login(ctx) or "root"
            try:
                sent = callrestart(jid, True) == jid
            except Exception as e:
                logger.error(f"restart_machine: {jid}: {e}")
                sent = False
            if not sent:
                return {"sent": False, "reason": "send_failed"}
            name = machine["hostname"] or jid
            XmppMasterDatabase().setlogxmpp(
                f'QA : [user "{login}"] ask a Reboot to [ machine : "{name}"][jid : "{jid}"]',
                "QA", "", 0, name, "Manuel", "", "QuickAction | Reboot sent", "", "",
                f"session user {login}")
            database.set_restart_requested(jid)
        except Exception as e:
            logger.error(f"restart_machine: {e}")
            logger.error(traceback.format_exc())
            return {"sent": False, "reason": "internal_error"}
        logger.info(f"restart_machine: {jid} by {login}")
        return {"sent": True, "reason": ""}

    def _group_upgrades(self, gid, ctx, systems):
        """(machines of the group with their upgrade, of the given systems; writable
        entity ids; machines of another system), None when the group is refused."""
        uuids = self._group_uuids("group upgrade", gid, ctx)
        if uuids is None:
            return None
        entity_ids = [entity for entity in self._dashboard_scope([], ctx)
                      if check_user_entity(ctx, entity)]
        members = set(uuids)
        allowed = {system for system in systems or [] if system in UPGRADE_SYSTEMS}
        machines = [machine for machine in UpdatesDatabase().get_upgrade_machines(entity_ids, None)
                    if machine["glpi_uuid"] in members] if entity_ids else []
        kept = [machine for machine in machines if machine["os"] in allowed]
        for machine in kept:
            machine["category"] = _upgrade_category(machine)
        return kept, entity_ids, len(machines) - len(kept)

    @with_optional_xmpp_context
    def get_upgrade_group_preview(self, gid, systems=None, ctx=None):
        """What « upgrade this group » would do on the given systems (those the caller
        may upgrade, none by default): {"launch": n machines ready, "targets": {release: n},
        "skipped": {category: n}, "system_refused": n machines of another system},
        plus "error"."""
        try:
            group = self._group_upgrades(gid, ctx, systems)
            if group is None:
                return {"launch": 0, "targets": {}, "skipped": {}, "system_refused": 0,
                        "error": "unknown_group"}
            result = {"launch": 0, "targets": {}, "skipped": {}, "system_refused": group[2]}
            for machine in group[0]:
                if machine["category"] == "ready":
                    result["launch"] += 1
                    target = machine["target_release"]
                    result["targets"][target] = result["targets"].get(target, 0) + 1
                else:
                    category = machine["category"]
                    result["skipped"][category] = result["skipped"].get(category, 0) + 1
            return result
        except Exception as e:
            logger.error(f"get_upgrade_group_preview: {e}")
            logger.error(traceback.format_exc())
            return {"launch": 0, "targets": {}, "skipped": {}, "system_refused": 0,
                    "error": "internal_error"}

    @with_optional_xmpp_context
    def launch_upgrade_group(self, gid, systems=None, ctx=None):
        """Launch the upgrade of the group machines that are ready, on the given systems
        (those the caller may upgrade, none by default).
        Returns {"launched": n}, plus "error" when refused."""
        try:
            group = self._group_upgrades(gid, ctx, systems)
            if group is None:
                return {"launched": 0, "error": "unknown_group"}
            machines, entity_ids, _ = group
            uuids = [m["glpi_uuid"] for m in machines if m["category"] == "ready"]
            login = self._ctx_login(ctx) or "root"
            launched = UpdatesDatabase().launch_upgrades(entity_ids, uuids, login) if uuids else 0
        except Exception as e:
            logger.error(f"launch_upgrade_group: {e}")
            logger.error(traceback.format_exc())
            return {"launched": 0, "error": "internal_error"}
        logger.info(f"launch_upgrade_group: {launched} machine(s) of group {gid} by {login}")
        if launched:
            # The substitute only checks an entity id and runs every launched upgrade
            self._notify_substitute("launch_upgrades", {"upgrades_launched": int(entity_ids[0])})
        return {"launched": launched}

    @with_optional_xmpp_context
    def get_windows_summary(self, location=None, system="windows", distribution="", ctx=None):
        """system: "windows" or "linux"; distribution: one Linux distribution, empty for all."""
        try:
            return UpdatesDatabase().get_windows_summary(self._dashboard_scope(location, ctx),
                                                         self._system(system),
                                                         str(distribution or ""))
        except Exception as e:
            return _read_failed("get_windows_summary", e)

    @staticmethod
    def _system(system):
        return "linux" if system == "linux" else "windows"

    @with_optional_xmpp_context
    def get_linux_distributions(self, location=None, ctx=None):
        """Linux distributions reported in the visible entities, one tab each."""
        try:
            entity_ids = self._dashboard_scope(location, ctx)
            return UpdatesDatabase().get_linux_distributions(entity_ids) if entity_ids else []
        except Exception as e:
            return _read_failed("get_linux_distributions", e)

    @with_optional_xmpp_context
    def get_windows_entities(self, ctx=None):
        try:
            return UpdatesDatabase().get_windows_entities(self._dashboard_scope([], ctx))
        except Exception as e:
            return _read_failed("get_windows_entities", e, {"rows": []})

    @with_optional_xmpp_context
    def get_windows_machines(self, location=None, start=0, limit=-1, filter="", system="windows",
                             distribution="", only="", ctx=None):
        """Machines of the visible entities of location (all of them when empty):
        system "windows" or "linux", of one Linux distribution when given, of one
        status card when only is given ("to_update", "critical", "reboot_pending")."""
        try:
            entity_ids = self._dashboard_scope(location, ctx)
            if not entity_ids:
                if location:
                    log_entity_refusal(ctx, "get_windows_machines", location)
                return {"total": 0, "rows": []}
            return UpdatesDatabase().get_windows_machines(entity_ids, start, limit, filter,
                                                          self._system(system),
                                                          str(distribution or ""),
                                                          str(only or ""))
        except Exception as e:
            return _read_failed("get_windows_machines", e, {"total": 0, "rows": []})

    @with_optional_xmpp_context
    def get_windows_machine(self, jid, ctx=None):
        try:
            machine = UpdatesDatabase().get_windows_machine(jid)
            if machine is None:
                return None
            if not self._dashboard_scope([machine["entity_id"]], ctx):
                log_entity_refusal(ctx, "get_windows_machine", machine["entity_id"])
                return None
            _sizes_for_xmlrpc(machine["updates"])
            return machine
        except Exception as e:
            return _read_failed("get_windows_machine", e)

    @with_optional_xmpp_context
    def get_windows_machine_history(self, jid, start=0, limit=-1, ctx=None):
        """Update history of a visible machine, latest first: Medulla deployments
        (session « update », source "medulla", with the deploy fields the deployment
        log page needs) and the updates the machine reports as installed (source
        "machine") that no successful Medulla deployment already shows.
        {"total", "rows": [{"source", "title", "kb", "date", "state", ...}]}; a failed
        Windows deployment of the page with a known cause also has "failure": "disk_full"."""
        empty = {"total": 0, "rows": []}
        try:
            database = UpdatesDatabase()
            machine = database.get_windows_machine(jid)
            if machine is None:
                return empty
            if not self._dashboard_scope([machine["entity_id"]], ctx):
                log_entity_refusal(ctx, "get_windows_machine_history", machine["entity_id"])
                return empty
            rows = []
            xmpp_machine = XmppMasterDatabase().getMachinefromjid(jid)
            if xmpp_machine:
                history = XmppMasterDatabase().get_audit_summary_updates_by_machine(
                    xmpp_machine["id"], 0, -1, "")
                for deploy in history["datas"]:
                    title = _history_title(deploy["title"])
                    kb = re.search(r"KB(\d+)", title)
                    rows.append(dict(deploy, source="medulla", title=title,
                                     kb=kb.group(1) if kb else "",
                                     date=deploy["start"] or ""))
            shown = {row["kb"] for row in rows
                     if row["kb"] and "SUCCESS" in (row["state"] or "")}
            # A Linux transaction run by a successful deployment is already its row
            ends = database.get_deployment_ends(
                [row["sessionid"] for row in rows
                 if not row["kb"] and "SUCCESS" in (row["state"] or "")])
            deployed = [(str(row["date"]), ends[row["sessionid"]]) for row in rows
                        if row.get("sessionid") in ends]
            for item in database.get_windows_installed(jid):
                if item["kb"] in shown or (not item["kb"] and _during_deployment(
                        item["date"], deployed)):
                    continue
                rows.append({"source": "machine", "kb": item["kb"], "date": item["date"],
                             "title": item["title"] or "KB%s" % item["kb"], "state": ""})
            rows.sort(key=lambda row: str(row["date"]), reverse=True)
            removable = database.get_windows_removable_kbs(jid)
            for row in rows:
                row["removable"] = row["reinstalled"] = False
                if row["kb"] and int(row["kb"]) in removable and (
                        row["source"] == "machine" or "SUCCESS" in (row["state"] or "")):
                    # Only the latest line of a KB carries the action
                    row["removable"] = row["state"] != "UNINSTALL SUCCESS"
                    row["reinstalled"] = removable.pop(int(row["kb"]))
            start, limit = int(start or 0), int(limit if limit is not None else -1)
            page = rows[start:] if limit < 0 else rows[start:start + limit]
            if machine["os"] == "windows":
                failures = database.get_deployment_failures(
                    [row["sessionid"] for row in page
                     if (row["state"] or "").startswith(("ABORT", "ERROR"))])
                for row in page:
                    if row.get("sessionid") in failures:
                        row["failure"] = failures[row["sessionid"]]
            return {"total": len(rows), "rows": page}
        except Exception as e:
            return _read_failed("get_windows_machine_history", e, empty)

    def _read_tracking(self, action, entity_id, ctx, read):
        """read(entity) when the user sees the entity, else the empty answer."""
        empty = {"rows": [], "inherited_from": None, "parent": None}
        try:
            entity_ids = self._dashboard_scope([entity_id], ctx)
            if not entity_ids:
                log_entity_refusal(ctx, action, entity_id)
                return empty
            return read(entity_ids[0])
        except Exception as e:
            return _read_failed(action, e, empty)

    def _write_tracking(self, action, entity_id, ctx, check, write):
        """write(entity) when check accepts the entity, then the substitute recomputes."""
        try:
            entity = check(ctx, action, entity_id)
            if entity is None:
                return False
            if not write(entity):
                return False
        except Exception as e:
            logger.error(f"{action}: {e}")
            logger.error(traceback.format_exc())
            return False
        self._notify_substitute(action, {"tracking_changed": entity})
        return True

    @with_optional_xmpp_context
    def get_windows_products(self, entity_id, ctx=None):
        return self._read_tracking("get_windows_products", entity_id, ctx,
                                   UpdatesDatabase().get_windows_products)

    @with_optional_xmpp_context
    def set_windows_products(self, entity_id, selections, ctx=None):
        return self._write_tracking(
            "set_windows_products", entity_id, ctx, self._settable_entity,
            lambda entity: UpdatesDatabase().set_windows_products(entity, selections or []))

    @with_optional_xmpp_context
    def reset_windows_products(self, entity_id, ctx=None):
        """The entity takes its parent's products again; refused for the root."""
        return self._write_tracking("reset_windows_products", entity_id, ctx, self._writable_entity,
                                    UpdatesDatabase().reset_windows_products)

    @with_optional_xmpp_context
    def get_linux_releases(self, entity_id, ctx=None):
        """Linux versions reported by the machines the user sees at or below the entity:
        {"rows": [{"distribution", "release", "codename", "tracked", "machines"}],
        "inherited_from", "parent"}."""
        return self._read_tracking(
            "get_linux_releases", entity_id, ctx,
            lambda entity: UpdatesDatabase().get_linux_releases(entity, user_entity_ids(ctx)))

    @with_optional_xmpp_context
    def set_linux_releases(self, entity_id, selections, ctx=None):
        """selections: [{"distribution", "release"}], among those get_linux_releases offers."""
        return self._write_tracking(
            "set_linux_releases", entity_id, ctx, self._settable_entity,
            lambda entity: UpdatesDatabase().set_linux_releases(entity, selections or [],
                                                                user_entity_ids(ctx)))

    @with_optional_xmpp_context
    def reset_linux_releases(self, entity_id, ctx=None):
        """The entity takes its parent's Linux versions again; refused for the root."""
        return self._write_tracking("reset_linux_releases", entity_id, ctx, self._writable_entity,
                                    UpdatesDatabase().reset_linux_releases)

    @staticmethod
    def _notify_substitute(action, data):
        try:
            send_message_json(UPDATES_SUBSTITUTE_JID, {
                "action": "updates",
                "sessionid": name_random(8, "updates_"),
                "data": data,
                "ret": 0,
                "base64": False,
            })
        except Exception as e:
            logger.warning(f"{action}: substitute not notified ({data}): {e}")

    @staticmethod
    def _ctx_login(ctx):
        if ctx is None:
            return None
        return (ctx.get_session_info() or {}).get("userid") or getattr(ctx, "userid", None)

    @staticmethod
    def _writable_entity(ctx, action, entity_id):
        entity = None if isinstance(entity_id, bool) else normalize_entity(entity_id, defaut=None)
        if entity is None or not check_user_entity(ctx, entity):
            log_entity_refusal(ctx, action, entity_id)
            return None
        return entity

    def _settable_entity(self, ctx, action, entity_id):
        """Writable entity whose settings may change. SaaS: never the root, every
        client would inherit them."""
        entity = self._writable_entity(ctx, action, entity_id)
        if entity is None:
            return None
        # Local import, as mmc.plugins.glpi.provisioning: plugins import one another
        from mmc.plugins.admin import _get_install_type
        if _get_install_type() == "saas" and UpdatesDatabase().is_root_entity(entity):
            logger.warning(f"{action}: root entity refused on a SaaS installation "
                           f"for user {self._ctx_login(ctx)!r}")
            return None
        return entity

    @with_optional_xmpp_context
    def get_windows_approvals(self, entity_id, status="pending", start=0, limit=-1,
                              filter="", system="windows", ctx=None):
        empty = {"total": 0, "rows": [],
                 "counts": {"pending": 0, "approved": 0, "declined": 0},
                 "parent": None}
        try:
            entity_ids = self._dashboard_scope([entity_id], ctx)
            if not entity_ids:
                log_entity_refusal(ctx, "get_windows_approvals", entity_id)
                return empty
            approvals = UpdatesDatabase().get_windows_approvals(entity_ids[0], status, start,
                                                                limit, filter,
                                                                self._system(system))
            _sizes_for_xmlrpc(approvals["rows"])
            return approvals
        except Exception as e:
            return _read_failed("get_windows_approvals", e, empty)

    @with_optional_xmpp_context
    def set_windows_approval(self, entity_id, update_ids, status, ctx=None):
        try:
            entity = self._settable_entity(ctx, "set_windows_approval", entity_id)
            if entity is None:
                return False
            if not UpdatesDatabase().set_windows_approval(entity, update_ids, status,
                                                          self._ctx_login(ctx)):
                return False
        except Exception as e:
            logger.error(f"set_windows_approval: {e}")
            logger.error(traceback.format_exc())
            return False
        self._notify_substitute("set_windows_approval", {"approvals_changed": entity})
        return True

    @with_optional_xmpp_context
    def deploy_windows_update(self, update_id, entity_id, jid="", ctx=None):
        """Deploy an approved update's package on the entity machines missing it.

        Returns {"created": n, "skipped": [{"jid", "hostname", "reason"}]},
        plus "error" (and "package_error") when nothing could be attempted.
        """
        result = {"created": 0, "skipped": []}
        try:
            entity = self._writable_entity(ctx, "deploy_windows_update", entity_id)
            if entity is None:
                result["error"] = "entity_refused"
                return result
            try:
                update_id = int(update_id)
            except (TypeError, ValueError):
                result["error"] = "unknown_update"
                return result
            jid = str(jid or "").strip()
            targets = UpdatesDatabase().get_windows_deploy_targets(update_id, entity, jid or None)
            if targets is None:
                result["error"] = "unknown_update"
                return result
            update = targets["update"]
            machines = targets["machines"]
            if machines and all(machine["offer"] == "esu" for machine in machines):
                result["error"] = "esu_required"
                return result
            if not update["approved"]:
                result["error"] = "not_approved"
                return result
            if update["package_state"] != "ready":
                result["error"] = f"package_{update['package_state'] or 'missing'}"
                result["package_error"] = update["package_error"]
                return result
            if not self._windows_package_registered(update["package_uuid"]):
                result["error"] = "package_unregistered"
                return result
            if jid and not machines:
                result["error"] = "machine_not_targeted"
                return result

            login = self._ctx_login(ctx) or "root"
            self._create_windows_deployments("deploy_windows_update", update, machines,
                                             login, result)
            logger.info(f"deploy_windows_update: update {update_id}, entity {entity}, "
                        f"{result['created']} created, {len(result['skipped'])} skipped "
                        f"by {login}")
        except Exception as e:
            logger.error(f"deploy_windows_update: {e}")
            logger.error(traceback.format_exc())
            result["error"] = "internal_error"
        return result

    @with_optional_xmpp_context
    def deploy_linux_updates(self, jid, package="", ctx=None):
        """Upgrade on the Linux machine jid the packages approved by the rules of
        its entity, or only package when given, with the package of its family.

        Returns {"created": n, "skipped": [...], "packages": n}, plus "error"
        when nothing could be attempted."""
        result = {"created": 0, "skipped": [], "packages": 0}
        try:
            machine = UpdatesDatabase().get_windows_machine(jid)
            if machine is None or machine.get("os") != "linux":
                result["error"] = "machine_not_targeted"
                return result
            entity = self._writable_entity(ctx, "deploy_linux_updates", machine["entity_id"])
            if entity is None:
                result["error"] = "entity_refused"
                return result
            login = self._ctx_login(ctx) or "root"
            self._deploy_linux_machine("deploy_linux_updates", jid, entity, package, login, result)
            if "error" not in result:
                logger.info(f"deploy_linux_updates: {jid}, {result['packages']} packages, "
                            f"{result['created']} created by {login}")
        except Exception as e:
            logger.error(f"deploy_linux_updates: {e}")
            logger.error(traceback.format_exc())
            result["error"] = "internal_error"
        return result

    def _deploy_linux_machine(self, action, jid, entity, package, login, result):
        """Upgrade on the Linux machine jid of the writable entity its approved
        packages, or only package when given; fills result, with "error" when
        nothing could be attempted."""
        target = UpdatesDatabase().get_linux_deploy_target(jid, [entity])
        if target is None or not target["machines"]:
            result["error"] = "machine_not_targeted"
            return
        if package:
            target["packages"] = [name for name in target["packages"] if name == package]
        if not target["packages"]:
            result["error"] = "not_approved"
            return
        if not target["package_uuid"] or not self._windows_package_registered(
                target["package_uuid"]):
            result["error"] = "package_missing"
            return
        result["packages"] = len(target["packages"])
        update = {"package_uuid": target["package_uuid"], "kb": None,
                  "title": LINUX_UPDATE_DEPLOY_TITLE,
                  "deploy_title": LINUX_UPDATE_DEPLOY_TITLE}
        self._create_windows_deployments(action, update, target["machines"], login, result,
                                         parameters={"packages": target["packages"]})

    @with_optional_xmpp_context
    def uninstall_windows_update(self, kb, jid, ctx=None):
        """Remove the installed update kb from the machine jid with its package.

        Returns {"created": n, "skipped": [{"jid", "hostname", "reason"}]},
        plus "error" (and "package_error") when nothing could be attempted.
        """
        result = {"created": 0, "skipped": []}
        try:
            machine = UpdatesDatabase().get_windows_machine(jid)
            if machine is None:
                result["error"] = "machine_not_targeted"
                return result
            entity = self._writable_entity(ctx, "uninstall_windows_update", machine["entity_id"])
            if entity is None:
                result["error"] = "entity_refused"
                return result
            try:
                kb = int(str(kb).upper().replace("KB", ""))
            except (TypeError, ValueError):
                result["error"] = "unknown_update"
                return result
            targets = UpdatesDatabase().get_windows_uninstall_target(kb, jid, [entity])
            if targets is None:
                result["error"] = "unknown_update"
                return result
            update = targets["update"]
            if update["package_state"] != "ready":
                result["error"] = f"package_{update['package_state'] or 'missing'}"
                result["package_error"] = update["package_error"]
                return result
            if not self._windows_package_registered(update["package_uuid"]):
                result["error"] = "package_unregistered"
                return result
            if not targets["machines"]:
                result["error"] = "machine_not_targeted"
                return result
            login = self._ctx_login(ctx) or "root"
            self._create_windows_deployments("uninstall_windows_update", update,
                                             targets["machines"], login, result,
                                             section="uninstall")
            logger.info(f"uninstall_windows_update: KB{kb} on {jid}, "
                        f"{result['created']} created by {login}")
        except Exception as e:
            logger.error(f"uninstall_windows_update: {e}")
            logger.error(traceback.format_exc())
            result["error"] = "internal_error"
        return result

    @staticmethod
    def _create_windows_deployments(action, update, machines, login, result, section="update",
                                    parameters=None):
        """Create the deployment of update's ready package on each machine (its
        section "update", or "uninstall"), or append it to result["skipped"] with
        the reason. parameters: added to the command parameters (Linux: the
        packages to upgrade); update["deploy_title"] replaces the Windows title."""
        package_uuid = update["package_uuid"]
        pending = MscDatabase().pending_command_targets(
            package_uuid, [m["glpi_uuid"] for m in machines])
        start_date = datetime.now().replace(microsecond=0)
        end_date = start_date + timedelta(hours=WINDOWS_UPDATE_DEPLOY_HOURS)
        label = f"KB{update['kb']}" if update["kb"] else update["title"]
        if section == "uninstall":
            label += " (uninstall)"
        title = (f"{update.get('deploy_title') or WINDOWS_UPDATE_DEPLOY_TITLE + ' ' + label}"
                 f" -@upd@- {start_date:%Y-%m-%d %H:%M:%S}")
        # The relay plays the package's own section (update) unless the login
        # command names another one
        section_parameter = "" if section == "update" else f'"section":"{section}"'
        for machine in machines:
            reason = _deploy_refusal(machine, pending)
            if reason is None:
                ret = MscDatabase().deploy_package_msc(package_uuid,
                                                       machine["glpi_uuid"],
                                                       machine["hostname"],
                                                       title_deployement=title,
                                                       start_date=start_date,
                                                       end_date=end_date,
                                                       userconnect=login,
                                                       usercreator=login,
                                                       upgrade_parameters=dict(
                                                           parameters or {}, section=section))
                if ret["success"]:
                    XmppMasterDatabase().addlogincommand(login, ret["commandid"],
                                                         "", "", "", "", section_parameter,
                                                         0, 0, 0, 0, {})
                    result["created"] += 1
                    continue
                logger.error(f"{action}: {machine['jid']}: {ret['msg']}")
                reason = "creation_failed"
            result["skipped"].append({"jid": machine["jid"],
                                      "hostname": machine["hostname"],
                                      "reason": reason})

    @staticmethod
    def _windows_package_registered(package_uuid):
        pkgsinfos = PkgsDatabase().pkgs_get_infos_details(package_uuid)
        return bool(pkgsinfos) and pkgsinfos.get("label") != ""

    def _group_glpi_uuids(self, gid):
        """GLPI uuids of the group members visible to the user, None when the
        group is unknown or not accessible."""
        ctx = self.currentContext
        if not DyngroupDatabase().get_group(ctx, gid):
            return None
        uuids = ComputerManager().getRestrictedComputersList(
            ctx, 0, -1, {"gid": gid}, justId=True) or []
        return [str(uuid) for uuid in uuids]

    @staticmethod
    def _group_id(gid):
        if isinstance(gid, bool):
            return None
        try:
            return int(gid)
        except (TypeError, ValueError):
            return None

    def _group_uuids(self, action, gid, ctx):
        """_group_glpi_uuids of the group for the user, None when refused."""
        gid = self._group_id(gid)
        uuids = self._group_glpi_uuids(gid) if gid is not None else None
        if uuids is None:
            logger.warning(f"{action}: group {gid!r} refused for user {self._ctx_login(ctx)!r}")
        return uuids

    @with_optional_xmpp_context
    def get_windows_group_updates(self, gid, ctx=None):
        empty = {"rows": [], "machines": 0}
        try:
            uuids = self._group_uuids("get_windows_group_updates", gid, ctx)
            if not uuids:
                return empty
            entity_ids = self._dashboard_scope([], ctx)
            if not entity_ids:
                return empty
            return UpdatesDatabase().get_windows_group_updates(uuids, entity_ids)
        except Exception as e:
            return _read_failed("get_windows_group_updates", e, empty)

    @with_optional_xmpp_context
    def deploy_windows_update_group(self, update_id, gid, ctx=None):
        """Deploy an update's package on the group machines missing it, each one
        if approved for its entity.

        Returns {"created": n, "skipped": [{"jid", "hostname", "reason"}]},
        plus "error" when nothing could be attempted.
        """
        result = {"created": 0, "skipped": []}
        try:
            uuids = self._group_uuids("deploy_windows_update_group", gid, ctx)
            if uuids is None:
                result["error"] = "unknown_group"
                return result
            try:
                update_id = int(update_id)
            except (TypeError, ValueError):
                result["error"] = "unknown_update"
                return result
            entity_ids = self._dashboard_scope([], ctx)
            targets = UpdatesDatabase().get_windows_group_deploy_targets(update_id, uuids,
                                                                         entity_ids)
            if targets is None:
                result["error"] = "unknown_update"
                return result
            update = targets["update"]
            package_ready = (update["package_state"] == "ready"
                             and self._windows_package_registered(update["package_uuid"]))
            candidates = []
            for machine in targets["machines"]:
                if not check_user_entity(ctx, machine["entity_id"]):
                    reason = "entity_refused"
                elif not package_ready:
                    reason = "package_not_ready"
                else:
                    candidates.append(machine)
                    continue
                result["skipped"].append({"jid": machine["jid"],
                                          "hostname": machine["hostname"],
                                          "reason": reason})
            login = self._ctx_login(ctx) or "root"
            if candidates:
                self._create_windows_deployments("deploy_windows_update_group", update,
                                                 candidates, login, result)
            logger.info(f"deploy_windows_update_group: update {update_id}, group {gid}, "
                        f"{result['created']} created, {len(result['skipped'])} skipped "
                        f"by {login}")
        except Exception as e:
            logger.error(f"deploy_windows_update_group: {e}")
            logger.error(traceback.format_exc())
            result["error"] = "internal_error"
        return result

    def _linux_group_targets(self, action, gid, ctx):
        """get_linux_group_targets of the group for the user, None when refused."""
        uuids = self._group_uuids(action, gid, ctx)
        if uuids is None:
            return None
        return UpdatesDatabase().get_linux_group_targets(uuids, self._dashboard_scope([], ctx))

    @with_optional_xmpp_context
    def get_linux_group_packages(self, group_id, start=0, limit=-1, filter="", ctx=None):
        """Packages deploy_linux_group would send: {"total": n, "rows": [{"package",
        "severity", "machines"}]}, by name."""
        empty = {"total": 0, "rows": []}
        try:
            uuids = self._group_uuids("get_linux_group_packages", group_id, ctx)
            if uuids is None:
                return empty
            return UpdatesDatabase().get_linux_group_packages(
                uuids, self._dashboard_scope([], ctx), start, limit, filter)
        except Exception as e:
            return _read_failed("get_linux_group_packages", e, empty)

    @with_optional_xmpp_context
    def get_linux_group_summary(self, group_id, ctx=None):
        """{"machines": Linux machines of the group, "eligible": those deploy_linux_group
        would deploy to now, "packages": sum of their approved packages per machine,
        eligible or not}."""
        summary = {"machines": 0, "eligible": 0, "packages": 0}
        try:
            group = self._linux_group_targets("get_linux_group_summary", group_id, ctx)
            if group is None:
                return summary
            summary["machines"] = group["machines"]
            registered = {}
            for machine in group["targets"]:
                summary["packages"] += machine["approved_packages"]
                package_uuid = machine["package_uuid"]
                if package_uuid and package_uuid not in registered:
                    registered[package_uuid] = self._windows_package_registered(package_uuid)
                # "running" already covers the waiting commands of any package
                if (machine["approved_packages"] and registered.get(package_uuid)
                        and check_user_entity(ctx, machine["entity_id"])
                        and _deploy_refusal(machine, ()) is None):
                    summary["eligible"] += 1
            return summary
        except Exception as e:
            return _read_failed("get_linux_group_summary", e, summary)

    @with_optional_xmpp_context
    def deploy_linux_group(self, group_id, ctx=None):
        """Upgrade on each Linux machine of the group the packages approved by its
        entity. Machines with nothing to upgrade are left out.

        Returns {"deployed": n, "skipped": [{"jid", "hostname", "reason"}], "error": ""}."""
        result = {"deployed": 0, "skipped": [], "error": ""}
        try:
            group = self._linux_group_targets("deploy_linux_group", group_id, ctx)
            if group is None:
                result["error"] = "unknown_group"
                return result
            login = self._ctx_login(ctx) or "root"
            for machine in group["targets"]:
                entity = self._writable_entity(ctx, "deploy_linux_group", machine["entity_id"])
                deployed = {"created": 0, "skipped": [], "packages": 0}
                if entity is None:
                    deployed["error"] = "entity_refused"
                else:
                    self._deploy_linux_machine("deploy_linux_group", machine["jid"], entity,
                                               "", login, deployed)
                result["deployed"] += deployed["created"]
                result["skipped"] += deployed["skipped"]
                if "error" in deployed:
                    reason = deployed["error"]
                    if reason in ("package_missing", "machine_not_targeted"):
                        reason = "package_not_ready"
                    result["skipped"].append({"jid": machine["jid"],
                                              "hostname": machine["hostname"],
                                              "reason": reason})
            logger.info(f"deploy_linux_group: group {group_id}, {result['deployed']} deployed, "
                        f"{len(result['skipped'])} skipped by {login}")
        except Exception as e:
            logger.error(f"deploy_linux_group: {e}")
            logger.error(traceback.format_exc())
            result["error"] = "internal_error"
        return result

    @staticmethod
    def _windows_hhmm(value):
        """Normalised "HH:MM", "" when empty, None when invalid."""
        value = str(value or "").strip()
        if not value:
            return ""
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", value)
        if not match:
            return None
        hours, minutes = int(match.group(1)), int(match.group(2))
        if hours > 23 or minutes > 59:
            return None
        return f"{hours:02d}:{minutes:02d}"

    @with_optional_xmpp_context
    def get_windows_settings(self, entity_id, ctx=None):
        empty = {"auto_deploy": False, "window_start": "", "window_end": "",
                 "upgrade_window_start": "", "upgrade_window_end": "",
                 "inherited_from": None, "parent": None}
        try:
            entity_ids = self._dashboard_scope([entity_id], ctx)
            if not entity_ids:
                log_entity_refusal(ctx, "get_windows_settings", entity_id)
                return empty
            return UpdatesDatabase().get_windows_settings(entity_ids[0])
        except Exception as e:
            return _read_failed("get_windows_settings", e, empty)

    @with_optional_xmpp_context
    def set_windows_settings(self, entity_id, auto_deploy, window_start, window_end,
                             upgrade_window_start="", upgrade_window_end="", ctx=None):
        try:
            entity = self._settable_entity(ctx, "set_windows_settings", entity_id)
            if entity is None:
                return False
            auto_deploy = auto_deploy in (True, 1, "1", "true", "on")
            window_start = self._windows_hhmm(window_start)
            window_end = self._windows_hhmm(window_end)
            upgrade_window_start = self._windows_hhmm(upgrade_window_start)
            upgrade_window_end = self._windows_hhmm(upgrade_window_end)
            if None in (window_start, window_end, upgrade_window_start, upgrade_window_end):
                return False
            # A window may cross midnight (22:00-06:00)
            if auto_deploy and (not window_start or not window_end
                                or window_start == window_end):
                return False
            # Upgrade window: both times or none (steps start at any time)
            if bool(upgrade_window_start) != bool(upgrade_window_end) or (
                    upgrade_window_start and upgrade_window_start == upgrade_window_end):
                return False
            return UpdatesDatabase().set_windows_settings(entity, auto_deploy,
                                                          window_start, window_end,
                                                          upgrade_window_start,
                                                          upgrade_window_end,
                                                          self._ctx_login(ctx))
        except Exception as e:
            logger.error(f"set_windows_settings: {e}")
            logger.error(traceback.format_exc())
            return False

    @with_optional_xmpp_context
    def reset_windows_settings(self, entity_id, ctx=None):
        """The entity takes its parent's settings again; refused for the root."""
        try:
            entity = self._writable_entity(ctx, "reset_windows_settings", entity_id)
            if entity is None:
                return False
            return UpdatesDatabase().reset_windows_settings(entity)
        except Exception as e:
            logger.error(f"reset_windows_settings: {e}")
            logger.error(traceback.format_exc())
            return False

    @with_optional_xmpp_context
    def get_windows_approval_rules(self, entity_id, system="windows", ctx=None):
        empty = {"rules": [], "inherited_from": None, "parent": None}
        try:
            entity_ids = self._dashboard_scope([entity_id], ctx)
            if not entity_ids:
                log_entity_refusal(ctx, "get_windows_approval_rules", entity_id)
                return empty
            return UpdatesDatabase().get_windows_approval_rules(entity_ids[0],
                                                                self._system(system))
        except Exception as e:
            return _read_failed("get_windows_approval_rules", e, empty)

    @with_optional_xmpp_context
    def set_windows_approval_rules(self, entity_id, rules, system="windows", ctx=None):
        try:
            entity = self._settable_entity(ctx, "set_windows_approval_rules", entity_id)
            if entity is None:
                return False
            if not UpdatesDatabase().set_windows_approval_rules(entity, rules or [],
                                                                self._ctx_login(ctx),
                                                                self._system(system)):
                return False
        except Exception as e:
            logger.error(f"set_windows_approval_rules: {e}")
            logger.error(traceback.format_exc())
            return False
        self._notify_substitute("set_windows_approval_rules", {"approvals_changed": entity})
        return True

    @with_optional_xmpp_context
    def reset_windows_approval_rules(self, entity_id, system="windows", ctx=None):
        """The entity takes its parent's rules of the system again; refused for the root."""
        try:
            entity = self._writable_entity(ctx, "reset_windows_approval_rules", entity_id)
            if entity is None:
                return False
            if not UpdatesDatabase().reset_windows_approval_rules(entity, self._system(system)):
                return False
        except Exception as e:
            logger.error(f"reset_windows_approval_rules: {e}")
            logger.error(traceback.format_exc())
            return False
        self._notify_substitute("reset_windows_approval_rules", {"approvals_changed": entity})
        return True


def get_replication_state():
    return UpdatesDatabase().get_replication_state()
