<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 */

// =============================================================================
// Legacy
// =============================================================================
function xmlrpc_tests() {
    return xmlCall("security.tests", array());
}

// =============================================================================
// Dashboard
// =============================================================================
function xmlrpc_get_dashboard_summary($location = '') {
    return xmlCall("security.get_dashboard_summary", array($location));
}

// =============================================================================
// CVE List
// =============================================================================
function xmlrpc_get_cves($start = 0, $limit = 50, $filter = '',
                         $severity = null, $location = '',
                         $sort_by = 'cvss_score', $sort_order = 'desc') {
    return xmlCall("security.get_cves", array(
        $start, $limit, $filter, $severity, $location, $sort_by, $sort_order
    ));
}

function xmlrpc_get_cve_details($cve_id, $location = '') {
    return xmlCall("security.get_cve_details", array($cve_id, $location));
}

// =============================================================================
// Machines
// =============================================================================
function xmlrpc_get_machines_summary($start = 0, $limit = 50, $filter = '', $location = '') {
    return xmlCall("security.get_machines_summary", array($start, $limit, $filter, $location));
}

function xmlrpc_get_machine_cves($id_glpi, $start = 0, $limit = 50, $filter = '', $severity = null) {
    return xmlCall("security.get_machine_cves", array($id_glpi, $start, $limit, $filter, $severity));
}

function xmlrpc_scan_machine($id_glpi) {
    return xmlCall("security.scan_machine", array($id_glpi));
}

// =============================================================================
// Scans
// =============================================================================
function xmlrpc_get_scans($start = 0, $limit = 20) {
    return xmlCall("security.get_scans", array($start, $limit));
}

function xmlrpc_create_scan() {
    return xmlCall("security.create_scan", array());
}

function xmlrpc_create_scan_entity($entity_id) {
    return xmlCall("security.create_scan_entity", array($entity_id));
}

function xmlrpc_create_scan_group($group_id) {
    return xmlCall("security.create_scan_group", array($group_id));
}

// =============================================================================
// Configuration
// =============================================================================
function xmlrpc_get_config($key = null) {
    return xmlCall("security.get_config", array($key));
}

function xmlrpc_set_config($key, $value) {
    return xmlCall("security.set_config", array($key, $value));
}

// =============================================================================
// Exclusions
// =============================================================================
function xmlrpc_get_exclusions() {
    return xmlCall("security.get_exclusions", array());
}

function xmlrpc_add_exclusion($cve_id, $reason, $user, $expires_at = null) {
    return xmlCall("security.add_exclusion", array($cve_id, $reason, $user, $expires_at));
}

function xmlrpc_remove_exclusion($cve_id) {
    return xmlCall("security.remove_exclusion", array($cve_id));
}

// =============================================================================
// Software-centric view
// =============================================================================
function xmlrpc_get_softwares_summary($start = 0, $limit = 50, $filter = '', $location = '') {
    return xmlCall("security.get_softwares_summary", array($start, $limit, $filter, $location));
}

function xmlrpc_get_software_cves($software_name, $software_version, $start = 0, $limit = 50,
                                   $filter = '', $severity = null) {
    return xmlCall("security.get_software_cves", array(
        $software_name, $software_version, $start, $limit, $filter, $severity
    ));
}

// =============================================================================
// Entity-centric view
// =============================================================================
function xmlrpc_get_entities_summary($start = 0, $limit = 50, $filter = '', $user_entities = '') {
    return xmlCall("security.get_entities_summary", array($start, $limit, $filter, $user_entities));
}

// =============================================================================
// Group-centric view
// =============================================================================
function xmlrpc_get_groups_summary($start = 0, $limit = 50, $filter = '', $user_login = '') {
    return xmlCall("security.get_groups_summary", array($start, $limit, $filter, $user_login));
}

function xmlrpc_get_group_machines($group_id, $start = 0, $limit = 50, $filter = '') {
    return xmlCall("security.get_group_machines", array($group_id, $start, $limit, $filter));
}
?>
