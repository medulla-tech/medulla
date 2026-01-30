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
 *
 * Security Module - AJAX Excluded Machines List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");
require_once("modules/base/includes/computers.inc.php");

global $conf;
$maxperpage = 10;

// Helper function to safely get value from array or string
function getInfoValue($info, $key, $default = '') {
    if (!isset($info[$key])) {
        return $default;
    }
    $value = $info[$key];
    if (is_array($value)) {
        return $value[0] ?? $default;
    }
    return $value;
}

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

// Get current exclusions from policies
$policies = xmlrpc_get_policies();
$excludedMachines = $policies['exclusions']['machines_ids'] ?? array();

// Display message if no exclusions
if (empty($excludedMachines)) {
    EmptyStateBox::show(
        _T("No excluded machines", "security"),
        _T("Machines can be excluded directly from the 'Results by Machine' view using the exclude action.", "security")
    );
} else {
    // Build filter to get machines by their UUIDs
    $uuids = array_map(function($id) { return 'UUID' . intval($id); }, $excludedMachines);

    // Get machine info using getRestrictedComputersList
    $machineFilter = array('uuids' => $uuids);
    if (!empty($filter)) {
        $machineFilter['hostname'] = $filter;
    }

    $machinesList = getRestrictedComputersList(0, -1, $machineFilter, False);

    // Build machine data array
    $machineData = array();

    // Create a set of found machine IDs
    $foundIds = array();

    if (!empty($machinesList) && is_array($machinesList)) {
        foreach ($machinesList as $uuid => $machine) {
            $info = $machine[1] ?? array();
            $machineId = intval(str_replace('UUID', '', $info['objectUUID'][0] ?? $uuid));
            $foundIds[$machineId] = true;

            $machineData[] = array(
                'machine_id' => $machineId,
                'hostname' => getInfoValue($info, 'cn', _T("Unknown", "security")),
                'os' => getInfoValue($info, 'os', ''),
                'entity' => getInfoValue($info, 'entity', '')
            );
        }
    }

    // Add machines not found in GLPI (maybe deleted)
    foreach ($excludedMachines as $machineId) {
        $machineId = intval($machineId);
        if (!isset($foundIds[$machineId])) {
            // Only add if not already in the list and matches filter
            if (empty($filter) || stripos(strval($machineId), $filter) !== false) {
                $machineData[] = array(
                    'machine_id' => $machineId,
                    'hostname' => _T("Unknown", "security") . ' (ID: ' . $machineId . ')',
                    'os' => '',
                    'entity' => ''
                );
            }
        }
    }

    // Sort by hostname
    usort($machineData, function($a, $b) {
        return strcasecmp($a['hostname'], $b['hostname']);
    });

    $count = count($machineData);

    // Paginate
    $pagedData = array_slice($machineData, $start, $maxperpage);

    // Prepare arrays for display
    $hostnames = array();
    $osNames = array();
    $entities = array();
    $params = array();

    foreach ($pagedData as $item) {
        $hostnames[] = htmlspecialchars($item['hostname']);
        $osNames[] = htmlspecialchars($item['os']);
        $entities[] = htmlspecialchars($item['entity']);
        $params[] = array(
            'name' => $item['machine_id'],
            'type' => 'machine'
        );
    }

    // Create remove action
    $removeAction = new ActionPopupItem(
        _T("Remove from exclusions", "security"),
        "ajaxRemoveExclusion",
        "remove",
        "",
        "security",
        "security"
    );
    $removeAction->setWidth(400);

    if ($count == 0) {
        EmptyStateBox::show(
            _T("No machines match your search", "security"),
            _T("Try a different search term.", "security")
        );
    } else {
        // Create and display list
        $list = new OptimizedListInfos($hostnames, _T("Machine", "security"));
        $list->addExtraInfo($osNames, _T("Operating System", "security"));
        $list->addExtraInfo($entities, _T("Entity", "security"));
        $list->disableFirstColumnActionLink();
        $list->setItemCount($count);
        $list->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamcontainerExcludedMachines", $maxperpage));
        $list->setParamInfo($params);
        $list->addActionItem($removeAction);
        $list->start = 0;
        $list->end = $count;
        $list->display();
    }
}
?>
