<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/includes/xmlrpc.php

function xmlrpc_get_replication_state()
{
    return xmlCall("updates.get_replication_state");
}

/**
 * Update counters of the user's scope, for one system.
 *
 * @param int[]  $location     GLPI entities; empty = all the user's entities
 * @param string $system       "windows" or "linux"
 * @param string $distribution Linux distribution (get_linux_distributions); "" = all
 * @return array {machines, evaluated, up_to_date, to_update, critical, not_evaluated, reboot_pending, no_report, conformity}
 */
function xmlrpc_get_windows_summary($location = array(), $system = "windows", $distribution = "")
{
    return xmlCall("updates.get_windows_summary", array(array_values(array_map('intval', (array) $location)),
                                                        (string) $system, (string) $distribution));
}

/**
 * Linux distributions reported in the given entities (all visible ones when empty).
 *
 * @param int[] $location GLPI entities
 * @return array [{distribution, label, machines}], sorted
 */
function xmlrpc_get_linux_distributions($location = array())
{
    return xmlCall("updates.get_linux_distributions", array(array_values(array_map('intval', (array) $location))));
}

/**
 * Windows machines and tracked products of every visible entity.
 *
 * @return array {rows: [{entity_id, machines, no_report, tracked_products}]}
 */
function xmlrpc_get_windows_entities()
{
    return xmlCall("updates.get_windows_entities");
}

/**
 * Machines of one system in the given entities (all visible ones when empty), paginated.
 *
 * @param string $system       "windows" or "linux"
 * @param string $distribution Linux distribution; "" = all
 * @param string $only         Machines of one summary card: "to_update", "critical" or "reboot_pending"; "" = all
 * @return array {total, rows: [{jid, hostname, glpi_uuid, entity_id, entity_name, system, missing, critical,
 *                received_at, evaluated, unsupported, untracked_version}]}
 */
function xmlrpc_get_windows_machines($location, $start, $limit, $filter = "", $system = "windows", $distribution = "", $only = "")
{
    return xmlCall("updates.get_windows_machines", array(array_values(array_map('intval', (array) $location)),
                                                         intval($start), intval($limit), (string) $filter,
                                                         (string) $system, (string) $distribution, (string) $only));
}

/**
 * Windows update state of one machine.
 *
 * @return array|null {jid, hostname, glpi_uuid, entity_id, os ("windows"|"linux"), distribution, kernel, system,
 *                     release, build, language, received_at, evaluated, signals, windows11, tracked_products,
 *                     updates: [{update_id, kb, package_name, installed_version, available_version, ...,
 *                                package: {state, error}, deployment: {state, date, command_id, sessionid}}]}
 */
function xmlrpc_get_windows_machine($jid)
{
    return xmlCall("updates.get_windows_machine", array((string) $jid));
}

/**
 * Update history of one machine, latest first: Medulla deployments and updates the machine reports as installed.
 *
 * @return array {total, rows: [{source ("medulla"|"machine"), title, kb, date, state, removable, reinstalled, ...}]}
 */
function xmlrpc_get_windows_machine_history($jid, $start = 0, $limit = -1)
{
    return xmlCall("updates.get_windows_machine_history", array((string) $jid, intval($start), intval($limit)));
}

/**
 * Windows products offered to an entity, with their tracking state.
 *
 * @return array {rows: [{id, name, group, supported, new, tracked, releases: [{name, tracked}]}]}
 */
function xmlrpc_get_windows_products($entity_id)
{
    return xmlCall("updates.get_windows_products", array(intval($entity_id)));
}

/**
 * Replace the tracked Windows products of an entity.
 *
 * @param array[] $selections [{product_id, release}], release "" for a product without versions
 * @return bool
 */
function xmlrpc_set_windows_products($entity_id, $selections)
{
    $payload = array();
    foreach ((array) $selections as $selection) {
        if (is_array($selection)) {
            $payload[] = array('product_id' => intval($selection['product_id'] ?? 0),
                               'release' => (string) ($selection['release'] ?? ''));
        }
    }
    return xmlCall("updates.set_windows_products", array(intval($entity_id), $payload));
}

