<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Reflex Module - XML-RPC client layer. Views never call xmlCall() directly.
 */

function reflex_current_login()
{
    return isset($_SESSION['login']) ? $_SESSION['login'] : '';
}

// Without a login the backend applies no entity filter and serves the channels
// of every client: no call of this file leaves without one.
function reflex_call_login($login = null)
{
    if ($login === null || $login === '') {
        return reflex_current_login();
    }
    return (string) $login;
}

// Paginated answers: rows and total, whatever a failed call brought back.
function reflex_rows($result, $fallback = array())
{
    return (is_array($result) && isset($result['data']) && is_array($result['data']))
        ? $result['data'] : $fallback;
}

function reflex_total($result)
{
    return (is_array($result) && isset($result['total'])) ? intval($result['total']) : 0;
}

// =============================================================================
// Dashboard
// =============================================================================
function xmlrpc_reflex_get_dashboard_summary($login)
{
    return xmlCall("reflex.get_dashboard_summary", array($login));
}

// =============================================================================
// Probes
// =============================================================================
// $entity_id sent as text: the root entity 0 must not read as an absent choice.
function xmlrpc_reflex_get_probes($login, $start = 0, $limit = 20, $filter = '', $scope = 'all', $entity_id = '')
{
    return xmlCall("reflex.get_probes", array($login, $start, $limit, $filter, $scope, (string) $entity_id));
}

function xmlrpc_reflex_get_probe($login, $probe_id, $entity_id = '')
{
    return xmlCall("reflex.get_probe", array($login, $probe_id, (string) $entity_id));
}

function xmlrpc_reflex_create_probe($login, $probe)
{
    return xmlCall("reflex.create_probe", array($login, $probe));
}

function xmlrpc_reflex_update_probe($login, $probe_id, $probe)
{
    return xmlCall("reflex.update_probe", array($login, $probe_id, $probe));
}

function xmlrpc_reflex_delete_probe($login, $probe_id)
{
    return xmlCall("reflex.delete_probe", array($login, $probe_id));
}

function xmlrpc_reflex_duplicate_probe($login, $probe_id, $label = '', $entity_id = null)
{
    return xmlCall("reflex.duplicate_probe",
        reflex_optional_entity(array($login, $probe_id, $label), $entity_id));
}

function xmlrpc_reflex_set_probe_visibility($login, $probe_id, $visibility, $entity_id = null)
{
    return xmlCall("reflex.set_probe_visibility",
        reflex_optional_entity(array($login, $probe_id, $visibility), $entity_id));
}

// XML-RPC carries no null: a caller with no entity sends one argument less.
// intval('') is 0 like the root entity, hence ctype_digit to tell them apart.
function reflex_optional_entity($params, $entity_id)
{
    if ($entity_id === null) {
        return $params;
    }
    $raw = trim((string) $entity_id);
    if ($raw === '' || !ctype_digit($raw)) {
        return $params;
    }
    $params[] = intval($raw);
    return $params;
}

function xmlrpc_reflex_get_probe_collectors($login, $probe_id)
{
    return xmlCall("reflex.get_probe_collectors", array($login, $probe_id));
}

function xmlrpc_reflex_get_user_entities($login)
{
    return xmlCall("reflex.get_user_entities", array($login));
}

function xmlrpc_reflex_get_probe_entity_settings($login, $probe_id)
{
    return xmlCall("reflex.get_probe_entity_settings", array($login, intval($probe_id)));
}

// =============================================================================
// Probe conditions
// =============================================================================
function xmlrpc_reflex_set_probe_conditions($login, $probe_id, $conditions)
{
    return xmlCall("reflex.set_probe_conditions", array($login, $probe_id, $conditions));
}

// A key left out of $overrides goes back to the shipped value: send the whole
// state of the override, not a differential.
function xmlrpc_reflex_set_condition_override($login, $condition_id, $overrides, $entity_id = '')
{
    return xmlCall("reflex.set_condition_override",
                   array($login, $condition_id, $overrides, (string) $entity_id));
}

function xmlrpc_reflex_reset_condition_override($login, $condition_id, $entity_id = '')
{
    return xmlCall("reflex.reset_condition_override",
                   array($login, $condition_id, (string) $entity_id));
}

