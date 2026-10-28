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
// Dashboard
// =============================================================================
function xmlrpc_get_dashboard_summary($location = '', $platform = '', $exploited_only = false)
{
    return xmlCall("security.get_dashboard_summary", array($location, $platform, $exploited_only));
}

// =============================================================================
// CVE List
// =============================================================================
function xmlrpc_get_cves(
    $start = 0,
    $limit = 50,
    $filter = '',
    $severity = null,
    $location = '',
    $sort_by = 'cvss_score',
    $sort_order = 'desc',
    $platform = '',
    $exploited_only = false
) {
    return xmlCall("security.get_cves", array(
        $start,
        $limit,
        $filter,
        $severity,
        $location,
        $sort_by,
        $sort_order,
        $platform,
        $exploited_only
    ));
}

function xmlrpc_get_cve_details($cve_id, $location = '')
{
    return xmlCall("security.get_cve_details", array($cve_id, $location));
}

// =============================================================================
// Machines
// =============================================================================
function xmlrpc_get_machines_summary($start = 0, $limit = 50, $filter = '', $location = '', $platform = '', $exploited_only = false, $group_id = '')
{
    return xmlCall("security.get_machines_summary", array($start, $limit, $filter, $location, $platform, $exploited_only, $group_id));
}

function xmlrpc_get_machine_cves($id_glpi, $start = 0, $limit = 50, $filter = '', $severity = null)
{
    return xmlCall("security.get_machine_cves", array($id_glpi, $start, $limit, $filter, $severity));
}

function xmlrpc_get_machine_softwares_summary($id_glpi, $start = 0, $limit = 50, $filter = '', $category = '')
{
    return xmlCall("security.get_machine_softwares_summary", array($id_glpi, $start, $limit, $filter, $category));
}

function xmlrpc_scan_machine($id_glpi)
{
    return xmlCall("security.scan_machine", array($id_glpi));
}

// =============================================================================
// Configuration
// =============================================================================
function xmlrpc_get_contract_status()
{
    return xmlCall("security.get_contract_status", array());
}

// =============================================================================
// Policies (editable via UI, stored in database)
// =============================================================================
function xmlrpc_get_policies()
{
    return xmlCall("security.get_policies", array());
}

function xmlrpc_set_policies($policies, $user = null)
{
    // JSON avoids XML-RPC nested array issues
    return xmlCall("security.set_policies_json", array(json_encode($policies), $user));
}

function xmlrpc_reset_display_policies($user = null)
{
    return xmlCall("security.reset_display_policies", array($user));
}

// =============================================================================
// Software-centric view
// =============================================================================
function xmlrpc_get_softwares_summary($start = 0, $limit = 50, $filter = '', $location = '', $category = '', $platform = '', $exploited_only = false)
{
    return xmlCall("security.get_softwares_summary", array($start, $limit, $filter, $location, $category, $platform, $exploited_only));
}

function xmlrpc_get_software_cves(
    $software_name,
    $software_version,
    $start = 0,
    $limit = 50,
    $filter = '',
    $severity = null
) {
    return xmlCall("security.get_software_cves", array(
        $software_name,
        $software_version,
        $start,
        $limit,
        $filter,
        $severity
    ));
}

// =============================================================================
// Entity-centric view
// =============================================================================
function xmlrpc_get_entities_summary($start = 0, $limit = 50, $filter = '', $user_entities = '', $platform = '', $exploited_only = false)
{
    return xmlCall("security.get_entities_summary", array($start, $limit, $filter, $user_entities, $platform, $exploited_only));
}

// =============================================================================
// Group-centric view
// =============================================================================
function xmlrpc_get_groups_summary($start = 0, $limit = 50, $filter = '', $user_login = '', $platform = '', $exploited_only = false)
{
    return xmlCall("security.get_groups_summary", array($start, $limit, $filter, $user_login, $platform, $exploited_only));
}

function xmlrpc_get_groups_list()
{
    return xmlCall("security.get_groups_list", array());
}

function xmlrpc_get_group_machines($group_id, $start = 0, $limit = 50, $filter = '')
{
    return xmlCall("security.get_group_machines", array($group_id, $start, $limit, $filter));
}

// =============================================================================
// Group creation helpers
// =============================================================================
function xmlrpc_get_machines_by_severity($severity, $location = '')
{
    return xmlCall("security.get_machines_by_severity", array($severity, $location));
}

// =============================================================================
// Store integration - Deploy updates for vulnerable software
// =============================================================================
function xmlrpc_get_machines_for_vulnerable_software(
    $software_name,
    $software_version,
    $location = '',
    $start = 0,
    $limit = 100,
    $filter = ''
) {
    return xmlCall("security.get_machines_for_vulnerable_software", array(
        $software_name,
        $software_version,
        $location,
        $start,
        $limit,
        $filter
    ));
}
