# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# SqlAlchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    text,
    bindparam,
)
from datetime import datetime

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster import (
    DEPLOY_LOG_COLUMNS,
    DEPLOY_LOG_DATES,
    deploy_log_fields,
)

# Imported last
import logging
import json
import re

logger = logging.getLogger()

STALE_DAYS = 7
WINDOWS_SEARCH_FAILURES = ("failed", "blocked", "timeout", "locked")
# Windows 11 requirements measured by the machine plugin (report["windows11"])
# First build of Windows 11 (21H2)
WINDOWS11_FIRST_BUILD = 22000
WINDOWS11_CRITERIA = ("cpu", "tpm", "secure_boot", "firmware", "ram_gb", "disk_size_gb",
                      "graphics", "display")

def linux_release_key(distribution, release):
    """Same key as the primary key of entity_linux_releases: case does not count."""
    return str(distribution or "").strip().lower(), str(release or "").strip().lower()


def linux_version_order(release):
    """Natural order: Debian 9 comes before Debian 10."""
    return [(0, int(part), "") if part.isdigit() else (1, 0, part)
            for part in re.findall(r"\d+|\D+", release.lower())]


def linux_release_name(distribution, version):
    """Version as linux_releases names it: AlmaLinux 9 for a machine on 9.7."""
    if str(distribution or "").strip().lower() == "almalinux":
        return version.split(".", 1)[0]
    return version


def linux_reported_versions(distribution, upgrade, system):
    """{version: codename} a machine reports: current and target of report["upgrade"],
    else its current version from report["system"]. upgrade, system: JSON text."""
    try:
        upgrade = json.loads(upgrade) if upgrade else None
        system = json.loads(system) if system else None
    except ValueError:
        return {}
    upgrade = upgrade if isinstance(upgrade, dict) else {}
    for parts in ((upgrade.get("current"), upgrade.get("target")), (system,)):
        versions = {}
        for part in parts:
            version = part.get("version") if isinstance(part, dict) else None
            if isinstance(version, str) and version.strip():
                codename = part.get("codename")
                versions[linux_release_name(distribution, version.strip())] = (
                    codename if isinstance(codename, str) else "")
        if versions:
            return versions
    return {}


def linux_release_rows(reports, tracked, catalog):
    """[{distribution, release, codename, tracked, machines}] per distribution, oldest
    version first: the versions the machines report, the versions of the catalog from
    the oldest reported one on, and the tracked ones, shown without machine since they
    still apply.

    reports: (distribution, report["upgrade"], report["system"]) of one machine each;
    tracked: (distribution, release_name);
    catalog: (distribution, release_name, codename) of linux_releases."""
    rows = {}

    def row_of(distribution, release):
        return rows.setdefault(linux_release_key(distribution, release), {
            "distribution": distribution, "release": release, "codename": "",
            "tracked": False, "machines": 0})

    for distribution, upgrade, system in reports:
        for release, codename in linux_reported_versions(distribution, upgrade, system).items():
            row = row_of(distribution, release)
            row["machines"] += 1
            row["codename"] = row["codename"] or codename

    oldest = {}
    for row in rows.values():
        key = row["distribution"].lower()
        if key not in oldest or linux_version_order(row["release"]) < oldest[key][1]:
            oldest[key] = (row["distribution"], linux_version_order(row["release"]))
    for distribution, release, codename in catalog:
        seen = oldest.get(distribution.lower())
        if seen and linux_version_order(release) >= seen[1]:
            row = row_of(seen[0], release)
            row["codename"] = row["codename"] or codename or ""

    for distribution, release in tracked:
        row_of(distribution, release)["tracked"] = True
    return sorted(rows.values(), key=lambda row: (row["distribution"].lower(),
                                                  linux_version_order(row["release"])))


def windows11_requirements(eligible, blockers, source, facts):
    """Verdict and measured values of the Windows 11 requirements of a machine report.

    eligible/blockers/source: machine_reports columns; facts: report["windows11"]
    as JSON text. secure_boot goes as text: a missing value must not reach the
    page as false."""
    try:
        facts = json.loads(facts) if facts else {}
    except ValueError:
        facts = {}
    if not isinstance(facts, dict):
        facts = {}
    criteria = {key: facts.get(key) for key in WINDOWS11_CRITERIA}
    if isinstance(criteria["secure_boot"], bool):
        criteria["secure_boot"] = "enabled" if criteria["secure_boot"] else "disabled"
    return {
        "eligible": None if eligible is None else bool(eligible),
        "blockers": [code.strip() for code in (blockers or "").split(",") if code.strip()],
        # "windows": verdict of Windows; "facts": measured only, processor not judged
        "source": source,
        "criteria": criteria,
    }


# Offers counted as missing, optional never is
MISSING_OFFER_SQL = "mu.offer IN ('main', 'esu')"
# Aliases: mu = machine_updates, u = updates (LEFT JOIN, NULL when not in catalog)
EXPLOITED_KB_SQL = """EXISTS (SELECT 1 FROM kb_cves kc JOIN cves c ON c.id = kc.cve_id
                WHERE kc.kb = COALESCE(u.kb, mu.kb) AND c.exploited = 1)"""
CRITICAL_UPDATE_SQL = f"(u.severity = 'Critical' OR {EXPLOITED_KB_SQL})"
# Same on a machine_updates row: a Linux package carries its own severity
MACHINE_CRITICAL_UPDATE_SQL = (
    f"(COALESCE(u.severity, mu.severity) = 'Critical' OR {EXPLOITED_KB_SQL})"
)
# Size of an update, alias p = its package (LEFT JOIN): the real size of the
# package, else the sum of the language-neutral files it would hold, NULL as soon
# as one of them has no known size since SUM would silently skip it
WINDOWS_UPDATE_SIZE_TEMPLATE = """COALESCE(p.size,
                (SELECT CASE WHEN COUNT(*) = COUNT(f.size) THEN SUM(f.size) END
                   FROM update_files uf JOIN files f ON f.id = uf.file_id
                  WHERE uf.update_id = {update_id} AND uf.language IS NULL))"""

# Machines without glpi_uuid or GLPI entity cannot be scoped and are left out
WINDOWS_ENTITY_JOIN_TEMPLATE = """
    JOIN xmppmaster.local_glpi_machines lgm
      ON {uuid} REGEXP '^UUID[0-9]+$'
     AND lgm.id = CAST(SUBSTRING({uuid}, 5) AS UNSIGNED)
     AND lgm.is_deleted = 0
     AND lgm.is_template = 0
    JOIN xmppmaster.local_glpi_entities e ON e.id = lgm.entities_id
    LEFT JOIN effective_products efp ON efp.entity_id = lgm.entities_id
    LEFT JOIN (SELECT entity_id, COUNT(*) AS tracked_products
                 FROM entity_products GROUP BY entity_id) ep
      ON ep.entity_id = efp.source_id
"""
WINDOWS_MACHINE_ENTITY_JOIN = WINDOWS_ENTITY_JOIN_TEMPLATE.format(uuid="mr.glpi_uuid")

# A machine is evaluated when its report is recent and, for Windows, its entity
# tracks a product. A Linux machine lists its packages itself: only its last
# search says something, no row after a failure does not mean up to date
WINDOWS_EVALUATED_SQL = """(mr.received_at >= NOW() - INTERVAL :stale_days DAY
            AND ((mr.os = 'linux' AND mr.search_status = 'ok')
                 OR (mr.os <> 'linux' AND COALESCE(ep.tracked_products, 0) > 0)))"""

# The last search failed: the machine cannot be proven up to date
SEARCH_FAILED_SQL = "COALESCE(mr.search_status IN ({}), 0)".format(
    ", ".join(f"'{status}'" for status in WINDOWS_SEARCH_FAILURES))

# Last xmppmaster.machines row (xm) of each bare jid: several resources of a jid
# must not repeat a report
XM_LATEST_JOIN_SQL = """
    LEFT JOIN (SELECT SUBSTRING_INDEX(jid, '/', 1) AS bare_jid, MAX(id) AS id
                 FROM xmppmaster.machines
                GROUP BY SUBSTRING_INDEX(jid, '/', 1)) xl ON xl.bare_jid = mr.jid
    LEFT JOIN xmppmaster.machines xm ON xm.id = xl.id
"""

# Machines at or below :entity_id
ENTITY_SUBTREE_SQL = """(SELECT anc.entity_id FROM entity_ancestors anc
                          WHERE anc.ancestor_id = :entity_id)"""

# Windows 10 out of support (since 2025-10-14) without an ESU license: Windows
# offers it no security update any more, so an empty list does not mean up to date.
# LTSC editions keep their own longer support.
WINDOWS_UNSUPPORTED_SQL = """(mr.system_type = 'client'
            AND mr.product LIKE 'Windows 10%%' AND mr.product NOT LIKE '%%LTSC%%'
            AND COALESCE(mr.esu_licensed, 0) = 0)"""

# Catalog releases (alias r) matching the machine's build, architecture and
# system type: a build can be shared by a client and a server product
WINDOWS_MACHINE_RELEASE_MATCH_SQL = """r.build = mr.build AND r.name IS NOT NULL
                  AND (COALESCE(mr.architecture, '') = '' OR COALESCE(r.architecture, '') = ''
                       OR LOWER(r.architecture) = LOWER(mr.architecture))
                  AND (mr.system_type IS NULL
                       OR (mr.system_type = 'client' AND LEFT(r.os_product_name, 7) = 'Client.')
                       OR (mr.system_type = 'server' AND LEFT(r.os_product_name, 7) = 'Server.'))"""

# The machine's version is not tracked by its entity (own or inherited)
WINDOWS_UNTRACKED_VERSION_SQL = f"""EXISTS (SELECT 1 FROM releases r
                WHERE {WINDOWS_MACHINE_RELEASE_MATCH_SQL}
                  AND NOT EXISTS (SELECT 1 FROM entity_releases er
                        WHERE er.entity_id = efp.source_id
                          AND er.product_id = r.product_id
                          AND er.release_name = r.name))"""

# Machine's release name from the catalog, falling back to the reported DisplayVersion
WINDOWS_MACHINE_RELEASE_SQL = f"""COALESCE((SELECT r.name FROM releases r
                WHERE {WINDOWS_MACHINE_RELEASE_MATCH_SQL}
                ORDER BY r.id LIMIT 1), mr.`release`)"""

# Catalog title of each KB of :kbs (expanding) on the machine :jid: an installation
# media shares the KB of its update, and the rows of a recurring KB (Defender, MSRT)
# each name a version the machine may not have, hence an empty title outside its release
WINDOWS_INSTALLED_TITLES_SQL = f"""
    SELECT t.kb, t.title FROM (
        SELECT u.kb,
               CASE WHEN r.id IS NULL
                         AND u.title REGEXP 'version [0-9]+[.][0-9]|[ (]v[0-9]+[.][0-9]'
                    THEN '' ELSE u.title END AS title,
               ROW_NUMBER() OVER (PARTITION BY u.kb
                                  ORDER BY COALESCE(u.classification, '') = 'Upgrades',
                                           u.title LIKE '%%Internal%%'
                                           OR u.title LIKE '%%Prerelease%%',
                                           r.id IS NULL, u.published_at DESC, u.id DESC) AS title_rank
        FROM updates u
        JOIN machine_reports mr ON mr.jid = :jid
        LEFT JOIN releases r ON r.id = u.release_id
             AND {WINDOWS_MACHINE_RELEASE_MATCH_SQL}
        WHERE u.kb IN :kbs) t
    WHERE t.title_rank = 1
"""

# xmppmaster.deploy states after which a deployment no longer runs
# A transfer failure, ERROR or ABORT, is not final: xmppmaster restarts it after
# 10 minutes (mmc_restart_blocked_deployments_transfer_error) while its window is open
DEPLOY_FINAL_STATE_SQL = """(d.state IN ('DEPLOYMENT SUCCESS', 'UNINSTALL SUCCESS')
                OR ((d.state LIKE 'ERROR%%' OR d.state LIKE 'ABORT%%')
                    AND d.state NOT LIKE '%%TRANSFER FAILED'))"""
DEPLOY_IN_PROGRESS_SQL = f"""(NOT {DEPLOY_FINAL_STATE_SQL}
                AND (d.endcmd IS NULL OR d.endcmd >= NOW()))"""
# msc commands (alias c) of the machine mr not yet handed to the deployment loop
PENDING_COMMANDS_SQL = """SELECT 1 FROM msc.commands c
                  JOIN msc.commands_on_host coh ON coh.fk_commands = c.id
                  JOIN msc.target t ON t.id = coh.fk_target
                  JOIN msc.phase ph ON ph.fk_commands_on_host = coh.id
                 WHERE CONVERT(t.target_uuid USING utf8mb4) COLLATE utf8mb4_unicode_ci = mr.glpi_uuid
                   AND ph.name = 'execute' AND ph.state = 'ready' AND c.end_date >= NOW()"""
# A deployment of any package holds the machine, or is about to
MACHINE_BUSY_SQL = f"""(EXISTS (SELECT 1 FROM xmppmaster.deploy d
                 WHERE d.inventoryuuid = mr.glpi_uuid AND {DEPLOY_IN_PROGRESS_SQL})
            OR EXISTS ({PENDING_COMMANDS_SQL}))"""