// =============================================================================
// Probe assignments
// =============================================================================
// $language is kept with the assignment so the alert mail is written in the
// language of the operator who placed the probe.
function xmlrpc_reflex_assign_probe($login, $probe_id, $target_type, $target_id, $interval_seconds, $language = null)
{
    return xmlCall("reflex.assign_probe", array($login, $probe_id, $target_type, $target_id, $interval_seconds, $language));
}

function xmlrpc_reflex_assign_probe_bulk($login, $probe_id, $target_type, $target_ids, $interval_seconds, $language = null)
{
    return xmlCall("reflex.assign_probe_bulk", array($login, $probe_id, $target_type, $target_ids, $interval_seconds, $language));
}

function xmlrpc_reflex_update_assignment_interval($login, $assignment_id, $interval_seconds)
{
    return xmlCall("reflex.update_assignment_interval", array($login, $assignment_id, $interval_seconds));
}

function xmlrpc_reflex_unassign_probe($login, $assignment_id)
{
    return xmlCall("reflex.unassign_probe", array($login, $assignment_id));
}

function xmlrpc_reflex_unassign_probes_bulk($login, $assignment_ids)
{
    return xmlCall("reflex.unassign_probes_bulk", array($login, $assignment_ids));
}

// =============================================================================
// Probe exclusions
//
// An assignment on 'all', a group or an entity holds no per machine row, so
// removing a probe from a single machine has nothing to delete. The exception
// list carries that decision instead.
// =============================================================================
// The hostname is stored with the exception so the console can name the
// machine without joining xmppmaster.
function xmlrpc_reflex_exclude_probe_on_machine($login, $probe_id, $machines_id, $hostname, $reason = '')
{
    return xmlCall("reflex.exclude_probe_on_machine",
        array($login, $probe_id, $machines_id, $hostname, $reason));
}

function xmlrpc_reflex_include_probe_on_machine($login, $probe_id, $machines_id)
{
    return xmlCall("reflex.include_probe_on_machine", array($login, $probe_id, $machines_id));
}

function xmlrpc_reflex_get_probe_exclusions($login, $probe_id)
{
    return xmlCall("reflex.get_probe_exclusions", array($login, $probe_id));
}

// =============================================================================
// Alerts
// =============================================================================
// $status: 'active' for the alerts that still stand, acknowledged included.
// Empty drops the clause and returns the resolved ones too, which is the
// history. $opened_from and $opened_to are YYYY-MM-DD; a bound the backend
// cannot read gives an empty list, so callers filter it through
// ReflexHelper::periodBound() beforehand.
function xmlrpc_reflex_get_alerts($login, $start = 0, $limit = 20, $filter = '', $severity = '', $status = '',
                                  $opened_from = '', $opened_to = '', $sort = 'severity', $probe_id = 0)
{
    return xmlCall("reflex.get_alerts",
        array($login, $start, $limit, $filter, $severity, $status, $opened_from, $opened_to, $sort,
              intval($probe_id)));
}

function xmlrpc_reflex_get_alert($login, $alert_id)
{
    return xmlCall("reflex.get_alert", array($login, $alert_id));
}

function xmlrpc_reflex_ack_alert($login, $alert_id, $comment = '')
{
    return xmlCall("reflex.ack_alert", array($login, $alert_id, $comment));
}

function xmlrpc_reflex_ack_alerts_bulk($login, $alert_ids, $comment = '')
{
    return xmlCall("reflex.ack_alerts_bulk", array($login, $alert_ids, $comment));
}

// =============================================================================
// Machines
// =============================================================================
function xmlrpc_reflex_get_machines_status($login, $start = 0, $limit = 20, $filter = '')
{
    return xmlCall("reflex.get_machines_status", array($login, $start, $limit, $filter));
}

function xmlrpc_reflex_get_machine_detail($login, $machines_id)
{
    return xmlCall("reflex.get_machine_detail", array($login, $machines_id));
}

// Trailing arguments are only appended when they carry something, so a backend
// without them keeps answering the day periods. max_points travels after
// hours, which is then sent as 0 on a period counted in days.
function xmlrpc_reflex_get_measures_timeseries($login, $machines_id, $probe_id,
                                               $days = 7, $hours = null,
                                               $max_points = null)
{
    $args = array($login, $machines_id, $probe_id, $days);
    $window = ($hours !== null && intval($hours) > 0) ? intval($hours) : 0;
    if ($max_points !== null && intval($max_points) > 0) {
        $args[] = $window;
        $args[] = intval($max_points);
    } elseif ($window > 0) {
        $args[] = $window;
    }
    return xmlCall("reflex.get_measures_timeseries", $args);
}