/**
 * Linux versions reported by the machines of an entity, tracked or not.
 *
 * @return array {rows: [{distribution, release, codename, tracked, machines}], inherited_from}
 */
function xmlrpc_get_linux_releases($entity_id)
{
    return xmlCall("updates.get_linux_releases", array(intval($entity_id)));
}

/**
 * Replace the tracked Linux versions of an entity.
 *
 * @param array[] $selections [{distribution, release}]
 * @return bool
 */
function xmlrpc_set_linux_releases($entity_id, $selections)
{
    $payload = array();
    foreach ((array) $selections as $selection) {
        if (is_array($selection)) {
            $payload[] = array('distribution' => (string) ($selection['distribution'] ?? ''),
                               'release' => (string) ($selection['release'] ?? ''));
        }
    }
    return xmlCall("updates.set_linux_releases", array(intval($entity_id), $payload));
}

/**
 * Drop the own Linux versions of a sub-entity: it takes those of its parent again.
 *
 * @return bool False for the root entity or when refused
 */
function xmlrpc_reset_linux_releases($entity_id)
{
    return xmlCall("updates.reset_linux_releases", array(intval($entity_id)));
}

/**
 * Windows updates of an entity in one approval state, paginated, critical first.
 *
 * @param string $status pending, approved or declined; ignored for linux
 * @param string $system windows or linux
 * @return array {total, counts: {pending, approved, declined}, rows: [{update_id, kb, title, classification,
 *                severity, exploited, critical, machines, by_rule, decided_by, decided_at,
 *                package_state, package_error, deployed}]}
 *               linux: rows [{package, classification, severity, machines, approved}], rules_from {id, name}|null
 */
function xmlrpc_get_windows_approvals($entity_id, $status, $start, $limit, $filter = "", $system = 'windows', $distribution = '')
{
    return xmlCall("updates.get_windows_approvals",
                   array(intval($entity_id), (string) $status, intval($start), intval($limit), (string) $filter,
                         (string) $system, (string) $distribution));
}

/**
 * Set the approval state of Windows updates for an entity.
 *
 * @param string[] $update_ids
 * @param string   $status approved, declined or pending
 * @return bool
 */
function xmlrpc_set_windows_approval($entity_id, $update_ids, $status)
{
    return xmlCall("updates.set_windows_approval",
                   array(intval($entity_id), array_values(array_map('strval', (array) $update_ids)), (string) $status));
}

/**
 * Automatic approval rules of an entity for one system.
 *
 * @param string $system windows or linux
 * @return array {rules: [{classification, severity, enabled}], inherited_from, parent},
 *               inheritance of this system only
 */
function xmlrpc_get_windows_approval_rules($entity_id, $system = "windows")
{
    return xmlCall("updates.get_windows_approval_rules", array(intval($entity_id), (string) $system));
}

/**
 * Replace the automatic approval rules of an entity for one system,
 * the rules of the other systems are left as they are.
 *
 * @param array  $rules  [{classification, severity}], severity "" = no severity
 * @param string $system windows or linux
 * @return bool
 */
function xmlrpc_set_windows_approval_rules($entity_id, $rules, $system = "windows")
{
    return xmlCall("updates.set_windows_approval_rules",
                   array(intval($entity_id), array_values((array) $rules), (string) $system));
}

/**
 * Deploy an approved Windows update to the machines of an entity that miss it,
 * or to one machine of that entity.
 *
 * @param string $jid "" = every machine of the entity that needs it
 * @return array {created, skipped: [{jid, hostname, reason}], error}
 */
function xmlrpc_deploy_windows_update($update_id, $entity_id, $jid = "")
{
    return xmlCall("updates.deploy_windows_update", array((string) $update_id, intval($entity_id), (string) $jid));
}