# Restart to show: Windows raises its signal during an installation. CASE so that
# only the flagged machines pay for the lookup
MACHINE_REBOOT_SHOWN_SQL = f"""(CASE WHEN COALESCE(mr.reboot_pending, 0)
                 THEN NOT {MACHINE_BUSY_SQL} ELSE 0 END)"""
# Without a report since, a restart sent from Medulla may be sent again after
RESTART_RETRY_MINUTES = 15
MACHINE_RESTART_REQUESTED_SQL = f"""COALESCE(mr.restart_requested_at > mr.received_at
                 AND mr.restart_requested_at > NOW() - INTERVAL {RESTART_RETRY_MINUTES} MINUTE, 0)"""
# Titles of the upgrade step deployments (substitute: upgrades.WINDOWS_TITLE, LINUX_TITLE)
UPGRADE_STEP_TITLE_SQL = """({column} LIKE 'Windows upgrade to %%'
                OR {column} LIKE 'Linux upgrade to %%')"""
# A deployment of the machine mr whose title matches runs, or is about to
DEPLOY_TITLED_RUNNING_SQL = f"""(EXISTS (SELECT 1 FROM xmppmaster.deploy d
                 WHERE d.inventoryuuid = mr.glpi_uuid
                   AND {{deploy_title}}
                   AND {DEPLOY_IN_PROGRESS_SQL})
            OR EXISTS ({PENDING_COMMANDS_SQL}
                   AND {{command_title}}))"""
UPGRADE_STEP_RUNNING_SQL = DEPLOY_TITLED_RUNNING_SQL.format(
    deploy_title=UPGRADE_STEP_TITLE_SQL.format(column="d.title"),
    command_title=UPGRADE_STEP_TITLE_SQL.format(column="c.title"))
# Any other deployment of the machine mr
NOT_UPGRADE_STEP_RUNNING_SQL = DEPLOY_TITLED_RUNNING_SQL.format(
    deploy_title=f"NOT {UPGRADE_STEP_TITLE_SQL.format(column='d.title')}",
    command_title=f"NOT {UPGRADE_STEP_TITLE_SQL.format(column='c.title')}")
# Deployment d succeeded since the last report of the machine mr: not confirmed yet
DEPLOY_AWAITING_REPORT_SQL = """(d.state IN ('DEPLOYMENT SUCCESS', 'UNINSTALL SUCCESS')
                AND d.start >= mr.received_at)"""
# Other than an upgrade step, a deployment of the machine mr runs or awaits its report
MACHINE_UPDATING_SQL = f"""({NOT_UPGRADE_STEP_RUNNING_SQL}
            OR EXISTS (SELECT 1 FROM xmppmaster.deploy d
                 WHERE d.inventoryuuid = mr.glpi_uuid
                   AND NOT {UPGRADE_STEP_TITLE_SQL.format(column='d.title')}
                   AND {DEPLOY_AWAITING_REPORT_SQL}))"""

# One row per Windows machine of :entity_ids (expanding); also binds :stale_days
WINDOWS_MACHINES_SQL = f"""
    SELECT mr.jid, COALESCE(xm.hostname, mr.hostname) AS hostname,
           COALESCE(xm.enabled, 0) AS online,
           mr.glpi_uuid, mr.product, mr.`release`, mr.received_at,
           lgm.entities_id AS entity_id,
           e.name AS entity_name,
           COALESCE(ep.tracked_products, 0) AS tracked_products,
           {WINDOWS_EVALUATED_SQL} AS evaluated,
           {WINDOWS_UNSUPPORTED_SQL} AS unsupported,
           {WINDOWS_UNTRACKED_VERSION_SQL} AS untracked_version,
           {MACHINE_REBOOT_SHOWN_SQL} AS reboot_pending,
           {MACHINE_RESTART_REQUESTED_SQL} AS restart_requested,
           (SELECT COUNT(*) FROM machine_updates mu
             WHERE mu.jid = mr.jid AND {MISSING_OFFER_SQL}) AS missing,
           (SELECT COUNT(*)
              FROM machine_updates mu
              LEFT JOIN updates u ON u.id = mu.update_id
             WHERE mu.jid = mr.jid AND {MISSING_OFFER_SQL}
               AND {MACHINE_CRITICAL_UPDATE_SQL}) AS critical,
           {SEARCH_FAILED_SQL} AS search_failed,
           {MACHINE_UPDATING_SQL} AS updating,
           0 AS no_report
    FROM machine_reports mr
    {WINDOWS_MACHINE_ENTITY_JOIN}
    {XM_LATEST_JOIN_SQL}
    WHERE lgm.entities_id IN :entity_ids
"""

# xmppmaster (utf8/general_ci) values compared to updates (utf8mb4_unicode_ci)
XM_BARE_JID_SQL = ("CONVERT(SUBSTRING_INDEX(xm.jid, '/', 1) USING utf8mb4)"
                   " COLLATE utf8mb4_unicode_ci")
XM_GLPI_UUID_SQL = "CONVERT(xm.uuid_inventorymachine USING utf8mb4) COLLATE utf8mb4_unicode_ci"
XM_WINDOWS_PLATFORM_SQL = "{xm}.platform LIKE 'Microsoft Windows%%'"
# Linux agents report their distribution as platform (« Debian GNU/Linux 12 »)
XM_LINUX_PLATFORM_SQL = ("{xm}.platform NOT LIKE 'Microsoft Windows%%'"
                         " AND {xm}.platform NOT LIKE '%%mac%%'")
XM_ANY_PLATFORM_SQL = "{xm}.platform NOT LIKE '%%mac%%'"
NO_REPORT_PLATFORMS = {"windows": XM_WINDOWS_PLATFORM_SQL, "linux": XM_LINUX_PLATFORM_SQL,
                       None: XM_ANY_PLATFORM_SQL}
XM_OS_SQL = "CASE WHEN xm.platform LIKE 'Microsoft Windows%%' THEN 'windows' ELSE 'linux' END"

# Known machine of a system (one per GLPI machine) without any report, under
# its own jid or its GLPI identifier
NO_REPORT_FROM_TEMPLATE = f"""
    FROM xmppmaster.machines xm
    {WINDOWS_ENTITY_JOIN_TEMPLATE.format(uuid="xm.uuid_inventorymachine")}
    WHERE xm.agenttype = 'machine' AND {{platform}}
      AND NOT EXISTS (SELECT 1 FROM machine_reports mr WHERE mr.jid = {XM_BARE_JID_SQL})
      AND NOT EXISTS (SELECT 1 FROM machine_reports mr WHERE mr.glpi_uuid = {XM_GLPI_UUID_SQL})
      AND NOT EXISTS (SELECT 1 FROM xmppmaster.machines xm2
                       WHERE xm2.uuid_inventorymachine = xm.uuid_inventorymachine
                         AND xm2.agenttype = 'machine' AND {{platform2}}
                         AND xm2.id > xm.id)
"""


def no_report_from_sql(platform):
    return NO_REPORT_FROM_TEMPLATE.format(platform=platform.format(xm="xm"),
                                          platform2=platform.format(xm="xm2"))


# Same columns as WINDOWS_MACHINES_SQL
NO_REPORT_MACHINES_TEMPLATE = """
    SELECT {bare_jid} AS jid,
           CONVERT(xm.hostname USING utf8mb4) COLLATE utf8mb4_unicode_ci AS hostname,
           COALESCE(xm.enabled, 0) AS online,
           {glpi_uuid} AS glpi_uuid,
           NULL AS product, NULL AS `release`, NULL AS received_at,
           lgm.entities_id AS entity_id,
           e.name AS entity_name,
           COALESCE(ep.tracked_products, 0) AS tracked_products,
           0 AS evaluated, 0 AS unsupported, 0 AS untracked_version,
           0 AS reboot_pending, 0 AS restart_requested, 0 AS missing, 0 AS critical,
           0 AS search_failed, 0 AS updating,
           1 AS no_report
    {from_sql}
      AND lgm.entities_id IN :entity_ids
"""


def no_report_machines_sql(platform):
    return NO_REPORT_MACHINES_TEMPLATE.format(
        bare_jid=XM_BARE_JID_SQL, glpi_uuid=XM_GLPI_UUID_SQL,
        from_sql=no_report_from_sql(platform))


# Machines with a report, then known machines without one (no_report = 1)
WINDOWS_ALL_MACHINES_SQL = f"""
    {WINDOWS_MACHINES_SQL}
      AND mr.os = 'windows'
    UNION ALL
    {no_report_machines_sql(XM_WINDOWS_PLATFORM_SQL)}
"""
# Linux machines, of one distribution when :distribution is not empty; a
# machine without report has no known distribution: listed under all only
LINUX_MACHINES_SQL = f"""
    {WINDOWS_MACHINES_SQL}
      AND mr.os = 'linux' AND (:distribution = '' OR mr.distribution = :distribution)
    UNION ALL
    {no_report_machines_sql(XM_LINUX_PLATFORM_SQL)}
      AND :distribution = ''
"""


def machines_sql(system):
    """Machine rows of a system tab: "windows" or "linux"."""
    return LINUX_MACHINES_SQL if system == "linux" else WINDOWS_ALL_MACHINES_SQL


# On the rows (alias m) of machines_sql: an untracked version counts as not
# evaluated, its row keeps evaluated for its status
MACHINE_COUNTED_SQL = "(m.evaluated AND NOT m.untracked_version)"
MACHINE_UP_TO_DATE_SQL = f"""({MACHINE_COUNTED_SQL} AND m.missing = 0 AND NOT m.unsupported
                AND NOT m.reboot_pending AND NOT m.search_failed)"""
# Cards of the status screen; to_update and reboot_pending follow the order of
# the status badges (updatesWinMachineStatus)
WINDOWS_MACHINE_CARDS = {
    "to_update": f"""{MACHINE_COUNTED_SQL} AND m.missing > 0 AND NOT m.search_failed
                AND NOT m.updating AND NOT m.reboot_pending AND NOT m.unsupported""",
    "critical": f"{MACHINE_COUNTED_SQL} AND m.critical > 0",
    "reboot_pending": "m.evaluated AND m.reboot_pending AND NOT m.search_failed AND NOT m.updating",
}

WINDOWS_SEVERITY_ORDER = ("Critical", "Important", "Moderate", "Low")
# Classifications of the Linux packages (vocabulary of the agent report)
LINUX_CLASSIFICATIONS = ("Security Updates", "Updates")
# Label of the deployment package of a Linux family (written by the substitute)
LINUX_PACKAGE_LABEL = "Linux updates (%s)"
# entity_overrides.setting of the approval rules of each system
RULES_SETTINGS = {"windows": "rules", "linux": "linux_rules"}
WINDOWS_APPROVAL_STATUSES = ("pending", "approved", "declined")
# machine_updates.offer, main first
WINDOWS_OFFERS_SQL = ", ".join(f"'{offer}'" for offer in ("main", "optional", "esu"))
# Rows of any other offer are ignored: FIELD would rank them first
KNOWN_OFFER_SQL = f"mu.offer IN ({WINDOWS_OFFERS_SQL})"


def windows_severity_rank_sql(column):
    whens = " ".join(f"WHEN '{severity}' THEN {rank}"
                     for rank, severity in enumerate(WINDOWS_SEVERITY_ORDER))
    return f"CASE {column} {whens} ELSE {len(WINDOWS_SEVERITY_ORDER)} END"


def windows_offer_rank_sql(column):
    return f"FIELD({column}, {WINDOWS_OFFERS_SQL})"


# Aliases: u = updates, mu = machine_updates or a row with its offer,
# a = effective decision for :entity_id;
# :rules_source = effective_rules.source_id of :entity_id
UPGRADES_CLASSIFICATION = "Upgrades"
# A rule without severity covers every update of its classification, offer main only
APPROVAL_RULE_MATCH_SQL = """(mu.offer = 'main'
            AND EXISTS (SELECT 1 FROM approval_rules ar
                WHERE ar.entity_id = :rules_source AND ar.os = 'windows'
                  AND ar.classification = u.classification
                  AND (ar.severity IS NULL OR ar.severity = u.severity)))"""
# Linux package (alias mu, no catalog update) approved by a rule of the entity
# {source}, :linux_rules_source for one entity
LINUX_RULE_MATCH_TEMPLATE = """EXISTS (SELECT 1 FROM approval_rules ar
                WHERE ar.entity_id = {source} AND ar.os = 'linux'
                  AND ar.classification = mu.classification
                  AND (ar.severity IS NULL OR ar.severity = mu.severity))"""
LINUX_RULE_MATCH_SQL = LINUX_RULE_MATCH_TEMPLATE.format(source=":linux_rules_source")
# Missing Linux packages approved by the rules of the entity of their machine
LINUX_APPROVED_PACKAGES_SQL = f"""
    FROM machine_updates mu
    JOIN machine_reports mr ON mr.jid = mu.jid
    {WINDOWS_MACHINE_ENTITY_JOIN}
    JOIN effective_rules er ON er.entity_id = lgm.entities_id AND er.os = 'linux'
    WHERE mu.package IS NOT NULL
      AND {LINUX_RULE_MATCH_TEMPLATE.format(source="er.source_id")}
"""
APPROVAL_STATUS_SQL = f"""COALESCE(a.status,
                CASE WHEN {APPROVAL_RULE_MATCH_SQL} THEN 'approved' ELSE 'pending' END)"""

