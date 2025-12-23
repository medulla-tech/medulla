<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * Medulla Store - Machine list for deployment
 * List of machines with checkboxes for deployment selection
 */

require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"] ?? 20;

// Filter parameters (same as ajaxMachinesList.php)
$location = isset($_GET['location']) ? $_GET['location'] : "";
$filter = isset($_GET['filter']) ? $_GET['filter'] : "";
// IMPORTANT: field must be 'allchamp' for the filter to work on all fields
$field = isset($_GET['field']) && $_GET['field'] != '' ? $_GET['field'] : "allchamp";
$contains = isset($_GET['contains']) ? $_GET['contains'] : "";

$start = isset($_GET['start']) ? intval($_GET['start']) : 0;
$end = isset($_GET['end']) ? intval($_GET['end']) : $start + $maxperpage - 1;

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;
$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

if (isset($_SESSION['computerpresence']) && $_SESSION['computerpresence'] != "all_computer") {
    $ctx['computerpresence'] = $_SESSION['computerpresence'];
}

try {
    $machines = xmlrpc_xmppmaster_get_machines_list($start, $maxperpage, $ctx);
} catch(Exception $e) {
    echo '<p style="text-align:center;color:#c00;padding:20px;">Error: ' . htmlspecialchars($e->getMessage()) . '</p>';
    return;
}

$count = (!empty($machines["count"])) ? $machines["count"] : 0;
$total = $machines["total"] ?? 0;
$datas = $machines["data"] ?? [];

if (empty($datas) || empty($datas['hostname'])) {
    echo '<p style="text-align:center;color:#888;padding:20px;">' . _T('No machines found', 'store') . '</p>';
    return;
}

// Prepare data
$names = [];
$params = [];
$osCol = [];
$entityCol = [];

for ($i = 0; $i < count($datas['hostname']); $i++) {
    $hostname = $datas['hostname'][$i] ?? '';
    $uuid = $datas['uuid_inventorymachine'][$i] ?? '';
    $os = $datas['platform'][$i] ?? '';
    $entity = $datas['entityname'][$i] ?? '';
    $online = !empty($datas['enabled'][$i]);

    if (empty($uuid)) continue;

    // Presence icon
    $statusIcon = $online
        ? '<img src="img/other/machine_up.svg" width="20" height="20" style="vertical-align:middle;margin-right:5px;" title="' . _T('Online', 'store') . '"/>'
        : '<img src="img/other/machine_down.svg" width="20" height="20" style="vertical-align:middle;margin-right:5px;" title="' . _T('Offline', 'store') . '"/>';

    // Checkbox + icon + name
    $names[] = '<input type="checkbox" class="machine-checkbox" name="machines[]" value="' . htmlspecialchars($uuid) . '" style="vertical-align:middle;margin-right:8px;"/>' . $statusIcon . htmlspecialchars($hostname);

    $params[] = [
        'objectUUID' => $uuid,
        'cn' => $hostname,
        'os' => $os,
        'entity' => $entity
    ];

    $osCol[] = htmlspecialchars($os ?: '-');
    $entityCol[] = htmlspecialchars($entity ?: '-');
}

if (empty($names)) {
    echo '<p style="text-align:center;color:#888;padding:20px;">' . _T('No machines found', 'store') . '</p>';
    return;
}

// Display with OptimizedListInfos
$n = new OptimizedListInfos($names, _T("Computer Name", "store"));
$n->disableFirstColumnActionLink();
$n->setParamInfo($params);
$n->addExtraInfo($osCol, _T("OS", "store"));
$n->addExtraInfo($entityCol, _T("Entity", "store"));
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, $filter, "updateSearchMachinesDeploy", $maxperpage));
$n->start = 0;
$n->end = count($names);
$n->display();