/**
 * Deploy to one Linux machine the missing packages approved by the Linux rules of its entity,
 * or only $package when given.
 *
 * @return array {created, skipped: [{jid, hostname, reason}], packages, error}
 */
function xmlrpc_deploy_linux_updates($jid, $package = '')
{
    return xmlCall("updates.deploy_linux_updates", array((string) $jid, (string) $package));
}

/**
 * Remove an installed Windows update from one machine with its Medulla package.
 *
 * @return array {created, skipped: [{jid, hostname, reason}], error, package_error}
 */
function xmlrpc_uninstall_windows_update($kb, $jid)
{
    return xmlCall("updates.uninstall_windows_update", array((string) $kb, (string) $jid));
}

/**
 * Automatic deployment and upgrade settings of an entity.
 *
 * @return array {auto_deploy: bool, window_start: "HH:MM"|"", window_end: "HH:MM"|"",
 *                upgrade_window_start: "HH:MM"|"", upgrade_window_end: "HH:MM"|""}
 */
function xmlrpc_get_windows_settings($entity_id)
{
    return xmlCall("updates.get_windows_settings", array(intval($entity_id)));
}

/**
 * Save the automatic deployment and upgrade settings of an entity.
 *
 * @param bool   $auto_deploy
 * @param string $window_start         "HH:MM" or ""
 * @param string $window_end           "HH:MM" or ""
 * @param string $upgrade_window_start "HH:MM" or "": both empty, the upgrade steps start right away
 * @param string $upgrade_window_end   "HH:MM" or ""
 * @return bool False when refused (half-filled upgrade range, or start equal to end)
 */
function xmlrpc_set_windows_settings($entity_id, $auto_deploy, $window_start, $window_end, $upgrade_window_start, $upgrade_window_end)
{
    return xmlCall("updates.set_windows_settings",
                   array(intval($entity_id), (bool) $auto_deploy, (string) $window_start, (string) $window_end,
                         (string) $upgrade_window_start, (string) $upgrade_window_end));
}

/**
 * Drop the own tracked products of a sub-entity: it takes those of its parent again.
 *
 * @return bool False for the root entity or when refused
 */
function xmlrpc_reset_windows_products($entity_id)
{
    return xmlCall("updates.reset_windows_products", array(intval($entity_id)));
}

/**
 * Drop the own automatic approval rules of a sub-entity for one system:
 * it takes those of its parent again for this system only.
 *
 * @param string $system windows or linux
 * @return bool False for the root entity or when refused
 */
function xmlrpc_reset_windows_approval_rules($entity_id, $system = "windows")
{
    return xmlCall("updates.reset_windows_approval_rules", array(intval($entity_id), (string) $system));
}

/**
 * Drop the own automatic deployment settings of a sub-entity: it takes those of its parent again.
 *
 * @return bool False for the root entity or when refused
 */
function xmlrpc_reset_windows_settings($entity_id)
{
    return xmlCall("updates.reset_windows_settings", array(intval($entity_id)));
}

/**
 * Windows updates missing on the machines of a group.
 *
 * @return array {rows: [{update_id, kb, title, severity, exploited, machines, eligible}], machines}
 */
function xmlrpc_get_windows_group_updates($gid)
{
    return xmlCall("updates.get_windows_group_updates", array(intval($gid)));
}

/**
 * Deploy a Windows update to the machines of a group that can receive it.
 *
 * @return array {created, skipped: [{jid, hostname, reason}]}
 */
function xmlrpc_deploy_windows_update_group($update_id, $gid)
{
    return xmlCall("updates.deploy_windows_update_group", array((string) $update_id, intval($gid)));
}

/**
 * Linux machines of a group and what deploying their approved packages would reach.
 *
 * @return array {machines, eligible, packages, error?}
 */
function xmlrpc_get_linux_group_summary($gid)
{
    return xmlCall("updates.get_linux_group_summary", array(intval($gid)));
}