# One row per catalog update missing on a machine of :entity_id or below, with
# the first offer it has among them and the machines where it has that offer;
# own_machines: those of :entity_id itself, the only ones its deployment reaches
WINDOWS_APPROVAL_UPDATES_SQL = f"""
    SELECT u.id AS update_id,
           COALESCE(u.kb, mu.kb) AS kb,
           u.title, u.classification, u.severity,
           mu.offer,
           {EXPLOITED_KB_SQL} AS exploited,
           {CRITICAL_UPDATE_SQL} AS critical,
           mu.machines, mu.own_machines,
           a.decided_by, a.decided_at, ea.source_id AS decided_in,
           (a.status IS NULL AND {APPROVAL_RULE_MATCH_SQL}) AS by_rule,
           {APPROVAL_STATUS_SQL} AS status
    FROM (SELECT o.* FROM
           (SELECT mu.update_id, mu.offer,
                   MAX(mu.kb) AS kb, COUNT(DISTINCT mu.jid) AS machines,
                   COUNT(DISTINCT CASE WHEN lgm.entities_id = :entity_id THEN mu.jid END) AS own_machines,
                   ROW_NUMBER() OVER (PARTITION BY mu.update_id
                                      ORDER BY {windows_offer_rank_sql("mu.offer")}) AS offer_rank
              FROM machine_reports mr
              {WINDOWS_MACHINE_ENTITY_JOIN}
              JOIN machine_updates mu ON mu.jid = mr.jid
             WHERE lgm.entities_id IN {ENTITY_SUBTREE_SQL}
               AND mu.update_id IS NOT NULL
               AND {KNOWN_OFFER_SQL}
             GROUP BY mu.update_id, mu.offer) o
          WHERE o.offer_rank = 1) mu
    JOIN updates u ON u.id = mu.update_id
    LEFT JOIN effective_approvals ea ON ea.entity_id = :entity_id AND ea.update_id = u.id
    LEFT JOIN approvals a ON a.entity_id = ea.source_id AND a.update_id = u.id
"""

# One row per Linux package missing on a machine of :entity_id or below
LINUX_APPROVAL_PACKAGES_SQL = f"""
    SELECT mu.package, mu.classification, mu.severity,
           COUNT(DISTINCT mu.jid) AS machines,
           {LINUX_RULE_MATCH_SQL} AS approved
    FROM machine_reports mr
    {WINDOWS_MACHINE_ENTITY_JOIN}
    JOIN machine_updates mu ON mu.jid = mr.jid
    WHERE lgm.entities_id IN {ENTITY_SUBTREE_SQL}
      AND mu.package IS NOT NULL
    GROUP BY mu.package, mu.classification, mu.severity
"""


# The servicing stack cannot be removed (Microsoft documentation of each
# cumulative); the .NET cumulative is installed as Package_for_DotNetRollup,
# a name without its KB; KB890830 (MSRT) has no installer
WINDOWS_NOT_REMOVABLE_SQL = """(u.kb = 890830
                OR u.title LIKE '%%Servicing Stack Update%%'
                OR u.title LIKE '%%Cumulative Update for .NET%%')"""
# Catalog update (alias u) with its deployment package
WINDOWS_UPDATE_PACKAGE_SQL = """SELECT u.id, u.kb, u.title, up.package_uuid, p.state AS package_state,
                   p.error AS package_error
            FROM updates u
            LEFT JOIN update_packages up ON up.update_id = u.id
            LEFT JOIN packages p ON p.uuid = up.package_uuid"""
# Linux release step stopped (alias mg = machine_upgrades): sources already changed
RELEASE_TO_RESUME_SQL = "mg.run_error LIKE 'release:%%'"
# Stable title prefix of Windows update deployments; "-@upd@-" files them as updates
WINDOWS_UPDATE_DEPLOY_TITLE = "Windows update"
# Install of the KB {kb} on the machine mr succeeded since its last report; the
# title of an uninstallation does not match
DEPLOYED_PENDING_REPORT_TEMPLATE = f"""EXISTS (SELECT 1 FROM xmppmaster.deploy d
                 WHERE d.inventoryuuid = mr.glpi_uuid
                   AND d.state = 'DEPLOYMENT SUCCESS'
                   AND d.start >= mr.received_at
                   AND d.title LIKE CONCAT('{WINDOWS_UPDATE_DEPLOY_TITLE} KB', {{kb}}, ' -@upd@- %%'))"""


def windows_conformity(up_to_date, machines):
    """Share of the known machines proven up to date: a machine without a
    report, or not evaluated, is not."""
    return round(100 * up_to_date / machines) if machines else None


def windows_system(product, release):
    # A Linux product (PRETTY_NAME) already carries its version
    if product and release and release in product:
        return product
    return " ".join(part for part in (product, release) if part)


def linux_label(product, release, distribution):
    """Name of a distribution without its version, e.g. « Debian GNU/Linux »
    from « Debian GNU/Linux 12 (bookworm) »."""
    if product and release and release in product:
        label = product.split(release, 1)[0].strip()
        if label:
            return label
    return product or distribution


def windows_datetime(value):
    return value.strftime("%Y-%m-%d %H:%M") if value else ""


def upgrade_target_label(system, product, release, target):
    """Target as the installed system is named: Linux « Debian GNU/Linux 13
    (trixie) » from « Debian GNU/Linux 12 (bookworm) », release 12, target
    « 13 (trixie) »; Windows unchanged."""
    target = target or ""
    if system != "linux" or not target or not product or not release:
        return target
    name, separator, _ = product.partition(f" {release}")
    return f"{name} {target}" if separator else target


# Packages named in the title of a Linux transaction, the others counted
LINUX_TRANSACTION_NAMES = 5


def linux_transaction(item):
    """History row of a transaction of a Linux report: {"kb": "", "date" (server
    local time), "title"}, title from the package names."""
    try:
        date = datetime.fromisoformat(str(item.get("date")).replace("Z", "+00:00"))
        date = date.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        date = ""
    packages = [p for p in item["packages"] if isinstance(p, dict) and p.get("name")]
    count = max(int(item.get("count") or 0), len(packages))
    if count == 1 and packages:
        title = f"{packages[0]['name']} {packages[0].get('version') or ''}".strip()
    else:
        title = ", ".join(p["name"] for p in packages[:LINUX_TRANSACTION_NAMES])
        if count > LINUX_TRANSACTION_NAMES:
            title += f" (+{count - LINUX_TRANSACTION_NAMES})"
    return {"kb": "", "date": date, "title": title}


# ERROR_DISK_FULL, then its HRESULT 0x80070070 unsigned and signed
DISK_FULL_CODES = (112, 2147942512, -2147024784)


def deploy_failure(result):
    """"disk_full" when the last non-zero codereturn of the last sequence of a
    deploy.result is a disk full code, None otherwise."""
    try:
        codes = [step.get("codereturn") for step in json.loads(result)["descriptorslist"][-1]]
    except (TypeError, ValueError, KeyError, IndexError, AttributeError):
        return None
    for code in reversed(codes):
        if str(code).lstrip("-").isdigit() and int(code):
            return "disk_full" if int(code) in DISK_FULL_CODES else None
    return None