function xmlrpc_reflex_get_agent_presence($login, $machines_id, $days = 7,
                                          $hours = null)
{
    $args = array($login, $machines_id, $days);
    if ($hours !== null && intval($hours) > 0) {
        $args[] = intval($hours);
    }
    return xmlCall("reflex.get_agent_presence", $args);
}

function xmlrpc_reflex_get_agent_config($machines_id, $login = null)
{
    return xmlCall("reflex.get_agent_config",
                   array($machines_id, reflex_call_login($login)));
}

// =============================================================================
// Notification channels
// =============================================================================
function xmlrpc_reflex_has_encryption_key()
{
    return xmlCall("reflex.has_encryption_key", array());
}

function xmlrpc_reflex_get_retention_settings($login = null)
{
    return xmlCall("reflex.get_retention_settings", array(reflex_call_login($login)));
}

function xmlrpc_reflex_set_retention_settings($login, $values)
{
    return xmlCall("reflex.set_retention_settings", array(reflex_call_login($login), $values));
}

function xmlrpc_reflex_get_channels($login = null)
{
    return xmlCall("reflex.get_channels", array(reflex_call_login($login)));
}

// 'entity_id' in $channel is required and sent as an integer, never as a
// string that may be empty.
function xmlrpc_reflex_create_channel($login, $channel)
{
    return xmlCall("reflex.create_channel", array(reflex_call_login($login), $channel));
}

function xmlrpc_reflex_update_channel($channel_id, $channel, $login = null)
{
    return xmlCall("reflex.update_channel",
        array($channel_id, $channel, reflex_call_login($login)));
}

function xmlrpc_reflex_delete_channel($channel_id, $login = null)
{
    return xmlCall("reflex.delete_channel",
        array($channel_id, reflex_call_login($login)));
}

function xmlrpc_reflex_test_channel($channel_id, $login = null, $language = null, $recipient = null)
{
    return xmlCall("reflex.test_channel",
        array($channel_id, reflex_call_login($login), $language, $recipient));
}

// =============================================================================
// Notification rules
// =============================================================================
// A rule has no entity of its own: it holds the one of its channel, returned
// as channel_entity_id.
function xmlrpc_reflex_get_notification_rules($login = null)
{
    return xmlCall("reflex.get_notification_rules", array(reflex_call_login($login)));
}

function xmlrpc_reflex_create_notification_rule($login, $rule)
{
    return xmlCall("reflex.create_notification_rule", array(reflex_call_login($login), $rule));
}

function xmlrpc_reflex_update_notification_rule($rule_id, $rule, $login = null)
{
    return xmlCall("reflex.update_notification_rule",
        array($rule_id, $rule, reflex_call_login($login)));
}

function xmlrpc_reflex_delete_notification_rule($rule_id, $login = null)
{
    return xmlCall("reflex.delete_notification_rule",
        array($rule_id, reflex_call_login($login)));
}

// =============================================================================
// Value type of a probe, for the pages that only hold an alert
// =============================================================================

// get_probes reads a limit of 0 as its default of twenty, so the catalog is
// asked for as one wide page, then asked again on its own total if wider.
function reflex_probe_rows($login)
{
    static $rows = null;
    if ($rows !== null) {
        return $rows;
    }
    $result = xmlrpc_reflex_get_probes($login, 0, 500, "", "all");
    $rows = reflex_rows($result);
    $total = reflex_total($result);
    if ($total > count($rows)) {
        $result = xmlrpc_reflex_get_probes($login, 0, $total, "", "all");
        $rows = reflex_rows($result, $rows);
    }
    return $rows;
}

// An alert row carries no value_type, and a yes/no value shown as 1 or 0 says
// the opposite of what it means: the alert pages read it from the catalog.
function reflex_probe_value_types($login)
{
    static $types = null;
    if ($types !== null) {
        return $types;
    }
    $types = array();
    foreach (reflex_probe_rows($login) as $row) {
        $probeId = intval($row['id'] ?? 0);
        if ($probeId > 0) {
            $types[$probeId] = strtolower(trim((string) ($row['value_type'] ?? '')));
        }
    }
    return $types;
}

function reflex_probe_value_type($login, $probe_id)
{
    $types = reflex_probe_value_types($login);
    $probeId = intval($probe_id);
    return isset($types[$probeId]) ? $types[$probeId] : '';
}

?>