/**
 * Packages approved for the Linux machines of a group, paginated.
 *
 * @return array {total, rows: [{package, severity?, machines}], error?}
 */
function xmlrpc_get_linux_group_packages($gid, $start = 0, $limit = -1, $filter = "")
{
    return xmlCall("updates.get_linux_group_packages", array(intval($gid), intval($start), intval($limit), (string) $filter));
}

/**
 * Deploy to the Linux machines of a group the packages approved by their entity.
 *
 * @return array {deployed, skipped: [{jid, hostname, reason}], error}
 */
function xmlrpc_deploy_linux_group($gid)
{
    return xmlCall("updates.deploy_linux_group", array(intval($gid)));
}

/**
 * Upgrade counters of the visible machines of a system.
 *
 * @param int[]  $location GLPI entities; empty = all the user's entities
 * @param string $system   "windows" or "linux"
 * @return array {total, categories: {key: count}}
 */
function xmlrpc_get_upgrade_summary($location = array(), $system = 'windows')
{
    return xmlCall("updates.get_upgrade_summary",
                   array(array_values(array_map('intval', (array) $location)), (string) $system));
}

/**
 * Visible machines of a system with their upgrade, paginated.
 *
 * @param int[]  $location GLPI entities; empty = all the user's entities
 * @param string $filter   Substring of the machine name
 * @param string $only     One category key, "" = all
 * @param string $system   "windows" or "linux"
 * @return array {total, rows: [{jid, hostname, glpi_uuid, product, release, build,
 *                received_at, entity_id, entity_name, state, target_release, reason, run_error,
 *                launched_at, category}]}; Linux rows also carry distribution, kernel
 */
function xmlrpc_get_upgrade_machine_list($location, $start, $limit, $filter = "", $only = "", $system = 'windows')
{
    return xmlCall("updates.get_upgrade_machine_list", array(
        array_values(array_map('intval', (array) $location)),
        intval($start),
        intval($limit),
        (string) $filter,
        (string) $only,
        (string) $system,
    ));
}

/**
 * Launch the upgrade of ready machines of an entity.
 *
 * @param string[] $glpi_uuids UUIDn
 * @return array {launched, error: entity_refused|internal_error when refused}
 */
function xmlrpc_launch_upgrades($entity_id, $glpi_uuids)
{
    return xmlCall("updates.launch_upgrades",
                   array(intval($entity_id), array_values(array_map('strval', (array) $glpi_uuids))));
}

/**
 * Abandon the running upgrade of a machine.
 *
 * @param string $jid
 * @return array {error: ""|not_launched|step_running|forbidden|internal_error}
 */
function xmlrpc_cancel_upgrade($jid)
{
    return xmlCall("updates.cancel_upgrade", array((string) $jid));
}

/**
 * Restart a machine waiting for a restart.
 *
 * @param string $jid
 * @return array {sent: bool, reason: ""|not_found|not_waiting|offline|already_requested|send_failed}
 */
function xmlrpc_restart_machine($jid)
{
    return xmlCall("updates.restart_machine", array((string) $jid));
}

/**
 * What upgrading a group would do.
 *
 * @param string[] $systems Systems the user may upgrade: "windows", "linux"
 * @return array {launch, targets: {release: n}, skipped: {category: n}, system_refused,
 *                error?: unknown_group|internal_error}
 */
function xmlrpc_get_upgrade_group_preview($gid, $systems)
{
    return xmlCall("updates.get_upgrade_group_preview",
                   array(intval($gid), array_values(array_map('strval', (array) $systems))));
}

/**
 * Launch the upgrade of the ready machines of a group.
 *
 * @param string[] $systems Systems the user may upgrade: "windows", "linux"
 * @return array {launched, error?}
 */
function xmlrpc_launch_upgrade_group($gid, $systems)
{
    return xmlCall("updates.launch_upgrade_group",
                   array(intval($gid), array_values(array_map('strval', (array) $systems))));
}