class UpdatesDatabase(DatabaseHelper):
    """
    Singleton Class to query the update database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "updates"
        self.configfile = "updates.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )

        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        return True

    def initMappers(self):
        return

    # =====================================================================
    # updates FUNCTIONS
    # =====================================================================
    @DatabaseHelper._sessionm
    def get_replication_state(self, session):
        """State of the mirror replication, written by the substitute.

        state: ok, stale (last attempt failed, older copy kept),
        first_copy, failing (never copied), denied, not_configured.
        The module is open only when ok or stale."""
        try:
            row = session.execute(
                "SELECT last_attempt_at, last_success_at, last_error"
                " FROM updates.replication WHERE id = 1"
            ).first()
        except Exception as e:
            session.rollback()
            logger.error(f"Error in get_replication_state: {e}")
            row = None
        attempt, success, error = row if row else (None, None, None)
        if error in ("not_configured", "denied"):
            state = error
        elif success is None:
            state = "failing" if error else ("first_copy" if attempt else "not_configured")
        else:
            state = "stale" if error else "ok"
        return {
            "state": state,
            "cause": error or "",
            "last_success_at": success.strftime("%Y-%m-%d %H:%M:%S") if success else "",
        }

    # ######################## group update windows ########################
    @staticmethod
    def _entity_id_list(entity_ids):
        ids = []
        for entity_id in entity_ids or []:
            try:
                entity_id = int(entity_id)
            except (TypeError, ValueError):
                continue
            if entity_id not in ids:
                ids.append(entity_id)
        return ids

    @staticmethod
    def _like_pattern(value):
        escaped = value.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        return f"%{escaped}%"

    @staticmethod
    def _page_sql(start, limit, params):
        try:
            start = max(int(start), 0)
            limit = int(limit)
        except (TypeError, ValueError):
            start, limit = 0, -1
        if limit <= 0:
            return ""
        params["page_start"] = start
        params["page_limit"] = limit
        return " LIMIT :page_limit OFFSET :page_start"

    @DatabaseHelper._sessionm
    def get_linux_distributions(self, session, entity_ids):
        """[{distribution, label, machines}] of the Linux machines of entity_ids."""
        entity_ids = self._entity_id_list(entity_ids)
        if not entity_ids:
            return []
        sql = text(f"""
            SELECT mr.distribution, mr.product, mr.`release`
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            WHERE lgm.entities_id IN :entity_ids
              AND mr.os = 'linux' AND mr.distribution IS NOT NULL
            """).bindparams(bindparam("entity_ids", expanding=True))
        distributions = {}
        for row in session.execute(sql, {"entity_ids": entity_ids}):
            item = distributions.setdefault(row.distribution, {
                "distribution": row.distribution,
                "label": linux_label(row.product, row.release, row.distribution),
                "machines": 0,
            })
            item["machines"] += 1
        return sorted(distributions.values(), key=lambda item: item["label"].lower())

    @DatabaseHelper._sessionm
    def get_windows_summary(self, session, entity_ids, system="windows", distribution=""):
        summary = {"machines": 0, "evaluated": 0, "up_to_date": 0, "to_update": 0,
                   "critical": 0, "not_evaluated": 0, "reboot_pending": 0,
                   "no_report": 0, "conformity": None}
        entity_ids = self._entity_id_list(entity_ids)
        if not entity_ids:
            return summary
        sql = text(f"""
            SELECT COALESCE(SUM(NOT m.no_report), 0) AS machines,
                   COALESCE(SUM(m.no_report), 0) AS no_report,
                   COALESCE(SUM({MACHINE_COUNTED_SQL}), 0) AS evaluated,
                   COALESCE(SUM({MACHINE_UP_TO_DATE_SQL}), 0) AS up_to_date,
                   COALESCE(SUM({WINDOWS_MACHINE_CARDS['to_update']}), 0) AS to_update,
                   COALESCE(SUM({WINDOWS_MACHINE_CARDS['critical']}), 0) AS critical,
                   COALESCE(SUM({WINDOWS_MACHINE_CARDS['reboot_pending']}), 0) AS reboot_pending
            FROM ({machines_sql(system)}) AS m
            """).bindparams(bindparam("entity_ids", expanding=True))
        row = session.execute(sql, {"entity_ids": entity_ids, "stale_days": STALE_DAYS,
                                    "distribution": distribution}).first()
        summary["machines"] = int(row.machines or 0)
        summary["no_report"] = int(row.no_report or 0)
        summary["evaluated"] = int(row.evaluated)
        summary["up_to_date"] = int(row.up_to_date)
        summary["critical"] = int(row.critical)
        summary["reboot_pending"] = int(row.reboot_pending)
        summary["to_update"] = int(row.to_update)
        summary["not_evaluated"] = summary["machines"] - summary["evaluated"]
        summary["conformity"] = windows_conformity(summary["up_to_date"],
                                                   summary["machines"] + summary["no_report"])
        return summary

    @DatabaseHelper._sessionm
    def get_windows_entities(self, session, entity_ids):
        """Windows machines of each entity having some, with and without a report,
        and the products it tracks."""
        result = {"rows": []}
        entity_ids = self._entity_id_list(entity_ids)
        if not entity_ids:
            return result
        sql = text(f"""
            SELECT m.entity_id,
                   SUM(NOT m.no_report) AS machines,
                   SUM(m.no_report) AS no_report,
                   MAX(m.tracked_products) AS tracked_products
            FROM ({WINDOWS_ALL_MACHINES_SQL}) AS m
            GROUP BY m.entity_id
            """).bindparams(bindparam("entity_ids", expanding=True))
        for row in session.execute(sql, {"entity_ids": entity_ids, "stale_days": STALE_DAYS}):
            result["rows"].append({
                "entity_id": int(row.entity_id),
                "machines": int(row.machines or 0),
                "no_report": int(row.no_report or 0),
                "tracked_products": int(row.tracked_products or 0),
            })
        return result

    @DatabaseHelper._sessionm
    def get_upgrade_machines(self, session, entity_ids, system="windows"):
        """Version upgrade of each machine of the system ("windows", "linux", None
        for both) of entity_ids (machine_upgrades, computed by the substitute);
        machines without a computation, or known without any report, have state None."""
        entity_ids = self._entity_id_list(entity_ids)
        if not entity_ids:
            return []
        params = {"entity_ids": entity_ids, "stale_days": STALE_DAYS}
        where = ""
        if system is not None:
            where = "AND mr.os = :system"
            params["system"] = system
        machines = []
        for row in session.execute(text(f"""
                SELECT mr.jid, COALESCE(xm.hostname, mr.hostname) AS hostname,
                       mr.glpi_uuid, mr.product, mr.`release`, mr.build, mr.ubr,
                       mr.received_at,
                       lgm.entities_id AS entity_id, e.name AS entity_name,
                       mg.state, mg.target_release, mg.reason,
                       mg.run_error, mg.launched_at,
                       (mg.launched_at IS NOT NULL AND {UPGRADE_STEP_RUNNING_SQL}) AS step_running,
                       mr.windows11_eligible, mr.windows11_blockers, mr.windows11_source,
                       JSON_EXTRACT(mr.report, '$.windows11') AS windows11_facts,
                       COALESCE(xm.enabled, 0) AS online,
                       {MACHINE_REBOOT_SHOWN_SQL} AS reboot_pending,
                       {MACHINE_RESTART_REQUESTED_SQL} AS restart_requested,
                       {WINDOWS_EVALUATED_SQL} AS evaluated,
                       mr.os, mr.distribution, mr.kernel
                FROM machine_reports mr
                {WINDOWS_MACHINE_ENTITY_JOIN}
                LEFT JOIN machine_upgrades mg ON mg.jid = mr.jid
                {XM_LATEST_JOIN_SQL}
                WHERE lgm.entities_id IN :entity_ids {where}
                ORDER BY hostname, mr.jid
                """).bindparams(bindparam("entity_ids", expanding=True)), params):
            machines.append({
                "jid": row.jid,
                "hostname": row.hostname or "",
                "glpi_uuid": row.glpi_uuid or "",
                "product": row.product or "",
                "release": row.release or "",
                "build": f"{row.build}.{row.ubr}" if row.build else "",
                "received_at": row.received_at.strftime("%Y-%m-%d %H:%M") if row.received_at else "",
                "entity_id": int(row.entity_id),
                "entity_name": row.entity_name or "",
                "state": row.state,
                "target_release": upgrade_target_label(row.os, row.product, row.release,
                                                       row.target_release),
                "reason": row.reason or "",
                "run_error": row.run_error or "",
                "launched_at": row.launched_at.strftime("%Y-%m-%d %H:%M") if row.launched_at else "",
                "step_running": bool(row.step_running),
                "online": bool(row.online),
                "reboot_pending": bool(row.reboot_pending),
                "restart_requested": bool(row.restart_requested),
                "evaluated": bool(row.evaluated),
                "os": row.os,
                "distribution": row.distribution or "",
                "kernel": row.kernel or "",
                # Windows 11 requirements, for a Windows 10 machine with a target: once
                # on Windows 11 the next versions come by enablement or same-base media
                "windows11": windows11_requirements(
                    row.windows11_eligible, row.windows11_blockers, row.windows11_source,
                    row.windows11_facts) if (row.os == "windows"
                                             and row.state in ("ready", "not_eligible")
                                             and int(row.build or 0) < WINDOWS11_FIRST_BUILD) else None,
            })
        return machines + self._upgrade_no_report_machines(session, entity_ids, system)

    @staticmethod
    def _upgrade_no_report_machines(session, entity_ids, system):
        """Known machines of the system without any report, as get_upgrade_machines rows."""
        return [{
            "jid": row.jid,
            "hostname": row.hostname or "",
            "glpi_uuid": row.glpi_uuid or "",
            "product": "",
            "release": "",
            "build": "",
            "received_at": "",
            "entity_id": int(row.entity_id),
            "entity_name": row.entity_name or "",
            "state": None,
            "target_release": "",
            "reason": "",
            "run_error": "",
            "launched_at": "",
            "step_running": False,
            "online": bool(row.online),
            "reboot_pending": False,
            "restart_requested": False,
            "evaluated": False,
            "os": row.os,
            "distribution": "",
            "kernel": "",
            "windows11": None,
        } for row in session.execute(text(f"""
                SELECT {XM_BARE_JID_SQL} AS jid, xm.hostname,
                       {XM_GLPI_UUID_SQL} AS glpi_uuid,
                       lgm.entities_id AS entity_id, e.name AS entity_name,
                       COALESCE(xm.enabled, 0) AS online, {XM_OS_SQL} AS os
                {no_report_from_sql(NO_REPORT_PLATFORMS[system])}
                  AND lgm.entities_id IN :entity_ids
                """).bindparams(bindparam("entity_ids", expanding=True)),
                {"entity_ids": entity_ids})]

    @DatabaseHelper._sessionm
    def get_last_upgrade_deployments(self, session, glpi_uuids):
        """{glpi_uuid: deploy_log_fields of its latest upgrade step deployment,
        running or finished}; a machine that never had one is absent."""
        glpi_uuids = sorted({uuid for uuid in glpi_uuids or [] if uuid})
        if not glpi_uuids:
            return {}
        columns = ", ".join(f"d.{column}" for column in (*DEPLOY_LOG_COLUMNS.values(),
                                                         *DEPLOY_LOG_DATES))
        rows = session.execute(text(f"""
            SELECT {columns}
            FROM xmppmaster.deploy d
            JOIN (SELECT MAX(l.id) AS id
                    FROM xmppmaster.deploy l
                   WHERE l.inventoryuuid IN :glpi_uuids
                     AND {UPGRADE_STEP_TITLE_SQL.format(column="l.title")}
                   GROUP BY l.inventoryuuid) latest ON latest.id = d.id
            """).bindparams(bindparam("glpi_uuids", expanding=True)),
            {"glpi_uuids": glpi_uuids})
        return {row.inventoryuuid: deploy_log_fields(row) for row in rows}

    @DatabaseHelper._sessionm
    def launch_upgrades(self, session, entity_ids, glpi_uuids, login):
        """Launch the upgrade of the ready machines among glpi_uuids (entity_ids
        scoped); the substitute runs the steps. Returns the number launched."""
        entity_ids = self._entity_id_list(entity_ids)
        glpi_uuids = [str(uuid) for uuid in glpi_uuids or [] if uuid]
        if not entity_ids or not glpi_uuids:
            return 0
        result = session.execute(text("""
            UPDATE machine_upgrades mg
            JOIN machine_reports mr ON mr.jid = mg.jid
            JOIN xmppmaster.local_glpi_machines lgm
              ON mr.glpi_uuid REGEXP '^UUID[0-9]+$'
             AND lgm.id = CAST(SUBSTRING(mr.glpi_uuid, 5) AS UNSIGNED)
             AND lgm.is_deleted = 0 AND lgm.is_template = 0
            SET mg.launched_at = NOW(), mg.launched_by = :login
            WHERE lgm.entities_id IN :entity_ids AND mr.glpi_uuid IN :glpi_uuids
              AND mg.state = 'ready' AND mg.launched_at IS NULL
            """).bindparams(bindparam("entity_ids", expanding=True),
                            bindparam("glpi_uuids", expanding=True)),
            {"entity_ids": entity_ids, "glpi_uuids": glpi_uuids, "login": login})
        session.commit()
        return int(result.rowcount or 0)

    @DatabaseHelper._sessionm
    def get_upgrade_to_cancel(self, session, jid):
        """{"entity_id", "os", "steps", "launched_at", "step_running", "evaluated",
        "reboot_pending", "release_started"} of the machine jid, None when it cannot be scoped. release_started: a release
        step went out since the launch, or an earlier one stopped and was not resumed."""
        row = session.execute(text(f"""
            SELECT lgm.entities_id AS entity_id, mr.os, mg.steps, mg.launched_at,
                   {WINDOWS_EVALUATED_SQL} AS evaluated, mr.reboot_pending,
                   {UPGRADE_STEP_RUNNING_SQL} AS step_running,
                   ({RELEASE_TO_RESUME_SQL}
                    OR EXISTS (SELECT 1 FROM xmppmaster.deploy d
                                WHERE d.inventoryuuid = mr.glpi_uuid
                                  AND {UPGRADE_STEP_TITLE_SQL.format(column="d.title")}
                                  AND d.start >= mg.launched_at)) AS release_started
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            LEFT JOIN machine_upgrades mg ON mg.jid = mr.jid
            WHERE mr.jid = :jid
            """), {"jid": jid, "stale_days": STALE_DAYS}).first()
        if row is None:
            return None
        return {"entity_id": int(row.entity_id),
                "os": row.os,
                "steps": row.steps.split(",") if row.steps else [],
                "launched_at": row.launched_at,
                "evaluated": bool(row.evaluated),
                "reboot_pending": bool(row.reboot_pending),
                "step_running": bool(row.step_running),
                "release_started": bool(row.release_started)}

    @DatabaseHelper._sessionm
    def cancel_upgrade(self, session, jid, error):
        """Stop following the launched upgrade of jid; state and steps stay as
        computed. Returns the number of rows changed."""
        result = session.execute(text("""
            UPDATE machine_upgrades SET launched_at = NULL, run_error = :error
            WHERE jid = :jid AND launched_at IS NOT NULL
            """), {"jid": jid, "error": error})
        session.commit()
        return int(result.rowcount or 0)

    @DatabaseHelper._sessionm
    def set_restart_requested(self, session, jid):
        session.execute(text(
            "UPDATE machine_reports SET restart_requested_at = NOW() WHERE jid = :jid"),
            {"jid": jid})
        session.commit()

    @DatabaseHelper._sessionm
    def get_windows_machines(self, session, entity_ids, start=0, limit=-1, filter="",
                             system="windows", distribution="", only=""):
        """only: key of WINDOWS_MACHINE_CARDS, empty for all; unknown: no machine."""
        result = {"total": 0, "rows": []}
        entity_ids = self._entity_id_list(entity_ids)
        if not entity_ids or (only and only not in WINDOWS_MACHINE_CARDS):
            return result
        params = {"entity_ids": entity_ids, "stale_days": STALE_DAYS,
                  "distribution": distribution}
        conditions = []
        filter = str(filter or "").strip()
        if filter:
            conditions.append("LOWER(m.hostname) LIKE LOWER(:filter) ESCAPE '!'")
            params["filter"] = self._like_pattern(filter)
        if only:
            conditions.append(f"({WINDOWS_MACHINE_CARDS[only]})")
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        page = self._page_sql(start, limit, params)
        sql = text(f"""
            SELECT m.*, COUNT(*) OVER () AS total
            FROM ({machines_sql(system)}) AS m
            {where}
            ORDER BY m.critical DESC, m.missing DESC, m.hostname, m.jid
            {page}
            """).bindparams(bindparam("entity_ids", expanding=True))
        for row in session.execute(sql, params):
            result["total"] = int(row.total)
            result["rows"].append({
                "jid": row.jid,
                "hostname": row.hostname or "",
                "online": bool(row.online),
                "glpi_uuid": row.glpi_uuid,
                "entity_id": int(row.entity_id),
                "entity_name": row.entity_name or "",
                "system": windows_system(row.product, row.release),
                "missing": int(row.missing),
                "critical": int(row.critical),
                "received_at": windows_datetime(row.received_at),
                "evaluated": bool(row.evaluated),
                "unsupported": bool(row.unsupported),
                "untracked_version": bool(row.untracked_version),
                "reboot_pending": bool(row.reboot_pending),
                "restart_requested": bool(row.restart_requested),
                "search_failed": bool(row.search_failed),
                "updating": bool(row.updating),
                "no_report": bool(row.no_report),
            })
        if not result["rows"] and page:
            result["total"] = self.get_windows_machines(
                entity_ids, 0, -1, filter, system, distribution, only)["total"]
        if system == "linux" and result["rows"]:
            busy = self._busy_machines(session, [row["glpi_uuid"] for row in result["rows"]])
            approved = self._linux_approved_packages(session, [row["jid"] for row in result["rows"]])
            for row in result["rows"]:
                row["approved"] = approved.get(row["jid"], 0)
                row["running"] = row["glpi_uuid"] in busy
        return result

    @staticmethod
    def _linux_approved_packages(session, jids):
        """{jid: number of its missing packages approved by the Linux rules of its
        entity}; a machine without any is absent."""
        return {row.jid: int(row.approved) for row in session.execute(text(f"""
            SELECT mu.jid, COUNT(DISTINCT mu.package) AS approved
            {LINUX_APPROVED_PACKAGES_SQL}
              AND mu.jid IN :jids
            GROUP BY mu.jid
            """).bindparams(bindparam("jids", expanding=True)), {"jids": jids})}

    @staticmethod
    def _busy_machines(session, glpi_uuids):
        """{glpi uuid: held by something else than an upgrade step} of the glpi_uuids
        held by a deployment, with or without a report."""
        glpi_uuids = sorted({uuid for uuid in glpi_uuids if uuid})
        if not glpi_uuids:
            return {}
        return {row.glpi_uuid: bool(row.updating) for row in session.execute(text(f"""
            SELECT mr.glpi_uuid, {NOT_UPGRADE_STEP_RUNNING_SQL} AS updating
            FROM (SELECT glpi_uuid FROM machine_reports WHERE glpi_uuid IN :uuids
                  UNION
                  SELECT {XM_GLPI_UUID_SQL} FROM xmppmaster.machines xm
                   WHERE xm.uuid_inventorymachine IN :uuids) mr
            WHERE {MACHINE_BUSY_SQL}
            """).bindparams(bindparam("uuids", expanding=True)), {"uuids": glpi_uuids})}

    @DatabaseHelper._sessionm
    def get_windows_installed(self, session, jid):
        """Updates the machine reports as installed (Windows Update history and
        hotfixes), latest first: [{"kb", "date", "title"}]; title from the catalog,
        empty when none can be trusted for this machine."""
        row = session.execute(text("SELECT report FROM machine_reports WHERE jid = :jid"),
                              {"jid": jid}).first()
        try:
            report = json.loads(row.report or "{}") if row else {}
        except ValueError:
            report = {}
        installed = report.get("installed") if isinstance(report, dict) else None
        if not isinstance(installed, list):
            return []
        if report.get("os") == "linux":
            return [linux_transaction(item) for item in installed
                    if isinstance(item, dict) and isinstance(item.get("packages"), list)]
        items = [item for item in installed
                 if isinstance(item, dict) and str(item.get("kb") or "").isdigit()]
        titles = {}
        kbs = sorted({str(item["kb"]) for item in items})
        if kbs:
            for kb, title in session.execute(
                    text(WINDOWS_INSTALLED_TITLES_SQL).bindparams(
                        bindparam("kbs", expanding=True)), {"jid": jid, "kbs": kbs}):
                titles[str(kb)] = title or ""
        rows = [{"kb": str(item["kb"]), "date": str(item.get("date") or ""),
                 "title": titles.get(str(item["kb"]), "")} for item in items]
        rows.sort(key=lambda r: r["date"], reverse=True)
        return rows

    @DatabaseHelper._sessionm
    def get_deployment_ends(self, session, sessionids):
        """{sessionid: date of its last log line, "YYYY-MM-DD HH:MM:SS"}."""
        if not sessionids:
            return {}
        return {row.sessionname: str(row.ended) for row in session.execute(text("""
            SELECT sessionname, MAX(date) AS ended FROM xmppmaster.logs
            WHERE sessionname IN :sessionids GROUP BY sessionname
            """).bindparams(bindparam("sessionids", expanding=True)),
            {"sessionids": sorted(set(sessionids))})}

    @DatabaseHelper._sessionm
    def get_deployment_failures(self, session, sessionids):
        """{sessionid: deploy_failure of its result}, only those with a known cause."""
        if not sessionids:
            return {}
        failures = {row.sessionid: deploy_failure(row.result) for row in session.execute(text("""
            SELECT sessionid, result FROM xmppmaster.deploy WHERE sessionid IN :sessionids
            """).bindparams(bindparam("sessionids", expanding=True)),
            {"sessionids": sorted(set(sessionids))})}
        return {sessionid: failure for sessionid, failure in failures.items() if failure}

    @DatabaseHelper._sessionm
    def get_windows_machine(self, session, jid):
        """Machine report, or None when the jid is unknown or cannot be scoped.

        A known machine without any report gets a minimal sheet with
        no_report True.

        signals: "reboot_pending" (Windows waits for a restart), "unsupported"
        (Windows 10 without ESU: no security update any more),
        "untracked_version" (the machine's version is not tracked by its
        entity), "search_failed" (last search failed, blocked, timed out or locked).

        running: a deployment of any package holds the machine, or its command waits.

        updates[i].deployed_pending_report: installed by Medulla since the last report.
        """
        row = session.execute(text(f"""
            SELECT mr.jid, COALESCE(xm.hostname, mr.hostname) AS hostname,
                   COALESCE(xm.enabled, 0) AS online,
                   mr.glpi_uuid, mr.product, mr.`release`, mr.build, mr.ubr, mr.language, mr.received_at,
                   COALESCE(ep.tracked_products, 0) AS tracked_products,
                   {WINDOWS_EVALUATED_SQL} AS evaluated,
                   {WINDOWS_UNSUPPORTED_SQL} AS unsupported,
                   {WINDOWS_UNTRACKED_VERSION_SQL} AS untracked_version,
                   {WINDOWS_MACHINE_RELEASE_SQL} AS release_name,
                   mr.search_status, mr.wsus_server, mr.automatic_updates, mr.reboot_pending,
                   mr.service_state, mr.report, lgm.entities_id AS entity_id,
                   mr.os, mr.distribution, mr.kernel,
                   {MACHINE_BUSY_SQL} AS running,
                   {MACHINE_RESTART_REQUESTED_SQL} AS restart_requested
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            {XM_LATEST_JOIN_SQL}
            WHERE mr.jid = :jid
            """), {"jid": jid, "stale_days": STALE_DAYS}).first()
        if row is None:
            return self._windows_no_report_machine(session, jid)

        signals = []
        if row.reboot_pending:
            signals.append("reboot_pending")
        if row.unsupported:
            signals.append("unsupported")
        if row.untracked_version:
            signals.append("untracked_version")
        if row.search_status in WINDOWS_SEARCH_FAILURES:
            signals.append("search_failed")

        try:
            report = json.loads(row.report or "{}") or {}
        except ValueError:
            report = {}
        if not isinstance(report, dict):
            report = {}

        paused_until = None
        tool = None
        policy = report.get("policy")
        if isinstance(policy, dict):
            paused_until = policy.get("paused_until") or None
            # Linux: the automatic update tool, e.g. unattended-upgrades
            tool = policy.get("tool") or None
        windows_update = {
            "tool": tool,
            "automatic_updates": row.automatic_updates,
            "service_state": row.service_state,
            "wsus_server": row.wsus_server,
            "paused_until": paused_until,
        }

        build = ""
        if row.build is not None:
            build = str(row.build) if row.ubr is None else f"{row.build}.{row.ubr}"

        rules_source = self._effective_source(session, "effective_rules", row.entity_id)
        linux_rules_source = self._effective_source(session, "effective_rules", row.entity_id,
                                                    "linux")
        updates = []
        for update in session.execute(text(f"""
                SELECT mu.update_id,
                       COALESCE(u.kb, mu.kb) AS kb,
                       COALESCE(u.title, mu.title) AS title,
                       COALESCE(u.classification, mu.classification) AS classification,
                       COALESCE(u.severity, mu.severity) AS severity,
                       mu.package AS package_name, mu.installed_version,
                       mu.available_version, mu.offer,
                       {EXPLOITED_KB_SQL} AS exploited,
                       {MACHINE_CRITICAL_UPDATE_SQL} AS critical,
                       {DEPLOYED_PENDING_REPORT_TEMPLATE.format(kb="COALESCE(u.kb, mu.kb)")} AS deployed_pending_report,
                       p.state AS package_state, p.error AS package_error,
                       {WINDOWS_UPDATE_SIZE_TEMPLATE.format(update_id="mu.update_id")} AS size,
                       CASE WHEN u.id IS NOT NULL
                            THEN mu.offer <> 'esu' AND {APPROVAL_STATUS_SQL} = 'approved'
                            ELSE mu.package IS NOT NULL AND {LINUX_RULE_MATCH_SQL}
                       END AS approved
                FROM machine_updates mu
                JOIN machine_reports mr ON mr.jid = mu.jid
                LEFT JOIN updates u ON u.id = mu.update_id
                LEFT JOIN effective_approvals a
                  ON a.entity_id = :entity_id AND a.update_id = u.id
                LEFT JOIN update_packages up ON up.update_id = mu.update_id
                LEFT JOIN packages p ON p.uuid = up.package_uuid
                WHERE mu.jid = :jid AND {KNOWN_OFFER_SQL}
                ORDER BY {windows_offer_rank_sql("mu.offer")}, exploited DESC, critical DESC,
                         {windows_severity_rank_sql("COALESCE(u.severity, mu.severity)")},
                         title
                """), {"jid": row.jid, "entity_id": int(row.entity_id),
                       "rules_source": rules_source,
                       "linux_rules_source": linux_rules_source}):
            package = ""
            if update.package_state is not None:
                package = {"state": update.package_state,
                           "error": update.package_error or ""}
            updates.append({
                "update_id": "" if update.update_id is None else int(update.update_id),
                "approved": bool(update.approved),
                "kb": update.kb,
                "title": update.title,
                "classification": update.classification,
                "severity": update.severity,
                "exploited": bool(update.exploited),
                "critical": bool(update.critical),
                "package": package,
                "size": None if update.size is None else int(update.size),
                "package_name": update.package_name or "",
                "installed_version": update.installed_version or "",
                "available_version": update.available_version or "",
                "offer": update.offer,
                "deployed_pending_report": bool(update.deployed_pending_report),
            })

        return {
            "jid": row.jid,
            "hostname": row.hostname or "",
            "online": bool(row.online),
            "glpi_uuid": row.glpi_uuid,
            "entity_id": int(row.entity_id),
            "system": windows_system(row.product, row.release),
            "release": row.release_name or "",
            "build": build,
            "language": row.language or "",
            "received_at": windows_datetime(row.received_at),
            "evaluated": bool(row.evaluated),
            "tracked_products": int(row.tracked_products),
            "signals": signals,
            "windows_update": windows_update,
            "updates": updates,
            "no_report": False,
            "running": bool(row.running),
            "reboot_pending": bool(row.reboot_pending),
            "restart_requested": bool(row.restart_requested),
            "os": row.os,
            "distribution": row.distribution or "",
            "kernel": row.kernel or "",
        }

    @staticmethod
    def _windows_no_report_machine(session, jid):
        row = session.execute(text(f"""
            SELECT {XM_BARE_JID_SQL} AS jid, xm.hostname, xm.enabled AS online,
                   xm.uuid_inventorymachine AS glpi_uuid,
                   lgm.entities_id AS entity_id,
                   COALESCE(ep.tracked_products, 0) AS tracked_products,
                   {XM_OS_SQL} AS os
            {no_report_from_sql(XM_ANY_PLATFORM_SQL)}
              AND SUBSTRING_INDEX(xm.jid, '/', 1) = :jid
            """), {"jid": jid}).first()
        if row is None:
            return None
        return {
            "jid": row.jid,
            "hostname": row.hostname or "",
            "online": bool(row.online),
            "glpi_uuid": row.glpi_uuid,
            "entity_id": int(row.entity_id),
            "system": "",
            "release": "",
            "build": "",
            "language": "",
            "received_at": "",
            "evaluated": False,
            "tracked_products": int(row.tracked_products),
            "signals": [],
            "windows_update": {"tool": None, "automatic_updates": None, "service_state": None,
                               "wsus_server": None, "paused_until": None},
            "updates": [],
            "no_report": True,
            "running": bool(UpdatesDatabase._busy_machines(session, [row.glpi_uuid])),
            "reboot_pending": False,
            "restart_requested": False,
            "os": row.os,
            "distribution": "",
            "kernel": "",
        }

    # Views giving, per entity, the entity whose setting applies
    EFFECTIVE_SOURCE_VIEWS = ("effective_products", "effective_linux_releases", "effective_rules",
                              "effective_settings")

    @classmethod
    def _effective_source(cls, session, view, entity_id, system="windows"):
        """Entity whose setting applies to entity_id, None when none has one.
        Approval rules are inherited per system."""
        if view not in cls.EFFECTIVE_SOURCE_VIEWS:
            raise ValueError(view)
        where = " AND os = :os" if view == "effective_rules" else ""
        source = session.execute(text(
            f"SELECT source_id FROM {view} WHERE entity_id = :entity_id{where}"),
            {"entity_id": int(entity_id), "os": system}).scalar()
        return None if source is None else int(source)

    @staticmethod
    def _entity_lineage(session, entity_id):
        """entity_id then its ancestors, nearest first; [] when unknown to GLPI."""
        return [int(row.ancestor_id) for row in session.execute(text("""
            SELECT ancestor_id FROM entity_ancestors
            WHERE entity_id = :entity_id ORDER BY depth
            """), {"entity_id": int(entity_id)})]

    @staticmethod
    def _entity_refs(session, entity_ids):
        """{id: {"id", "name"}}, name as shown in the entity selector."""
        entity_ids = sorted({int(entity_id) for entity_id in entity_ids})
        refs = {entity_id: {"id": entity_id, "name": ""} for entity_id in entity_ids}
        if entity_ids:
            for row in session.execute(text("""
                    SELECT id, completename FROM xmppmaster.local_glpi_entities
                    WHERE id IN :entity_ids
                    """).bindparams(bindparam("entity_ids", expanding=True)),
                    {"entity_ids": entity_ids}):
                refs[int(row.id)]["name"] = row.completename or ""
        return refs

    def _inheritance(self, session, entity_id, source_id):
        """{"parent", "inherited_from"}: {"id", "name"} or None.

        The root always has its own setting. A sub-entity without source
        inherits the root's empty one."""
        entity_id = int(entity_id)
        lineage = self._entity_lineage(session, entity_id)
        parent_id = lineage[1] if len(lineage) > 1 else None
        inherited_id = None
        if parent_id is not None and source_id != entity_id:
            inherited_id = lineage[-1] if source_id is None else source_id
        refs = self._entity_refs(session, [entity for entity in (parent_id, inherited_id)
                                           if entity is not None])
        return {"parent": refs.get(parent_id), "inherited_from": refs.get(inherited_id)}

    @DatabaseHelper._sessionm
    def is_root_entity(self, session, entity_id):
        """True when entity_id is known to GLPI without a parent."""
        return len(self._entity_lineage(session, entity_id)) == 1

    def _sub_entity(self, session, entity_id):
        """True when entity_id has a parent, so it can return to inheritance."""
        return len(self._entity_lineage(session, entity_id)) > 1

    @staticmethod
    def _set_override(session, entity_id, setting):
        """The entity has its own setting, even empty."""
        session.execute(text("""
            INSERT IGNORE INTO entity_overrides (entity_id, setting)
            VALUES (:entity_id, :setting)
            """), {"entity_id": entity_id, "setting": setting})

    def _reset_tracking(self, session, entity_id, tables, setting):
        """Drop the entity's own selection: it inherits again. Refused for the root."""
        entity_id = int(entity_id)
        try:
            if not self._sub_entity(session, entity_id):
                return False
            params = {"entity_id": entity_id, "setting": setting}
            for table in tables:
                session.execute(text(f"DELETE FROM {table} WHERE entity_id = :entity_id"),
                                params)
            session.execute(text("""
                DELETE FROM entity_overrides
                WHERE entity_id = :entity_id AND setting = :setting
                """), params)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"reset of {setting}: {e}")
            return False

    @DatabaseHelper._sessionm
    def get_windows_products(self, session, entity_id):
        """Effective selection: the entity's own, or its nearest ancestor's."""
        entity_id = int(entity_id)
        source_id = self._effective_source(session, "effective_products", entity_id)
        releases = {}
        # Version names (1903, 21H2, 26H1, 26H2) sort in release order; builds do not:
        # 26H1 (28000) came out before 26H2 (26300)
        for row in session.execute(text("""
                SELECT r.product_id, r.name,
                       MAX(er.entity_id IS NOT NULL) AS tracked
                FROM releases r
                LEFT JOIN entity_releases er
                  ON er.entity_id = :source_id AND er.product_id = r.product_id
                 AND er.release_name = r.name
                WHERE r.name IS NOT NULL
                GROUP BY r.product_id, r.name
                ORDER BY r.product_id, r.name
                """), {"source_id": source_id}):
            releases.setdefault(int(row.product_id), []).append({
                "name": row.name,
                "tracked": bool(row.tracked),
            })
        rows = []
        for row in session.execute(text("""
                SELECT p.id, COALESCE(p.display_name, p.name) AS name, p.display_group,
                       p.supported, ep.entity_id IS NOT NULL AS tracked
                FROM products p
                LEFT JOIN entity_products ep
                  ON ep.product_id = p.id AND ep.entity_id = :source_id
                ORDER BY p.display_group IS NULL, p.position, p.name, p.id
                """), {"source_id": source_id}):
            rows.append({
                "id": int(row.id),
                "name": row.name,
                "group": row.display_group or "",
                "supported": bool(row.supported),
                "tracked": bool(row.tracked),
                "releases": releases.get(int(row.id), []),
            })
        result = {"rows": rows}
        result.update(self._inheritance(session, entity_id, source_id))
        return result

    @DatabaseHelper._sessionm
    def set_windows_products(self, session, entity_id, selections):
        """Replace the versions tracked by an entity.

        selections: [{"product_id": int, "release": str}]; release "" tracks a
        product without named release. Entries absent from the catalog are ignored.
        entity_products keeps a row per product tracked at all. The entity
        gets its own setting, even empty.
        """
        entity_id = int(entity_id)
        try:
            catalog = {}
            for row in session.execute(text("""
                    SELECT p.id, r.name
                    FROM products p
                    LEFT JOIN releases r ON r.product_id = p.id AND r.name IS NOT NULL
                    """)):
                names = catalog.setdefault(int(row.id), {})
                if row.name is not None:
                    names[row.name.lower()] = row.name

            product_ids = set()
            release_rows = set()
            for selection in selections or []:
                if not isinstance(selection, dict):
                    continue
                product_id = selection.get("product_id")
                if isinstance(product_id, bool):
                    continue
                try:
                    product_id = int(product_id)
                except (TypeError, ValueError):
                    continue
                names = catalog.get(product_id)
                if names is None:
                    continue
                release = str(selection.get("release") or "").strip()
                if not release:
                    if not names:
                        product_ids.add(product_id)
                    continue
                name = names.get(release.lower())
                if name is not None:
                    product_ids.add(product_id)
                    release_rows.add((product_id, name))

            params = {"entity_id": entity_id}
            session.execute(text("DELETE FROM entity_releases WHERE entity_id = :entity_id"),
                            params)
            session.execute(text("DELETE FROM entity_products WHERE entity_id = :entity_id"),
                            params)
            if product_ids:
                session.execute(text("""
                    INSERT INTO entity_products (entity_id, product_id)
                    VALUES (:entity_id, :product_id)
                    """), [{"entity_id": entity_id, "product_id": product_id}
                           for product_id in sorted(product_ids)])
            if release_rows:
                session.execute(text("""
                    INSERT INTO entity_releases (entity_id, product_id, release_name)
                    VALUES (:entity_id, :product_id, :release_name)
                    """), [{"entity_id": entity_id, "product_id": product_id,
                            "release_name": name}
                           for product_id, name in sorted(release_rows)])
            self._set_override(session, entity_id, "products")
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"set_windows_products: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_windows_products(self, session, entity_id):
        """Drop the entity's own selection: it inherits again. Refused for the root."""
        return self._reset_tracking(session, entity_id, ("entity_releases", "entity_products"),
                                    "products")

    @staticmethod
    def _linux_release_rows(session, entity_id, source_id, allowed_ids):
        """linux_release_rows of the machines at or below entity_id; allowed_ids:
        entities the user sees, None when not restricted."""
        allowed = "" if allowed_ids is None else "AND lgm.entities_id IN :allowed_ids"
        sql = text(f"""
            SELECT mr.distribution, JSON_EXTRACT(mr.report, '$.upgrade') AS upgrade,
                   JSON_EXTRACT(mr.report, '$.system') AS system_info
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            WHERE lgm.entities_id IN {ENTITY_SUBTREE_SQL} {allowed}
              AND mr.os = 'linux' AND mr.distribution IS NOT NULL
            """)
        params = {"entity_id": entity_id}
        if allowed_ids is not None:
            sql = sql.bindparams(bindparam("allowed_ids", expanding=True))
            params["allowed_ids"] = [int(allowed_id) for allowed_id in allowed_ids]
        reports = [(row.distribution, row.upgrade, row.system_info)
                   for row in session.execute(sql, params)]
        tracked = [(row.distribution, row.release_name) for row in session.execute(text("""
            SELECT distribution, release_name FROM entity_linux_releases
            WHERE entity_id = :source_id
            """), {"source_id": source_id})]
        catalog = []
        if reports:
            catalog = [(row.distribution, row.release_name, row.codename)
                       for row in session.execute(text("""
                SELECT distribution, release_name, codename FROM linux_releases
                WHERE distribution IN :distributions
                """).bindparams(bindparam("distributions", expanding=True)),
                {"distributions": sorted({report[0] for report in reports})})]
        return linux_release_rows(reports, tracked, catalog)

    @DatabaseHelper._sessionm
    def get_linux_releases(self, session, entity_id, allowed_ids=None):
        """Linux versions to choose from for the entity, with the effective selection."""
        entity_id = int(entity_id)
        source_id = self._effective_source(session, "effective_linux_releases", entity_id)
        result = {"rows": self._linux_release_rows(session, entity_id, source_id, allowed_ids)}
        result.update(self._inheritance(session, entity_id, source_id))
        return result

    @DatabaseHelper._sessionm
    def set_linux_releases(self, session, entity_id, selections, allowed_ids=None):
        """Replace the Linux versions tracked by an entity.

        selections: [{"distribution": str, "release": str}]; entries get_linux_releases
        does not offer are ignored. The entity gets its own setting, even empty."""
        entity_id = int(entity_id)
        try:
            source_id = self._effective_source(session, "effective_linux_releases", entity_id)
            offered = {linux_release_key(row["distribution"], row["release"]): row
                       for row in self._linux_release_rows(session, entity_id, source_id,
                                                           allowed_ids)}
            chosen = {}
            for selection in selections or []:
                if isinstance(selection, dict):
                    key = linux_release_key(selection.get("distribution"), selection.get("release"))
                    if key in offered:
                        chosen[key] = offered[key]
            session.execute(text("DELETE FROM entity_linux_releases WHERE entity_id = :entity_id"),
                            {"entity_id": entity_id})
            if chosen:
                session.execute(text("""
                    INSERT INTO entity_linux_releases (entity_id, distribution, release_name)
                    VALUES (:entity_id, :distribution, :release_name)
                    """), [{"entity_id": entity_id, "distribution": row["distribution"],
                            "release_name": row["release"]}
                           for row in chosen.values()])
            self._set_override(session, entity_id, "linux_releases")
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"set_linux_releases: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_linux_releases(self, session, entity_id):
        """Drop the entity's own Linux versions: it inherits again. Refused for the root."""
        return self._reset_tracking(session, entity_id, ("entity_linux_releases",),
                                    "linux_releases")

    @DatabaseHelper._sessionm
    def get_windows_approvals(self, session, entity_id, status="pending", start=0,
                              limit=-1, filter="", system="windows"):
        """Effective status per update: the entity's decision, else its nearest
        ancestor's, else its effective rules. Per row "inherited_from" when the
        decision comes from an ancestor.

        Linux: the packages approved ("approved") or not ("pending") by the
        effective rules, no decision per package; "rules_from" is the entity
        whose rules apply."""
        result = {"total": 0, "rows": [],
                  "counts": {status: 0 for status in WINDOWS_APPROVAL_STATUSES},
                  "parent": None}
        if status not in WINDOWS_APPROVAL_STATUSES:
            return result
        entity_id = int(entity_id)
        result["parent"] = self._inheritance(session, entity_id, entity_id)["parent"]
        if system == "linux":
            return self._linux_approvals(session, entity_id, status, start, limit, filter,
                                         result)
        rules_source = self._effective_source(session, "effective_rules", entity_id)
        for row in session.execute(text(f"""
                SELECT s.status, COUNT(*) AS updates
                FROM ({WINDOWS_APPROVAL_UPDATES_SQL}) AS s
                GROUP BY s.status
                """), {"entity_id": entity_id, "rules_source": rules_source}):
            result["counts"][row.status] = int(row.updates)

        params = {"entity_id": entity_id, "status": status,
                  "rules_source": rules_source}
        where = ""
        filter = str(filter or "").strip()
        if filter:
            where = """AND (LOWER(s.title) LIKE LOWER(:filter) ESCAPE '!'
                            OR LOWER(CONCAT('KB', s.kb)) LIKE LOWER(:filter) ESCAPE '!')"""
            params["filter"] = self._like_pattern(filter)
        page = self._page_sql(start, limit, params)
        sql = text(f"""
            SELECT s.*, p.state AS package_state, p.error AS package_error,
                   {WINDOWS_UPDATE_SIZE_TEMPLATE.format(update_id="s.update_id")} AS size,
                   COUNT(*) OVER () AS total
            FROM ({WINDOWS_APPROVAL_UPDATES_SQL}) AS s
            LEFT JOIN update_packages up ON up.update_id = s.update_id
            LEFT JOIN packages p ON p.uuid = up.package_uuid
            WHERE s.status = :status
            {where}
            ORDER BY {windows_offer_rank_sql("s.offer")}, s.exploited DESC, s.critical DESC,
                     {windows_severity_rank_sql("s.severity")},
                     s.machines DESC, s.title, s.update_id
            {page}
            """)
        rows = session.execute(sql, params).fetchall()
        refs = self._entity_refs(session, [row.decided_in for row in rows
                                           if row.decided_in is not None
                                           and int(row.decided_in) != entity_id])
        for row in rows:
            result["total"] = int(row.total)
            decided_in = None if row.decided_in is None else int(row.decided_in)
            result["rows"].append({
                "update_id": int(row.update_id),
                "inherited_from": refs.get(decided_in),
                "kb": row.kb,
                "title": row.title,
                "classification": row.classification,
                "severity": row.severity,
                "offer": row.offer,
                "exploited": bool(row.exploited),
                "critical": bool(row.critical),
                "machines": int(row.machines),
                "own_machines": int(row.own_machines),
                "by_rule": bool(row.by_rule),
                "decided_by": row.decided_by or "",
                "decided_at": windows_datetime(row.decided_at),
                "package_state": row.package_state or "",
                "package_error": row.package_error or "",
                "size": None if row.size is None else int(row.size),
            })
        if not result["rows"] and page:
            result["total"] = self.get_windows_approvals(
                entity_id, status, 0, -1, filter)["total"]
        return result

    def _linux_approvals(self, session, entity_id, status, start, limit, filter, result):
        rules_source = self._effective_source(session, "effective_rules", entity_id, "linux")
        result["rules_from"] = (self._entity_refs(session, [rules_source]).get(rules_source)
                                if rules_source is not None else None)
        params = {"entity_id": entity_id, "linux_rules_source": rules_source}
        for row in session.execute(text(f"""
                SELECT s.approved, COUNT(*) AS packages
                FROM ({LINUX_APPROVAL_PACKAGES_SQL}) AS s
                GROUP BY s.approved
                """), params):
            result["counts"]["approved" if row.approved else "pending"] = int(row.packages)

        if status == "declined":
            return result
        params["approved"] = status == "approved"
        where = "WHERE s.approved = :approved"
        filter = str(filter or "").strip()
        if filter:
            where += " AND LOWER(s.package) LIKE LOWER(:filter) ESCAPE '!'"
            params["filter"] = self._like_pattern(filter)
        result["total"] = int(session.execute(text(
            f"SELECT COUNT(*) FROM ({LINUX_APPROVAL_PACKAGES_SQL}) AS s {where}"),
            params).scalar())
        page = self._page_sql(start, limit, params)
        for row in session.execute(text(f"""
                SELECT s.* FROM ({LINUX_APPROVAL_PACKAGES_SQL}) AS s
                {where}
                ORDER BY s.machines DESC, s.package
                {page}
                """), params):
            result["rows"].append({
                "package": row.package,
                "classification": row.classification or "",
                "severity": row.severity or "",
                "machines": int(row.machines),
                "approved": bool(row.approved),
            })
        return result

    @staticmethod
    def _windows_update_package(session, update_id):
        return session.execute(text(f"""
            {WINDOWS_UPDATE_PACKAGE_SQL}
            WHERE u.id = :update_id
            """), {"update_id": update_id}).first()

    @staticmethod
    def _windows_deploy_machines(session, update_id, package_uuid, entity_ids,
                                 glpi_uuids=None, jid=None, installed_kb=None,
                                 linux=False):
        """Machines of entity_ids (and glpi_uuids, jid if given) missing the update,
        reporting installed_kb when given (uninstallation), or with a Linux
        package to upgrade (linux). "offer": of the update on the machine, empty
        for an uninstallation or Linux; "approved": for this machine, a rule only
        covers the offer main and esu never is."""
        params = {"update_id": update_id, "entity_ids": entity_ids,
                  "package_uuid": package_uuid or ""}
        offer = "NULL"
        deployed = "0"
        if linux:
            target = ("SELECT 1 FROM machine_updates mu"
                      " WHERE mu.jid = mr.jid AND mu.package IS NOT NULL")
        elif installed_kb is None:
            target = ("SELECT 1 FROM machine_updates mu"
                      f" WHERE mu.jid = mr.jid AND mu.update_id = :update_id AND {KNOWN_OFFER_SQL}")
            offer = ("(SELECT mu.offer FROM machine_updates mu"
                     f" WHERE mu.jid = mr.jid AND mu.update_id = :update_id AND {KNOWN_OFFER_SQL}"
                     " LIMIT 1)")
            deployed = DEPLOYED_PENDING_REPORT_TEMPLATE.format(
                kb="(SELECT u.kb FROM updates u WHERE u.id = :update_id)")
        else:
            target = "SELECT 1 FROM machine_installed_kbs mik WHERE mik.jid = mr.jid AND mik.kb = :kb"
            params["kb"] = int(installed_kb)
        where = ""
        bind = [bindparam("entity_ids", expanding=True)]
        if glpi_uuids is not None:
            where += " AND mr.glpi_uuid IN :glpi_uuids"
            params["glpi_uuids"] = glpi_uuids
            bind.append(bindparam("glpi_uuids", expanding=True))
        if jid:
            where += " AND mr.jid = :jid"
            params["jid"] = jid
        machines = []
        for row in session.execute(text(f"""
                SELECT mr.jid, mr.glpi_uuid, mr.received_at, mr.reboot_pending,
                       lgm.entities_id AS entity_id,
                       COALESCE(xm.hostname, mr.hostname) AS hostname,
                       xm.jid AS xmpp_jid,
                       {offer} AS offer,
                       EXISTS (SELECT 1 FROM approved_updates au
                                WHERE au.entity_id = lgm.entities_id
                                  AND au.update_id = :update_id
                                  AND (au.by_rule = 0
                                       OR COALESCE({offer}, 'main') = 'main')) AS approved,
                       (SELECT {DEPLOY_IN_PROGRESS_SQL}
                          FROM xmppmaster.deploy d
                         WHERE d.inventoryuuid = mr.glpi_uuid
                           AND d.command IN (SELECT c.id FROM msc.commands c
                                                   WHERE c.package_id = :package_uuid)
                         ORDER BY d.start DESC, d.id DESC LIMIT 1) AS deploying,
                       EXISTS (SELECT 1 FROM xmppmaster.deploy d
                                WHERE d.inventoryuuid = mr.glpi_uuid
                                  AND d.command IN (SELECT c.id FROM msc.commands c
                                                   WHERE c.package_id = :package_uuid)
                                  AND {DEPLOY_AWAITING_REPORT_SQL}) AS awaiting_report,
                       {deployed} AS deployed_pending_report,
                       {MACHINE_BUSY_SQL} AS running,
                       EXISTS (SELECT 1 FROM machine_upgrades mg
                                WHERE mg.jid = mr.jid AND mg.launched_at IS NOT NULL) AS upgrading,
                       EXISTS (SELECT 1 FROM machine_upgrades mg
                                WHERE mg.jid = mr.jid
                                  AND {RELEASE_TO_RESUME_SQL}) AS release_to_resume
                FROM machine_reports mr
                {WINDOWS_MACHINE_ENTITY_JOIN}
                {XM_LATEST_JOIN_SQL}
                WHERE lgm.entities_id IN :entity_ids
                  AND EXISTS ({target})
                  {where}
                ORDER BY hostname, mr.jid
                """).bindparams(*bind), params):
            machines.append({
                "jid": row.jid,
                "glpi_uuid": row.glpi_uuid,
                "hostname": row.hostname or "",
                "entity_id": int(row.entity_id),
                "offer": row.offer or "",
                "approved": bool(row.approved) and row.offer != "esu",
                "known": row.xmpp_jid is not None,
                "deploying": bool(row.deploying),
                "awaiting_report": bool(row.awaiting_report),
                "deployed_pending_report": bool(row.deployed_pending_report),
                "running": bool(row.running),
                "upgrading": bool(row.upgrading),
                "release_to_resume": bool(row.release_to_resume),
                "reboot_pending": bool(row.reboot_pending),
            })
        return machines

    @staticmethod
    def _windows_deploy_update(catalog):
        return {
            "update_id": int(catalog.id),
            "kb": catalog.kb,
            "title": catalog.title,
            "package_uuid": catalog.package_uuid or "",
            "package_state": catalog.package_state or "",
            "package_error": catalog.package_error or "",
        }

    @DatabaseHelper._sessionm
    def get_windows_deploy_targets(self, session, update_id, entity_id, jid=None):
        """Update, its package and the entity machines missing it (only jid if given).

        None when the update is unknown. Per machine: "known" (xmppmaster
        machine found), "deploying" (latest deployment of the package still in
        progress), "awaiting_report" (package deployed successfully since the
        last report), "running" (a deployment of any package holds the machine,
        or its command waits), "release_to_resume" (Linux release step stopped:
        sources already changed), "approved" (approved for the machine's entity).
        """
        update_id = int(update_id)
        entity_id = int(entity_id)
        catalog = self._windows_update_package(session, update_id)
        if catalog is None:
            return None
        approved = session.execute(text("""
            SELECT EXISTS (SELECT 1 FROM approved_updates au
                            WHERE au.entity_id = :entity_id
                              AND au.update_id = :update_id) AS approved
            """), {"update_id": update_id, "entity_id": entity_id}).scalar()
        result = self._windows_deploy_update(catalog)
        result["approved"] = bool(approved)
        return {
            "update": result,
            "machines": self._windows_deploy_machines(session, update_id,
                                                      catalog.package_uuid, [entity_id],
                                                      jid=jid),
        }

    @DatabaseHelper._sessionm
    def get_windows_uninstall_target(self, session, kb, jid, entity_ids):
        """Update of kb whose package can remove it, and the machine jid of
        entity_ids reporting it installed (same fields as get_windows_deploy_targets).

        None when no catalog update carries kb or when it cannot be removed; the
        update with a ready package comes first.
        """
        catalog = session.execute(text(f"""
            {WINDOWS_UPDATE_PACKAGE_SQL}
            WHERE u.kb = :kb AND NOT {WINDOWS_NOT_REMOVABLE_SQL}
            ORDER BY p.state = 'ready' DESC, up.package_uuid IS NOT NULL DESC, u.id DESC
            LIMIT 1
            """), {"kb": int(kb)}).first()
        entity_ids = self._entity_id_list(entity_ids)
        if catalog is None or not entity_ids:
            return None
        return {
            "update": self._windows_deploy_update(catalog),
            "machines": self._windows_deploy_machines(session, int(catalog.id),
                                                      catalog.package_uuid, entity_ids,
                                                      jid=jid, installed_kb=kb),
        }

    @staticmethod
    def _linux_family_package(session, family):
        """uuid of the ready package of a Linux family, None without one."""
        # updates.packages is written by the substitute only: a pkgs package of the
        # same label is not one of ours. The latest ready is the current sequence.
        return session.execute(text("""
            SELECT p.uuid
            FROM packages p
            JOIN pkgs.packages pk
              ON CONVERT(pk.uuid USING utf8mb4) COLLATE utf8mb4_unicode_ci = p.uuid
            WHERE p.state = 'ready' AND pk.label = :label
            ORDER BY p.ready_at DESC
            LIMIT 1
            """), {"label": LINUX_PACKAGE_LABEL % family}).scalar()

    @DatabaseHelper._sessionm
    def get_linux_deploy_target(self, session, jid, entity_ids):
        """Package of the Linux family of jid, the packages approved by the Linux
        rules of its entity and the machine (fields of get_windows_deploy_targets);
        None when jid is not a Linux machine of entity_ids."""
        entity_ids = self._entity_id_list(entity_ids)
        report = session.execute(text(f"""
            SELECT mr.family, lgm.entities_id AS entity_id
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            WHERE mr.jid = :jid AND mr.os = 'linux' AND lgm.entities_id IN :entity_ids
            """).bindparams(bindparam("entity_ids", expanding=True)),
            {"jid": jid, "entity_ids": entity_ids}).first() if entity_ids else None
        if report is None or not report.family:
            return None
        rules_source = self._effective_source(session, "effective_rules", report.entity_id,
                                              "linux")
        packages = [row.package for row in session.execute(text(f"""
            SELECT DISTINCT mu.package FROM machine_updates mu
            WHERE mu.jid = :jid AND mu.package IS NOT NULL AND {LINUX_RULE_MATCH_SQL}
            ORDER BY mu.package
            """), {"jid": jid, "linux_rules_source": rules_source})]
        package_uuid = self._linux_family_package(session, report.family)
        return {
            "package_uuid": package_uuid or "",
            "packages": packages,
            "machines": self._windows_deploy_machines(session, 0, package_uuid, entity_ids,
                                                      jid=jid, linux=True),
        }

    @DatabaseHelper._sessionm
    def get_linux_group_targets(self, session, glpi_uuids, entity_ids):
        """Linux machines glpi_uuids of entity_ids: {"machines": n, "targets": those
        with a package to upgrade}; a target has the fields of
        get_linux_deploy_target machines, "package_uuid" of its family and
        "approved_packages"."""
        result = {"machines": 0, "targets": []}
        entity_ids = self._entity_id_list(entity_ids)
        glpi_uuids = list(glpi_uuids or [])
        if not entity_ids or not glpi_uuids:
            return result
        families = {}
        for row in session.execute(text(f"""
                SELECT mr.glpi_uuid, mr.family
                FROM machine_reports mr
                {WINDOWS_MACHINE_ENTITY_JOIN}
                WHERE mr.os = 'linux' AND lgm.entities_id IN :entity_ids
                  AND mr.glpi_uuid IN :glpi_uuids
                """).bindparams(bindparam("entity_ids", expanding=True),
                                bindparam("glpi_uuids", expanding=True)),
                {"entity_ids": entity_ids, "glpi_uuids": glpi_uuids}):
            result["machines"] += 1
            families.setdefault(row.family, []).append(row.glpi_uuid)
        for family, uuids in families.items():
            package_uuid = self._linux_family_package(session, family) if family else None
            for machine in self._windows_deploy_machines(session, 0, package_uuid, entity_ids,
                                                         glpi_uuids=uuids, linux=True):
                machine["package_uuid"] = package_uuid or ""
                result["targets"].append(machine)
        if result["targets"]:
            approved = self._linux_approved_packages(
                session, [machine["jid"] for machine in result["targets"]])
            for machine in result["targets"]:
                machine["approved_packages"] = approved.get(machine["jid"], 0)
        return result

    @DatabaseHelper._sessionm
    def get_linux_group_packages(self, session, glpi_uuids, entity_ids, start=0, limit=-1,
                                 filter=""):
        """Packages approved for the Linux machines glpi_uuids of entity_ids, by name:
        {"total": n, "rows": [{"package", "severity": highest among those machines,
        "machines": those missing it and approved}]}."""
        result = {"total": 0, "rows": []}
        entity_ids = self._entity_id_list(entity_ids)
        glpi_uuids = list(glpi_uuids or [])
        if not entity_ids or not glpi_uuids:
            return result
        params = {"entity_ids": entity_ids, "glpi_uuids": glpi_uuids}
        condition = ""
        filter = str(filter or "").strip()
        if filter:
            condition = "AND LOWER(mu.package) LIKE LOWER(:filter) ESCAPE '!'"
            params["filter"] = self._like_pattern(filter)
        page = self._page_sql(start, limit, params)
        for row in session.execute(text(f"""
                WITH s AS (
                    SELECT mu.package,
                           MIN({windows_severity_rank_sql("mu.severity")}) AS severity_rank,
                           COUNT(DISTINCT mu.jid) AS machines
                    {LINUX_APPROVED_PACKAGES_SQL}
                      AND mr.os = 'linux' AND lgm.entities_id IN :entity_ids
                      AND mr.glpi_uuid IN :glpi_uuids
                      {condition}
                    GROUP BY mu.package)
                SELECT t.total, p.package, p.severity_rank, p.machines
                FROM (SELECT COUNT(*) AS total FROM s) t
                LEFT JOIN (SELECT * FROM s ORDER BY s.package {page}) p ON 1 = 1
                ORDER BY p.package
                """).bindparams(bindparam("entity_ids", expanding=True),
                                bindparam("glpi_uuids", expanding=True)), params):
            result["total"] = int(row.total)
            if row.package is not None:
                result["rows"].append({
                    "package": row.package,
                    "severity": (WINDOWS_SEVERITY_ORDER + ("",))[int(row.severity_rank)],
                    "machines": int(row.machines),
                })
        return result

    @DatabaseHelper._sessionm
    def get_windows_removable_kbs(self, session, jid):
        """{kb: reinstalled} for the KBs installed on jid that a ready Medulla
        package can remove; reinstalled: the machine's entity approves the update
        and deploys automatically, so it would come back."""
        removable = {}
        for row in session.execute(text(f"""
                SELECT mik.kb,
                       MAX(es.auto_deploy = 1 AND au.update_id IS NOT NULL) AS reinstalled
                FROM machine_installed_kbs mik
                JOIN machine_reports mr ON mr.jid = mik.jid
                {WINDOWS_MACHINE_ENTITY_JOIN}
                JOIN updates u ON u.kb = mik.kb
                JOIN update_packages up ON up.update_id = u.id
                JOIN packages p ON p.uuid = up.package_uuid AND p.state = 'ready'
                LEFT JOIN approved_updates au
                  ON au.entity_id = lgm.entities_id AND au.update_id = u.id
                LEFT JOIN effective_settings es ON es.entity_id = lgm.entities_id
                WHERE mik.jid = :jid AND NOT {WINDOWS_NOT_REMOVABLE_SQL}
                GROUP BY mik.kb
                """), {"jid": jid}):
            removable[int(row.kb)] = bool(row.reinstalled)
        return removable

    @DatabaseHelper._sessionm
    def get_windows_group_deploy_targets(self, session, update_id, glpi_uuids, entity_ids):
        """Same as get_windows_deploy_targets for the machines glpi_uuids of entity_ids."""
        update_id = int(update_id)
        catalog = self._windows_update_package(session, update_id)
        if catalog is None:
            return None
        entity_ids = self._entity_id_list(entity_ids)
        machines = []
        if glpi_uuids and entity_ids:
            machines = self._windows_deploy_machines(session, update_id,
                                                     catalog.package_uuid, entity_ids,
                                                     glpi_uuids=list(glpi_uuids))
        return {"update": self._windows_deploy_update(catalog), "machines": machines}

    @DatabaseHelper._sessionm
    def get_windows_group_updates(self, session, glpi_uuids, entity_ids):
        """Catalog updates missing on the Windows machines glpi_uuids of entity_ids.

        "machines": machines missing it; "eligible": of those, the ones whose
        entity approved it for them, with the package ready; "offer": the first
        it has among them.
        """
        result = {"rows": [], "machines": 0}
        entity_ids = self._entity_id_list(entity_ids)
        glpi_uuids = list(glpi_uuids or [])
        if not entity_ids or not glpi_uuids:
            return result
        params = {"entity_ids": entity_ids, "glpi_uuids": glpi_uuids}
        bind = (bindparam("entity_ids", expanding=True),
                bindparam("glpi_uuids", expanding=True))
        result["machines"] = int(session.execute(text(f"""
            SELECT COUNT(DISTINCT mr.jid)
            FROM machine_reports mr
            {WINDOWS_MACHINE_ENTITY_JOIN}
            WHERE mr.os = 'windows' AND lgm.entities_id IN :entity_ids AND mr.glpi_uuid IN :glpi_uuids
            """).bindparams(*bind), params).scalar() or 0)
        if not result["machines"]:
            return result
        for row in session.execute(text(f"""
                SELECT g.*,
                       EXISTS (SELECT 1 FROM kb_cves kc JOIN cves c ON c.id = kc.cve_id
                                WHERE kc.kb = g.kb AND c.exploited = 1) AS exploited
                FROM (SELECT u.id AS update_id, u.kb, u.title, u.severity,
                             ELT(MIN({windows_offer_rank_sql("mu.offer")}),
                                 {WINDOWS_OFFERS_SQL}) AS offer,
                             COUNT(DISTINCT mr.jid) AS machines,
                             COUNT(DISTINCT CASE WHEN au.update_id IS NOT NULL
                                                  AND (au.by_rule = 0 OR mu.offer = 'main')
                                                  AND mu.offer <> 'esu'
                                                  AND p.state = 'ready'
                                                 THEN mr.jid END) AS eligible
                        FROM machine_reports mr
                        {WINDOWS_MACHINE_ENTITY_JOIN}
                        JOIN machine_updates mu ON mu.jid = mr.jid
                        JOIN updates u ON u.id = mu.update_id
                        LEFT JOIN approved_updates au
                          ON au.entity_id = lgm.entities_id AND au.update_id = u.id
                        LEFT JOIN update_packages up ON up.update_id = u.id
                        LEFT JOIN packages p ON p.uuid = up.package_uuid
                       WHERE lgm.entities_id IN :entity_ids AND mr.glpi_uuid IN :glpi_uuids
                         AND {KNOWN_OFFER_SQL}
                       GROUP BY u.id, u.kb, u.title, u.severity) g
                ORDER BY {windows_offer_rank_sql("g.offer")}, exploited DESC,
                         {windows_severity_rank_sql("g.severity")},
                         g.machines DESC, g.title, g.update_id
                """).bindparams(*bind), params):
            result["rows"].append({
                "update_id": int(row.update_id),
                "kb": row.kb,
                "title": row.title,
                "severity": row.severity or "",
                "offer": row.offer,
                "exploited": bool(row.exploited),
                "machines": int(row.machines),
                "eligible": int(row.eligible),
            })
        return result

    @staticmethod
    def _windows_time(value):
        """TIME column (timedelta) as "HH:MM", "" when NULL."""
        if value is None:
            return ""
        minutes = int(value.total_seconds()) // 60
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    @DatabaseHelper._sessionm
    def get_windows_settings(self, session, entity_id):
        """Effective settings: the entity's row, else its nearest ancestor's."""
        entity_id = int(entity_id)
        row = session.execute(text("""
            SELECT source_id, auto_deploy, window_start, window_end,
                   upgrade_window_start, upgrade_window_end
            FROM effective_settings WHERE entity_id = :entity_id
            """), {"entity_id": entity_id}).first()
        if row is None or row.source_id is None:
            result = {"auto_deploy": False, "window_start": "", "window_end": "",
                      "upgrade_window_start": "", "upgrade_window_end": ""}
            source_id = None
        else:
            result = {"auto_deploy": bool(row.auto_deploy),
                      "window_start": self._windows_time(row.window_start),
                      "window_end": self._windows_time(row.window_end),
                      "upgrade_window_start": self._windows_time(row.upgrade_window_start),
                      "upgrade_window_end": self._windows_time(row.upgrade_window_end)}
            source_id = int(row.source_id)
        result.update(self._inheritance(session, entity_id, source_id))
        return result

    @DatabaseHelper._sessionm
    def set_windows_settings(self, session, entity_id, auto_deploy, window_start,
                             window_end, upgrade_window_start, upgrade_window_end,
                             updated_by=None):
        """Windows: "HH:MM" or None, already validated."""
        try:
            session.execute(text("""
                INSERT INTO entity_settings (entity_id, auto_deploy, window_start,
                                             window_end, upgrade_window_start,
                                             upgrade_window_end, updated_by)
                VALUES (:entity_id, :auto_deploy, :window_start, :window_end,
                        :upgrade_window_start, :upgrade_window_end, :updated_by)
                ON DUPLICATE KEY UPDATE auto_deploy = VALUES(auto_deploy),
                                        window_start = VALUES(window_start),
                                        window_end = VALUES(window_end),
                                        upgrade_window_start = VALUES(upgrade_window_start),
                                        upgrade_window_end = VALUES(upgrade_window_end),
                                        updated_by = VALUES(updated_by)
                """), {"entity_id": int(entity_id), "auto_deploy": 1 if auto_deploy else 0,
                       "window_start": window_start or None,
                       "window_end": window_end or None,
                       "upgrade_window_start": upgrade_window_start or None,
                       "upgrade_window_end": upgrade_window_end or None,
                       "updated_by": updated_by or None})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"set_windows_settings: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_windows_settings(self, session, entity_id):
        """Drop the entity's own settings: it inherits again. Refused for the root."""
        entity_id = int(entity_id)
        try:
            if not self._sub_entity(session, entity_id):
                return False
            session.execute(text("DELETE FROM entity_settings WHERE entity_id = :entity_id"),
                            {"entity_id": entity_id})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"reset_windows_settings: {e}")
            return False

    @DatabaseHelper._sessionm
    def set_windows_approval(self, session, entity_id, update_ids, status, decided_by=None):
        if status not in WINDOWS_APPROVAL_STATUSES:
            return False
        update_ids = self._entity_id_list(update_ids)
        if not update_ids:
            return True
        params = {"entity_id": int(entity_id), "update_ids": update_ids}
        try:
            if status == "pending":
                session.execute(text("""
                    DELETE FROM approvals
                    WHERE entity_id = :entity_id AND update_id IN :update_ids
                    """).bindparams(bindparam("update_ids", expanding=True)), params)
            else:
                params.update(status=status, decided_by=decided_by or None)
                session.execute(text("""
                    INSERT INTO approvals (entity_id, update_id, status, decided_by, decided_at)
                    SELECT :entity_id, u.id, :status, :decided_by, NOW()
                    FROM updates u
                    WHERE u.id IN :update_ids
                    ON DUPLICATE KEY UPDATE status = VALUES(status),
                                            decided_by = VALUES(decided_by),
                                            decided_at = VALUES(decided_at)
                    """).bindparams(bindparam("update_ids", expanding=True)), params)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"set_windows_approval: {e}")
            return False

    @DatabaseHelper._sessionm
    def get_windows_approval_rules(self, session, entity_id, system="windows"):
        """Rule lines offered to the entity. Windows, from the catalog: one per
        severity of a classification that has some, plus one for all its updates
        (severity ""); upgrades are never approved automatically. Linux: one line
        per classification of the packages. "enabled" follows the effective rules
        of the system: the entity's own, or its nearest ancestor's."""
        entity_id = int(entity_id)
        source_id = self._effective_source(session, "effective_rules", entity_id, system)
        levels = self._rule_levels(session, system)
        enabled = {(row.classification, row.severity or "") for row in session.execute(text(
            "SELECT classification, severity FROM approval_rules"
            " WHERE entity_id = :source_id AND os = :os"),
            {"source_id": source_id, "os": system})}
        rules = []
        for classification, severities in levels.items():
            for severity in severities + [""]:
                rules.append({"classification": classification, "severity": severity,
                              "enabled": (classification, severity) in enabled})
        result = {"rules": rules}
        result.update(self._inheritance(session, entity_id, source_id))
        return result

    @staticmethod
    def _rule_levels(session, system):
        """{classification: [severities]} a rule may name."""
        if system == "linux":
            return {classification: [] for classification in LINUX_CLASSIFICATIONS}
        levels = {}
        for row in session.execute(text(f"""
                SELECT DISTINCT classification, severity FROM updates
                WHERE classification IS NOT NULL AND classification <> ''
                  AND classification <> :upgrades
                ORDER BY classification, severity IS NULL,
                         {windows_severity_rank_sql("severity")}, severity
                """), {"upgrades": UPGRADES_CLASSIFICATION}):
            levels.setdefault(row.classification, [])
            if row.severity:
                levels[row.classification].append(row.severity)
        return levels

    @DatabaseHelper._sessionm
    def set_windows_approval_rules(self, session, entity_id, rules, created_by=None,
                                   system="windows"):
        entity_id = int(entity_id)
        try:
            levels = self._rule_levels(session, system)
            classifications = set(levels)
            severities = {severity for values in levels.values() for severity in values}
            cells = []
            for rule in rules or []:
                if not isinstance(rule, dict):
                    continue
                classification = rule.get("classification")
                # XML-RPC sends None as ""
                severity = rule.get("severity") or None
                if classification not in classifications \
                        or (severity is not None and severity not in severities):
                    continue
                if (classification, severity) not in cells:
                    cells.append((classification, severity))
            session.execute(text(
                "DELETE FROM approval_rules WHERE entity_id = :entity_id AND os = :os"),
                {"entity_id": entity_id, "os": system})
            if cells:
                session.execute(text("""
                    INSERT INTO approval_rules (entity_id, os, classification, severity,
                                                created_by)
                    VALUES (:entity_id, :os, :classification, :severity, :created_by)
                    """), [{"entity_id": entity_id, "os": system,
                            "classification": classification, "severity": severity,
                            "created_by": created_by or None}
                           for classification, severity in cells])
            self._set_override(session, entity_id, RULES_SETTINGS[system])
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"set_windows_approval_rules: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_windows_approval_rules(self, session, entity_id, system="windows"):
        """Drop the entity's own rules of the system: it inherits them again.
        Refused for the root."""
        entity_id = int(entity_id)
        try:
            if not self._sub_entity(session, entity_id):
                return False
            params = {"entity_id": entity_id, "os": system, "setting": RULES_SETTINGS[system]}
            session.execute(text(
                "DELETE FROM approval_rules WHERE entity_id = :entity_id AND os = :os"), params)
            session.execute(text("""
                DELETE FROM entity_overrides
                WHERE entity_id = :entity_id AND setting = :setting
                """), params)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"reset_windows_approval_rules: {e}")
            return False
