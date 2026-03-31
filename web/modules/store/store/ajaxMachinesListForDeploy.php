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

// Only show online machines (can't deploy to offline)
$ctx['computerpresence'] = 'presence';

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
$presenceClasses = [];
$machineUuids = [];

for ($i = 0; $i < count($datas['hostname']); $i++) {
    $hostname = $datas['hostname'][$i] ?? '';
    $uuid = $datas['uuid_inventorymachine'][$i] ?? '';
    $os = $datas['platform'][$i] ?? '';
    $entity = $datas['entityname'][$i] ?? '';
    $online = !empty($datas['enabled'][$i]);

    if (empty($uuid)) continue;

    $names[] = '<strong>' . htmlspecialchars($hostname) . '</strong>';
    $machineUuids[] = $uuid;

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
$n = new OptimizedListInfos($names, _T("Computer Name", "glpi"));
$n->disableFirstColumnActionLink();
$n->setParamInfo($params);
$n->addExtraInfo($osCol, _T("OS", "store"));
$n->addExtraInfo($entityCol, _T("Entity", "store"));
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, $filter, "updateSearchMachinesDeploy", $maxperpage));
$n->start = 0;
$n->end = count($names);
$n->display();

// Inject checkboxes + machine icon
$uuidsJson = json_encode($machineUuids);
echo <<<SCRIPT
<script>
(function() {
    var uuids = {$uuidsJson};
    var rows = document.querySelectorAll('.listinfos tbody tr.alternate');
    for (var i = 0; i < rows.length && i < uuids.length; i++) {
        var cell = rows[i].children[0];
        if (!cell) continue;
        cell.classList.add('bulk-active');

        var icon = new Image();
        icon.src = 'img/other/machine_up.svg';
        icon.style.cssText = 'width:22px;height:22px;flex-shrink:0;filter:none !important;vertical-align:middle;margin:0 4px;';

        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'machine-checkbox';
        cb.name = 'machines[]';
        cb.value = uuids[i];
        cb.style.cssText = 'width:15px;height:15px;cursor:pointer;flex-shrink:0;vertical-align:middle;margin:0 2px;';

        // Order: checkbox, icon, then existing text
        var first = cell.firstChild;
        cell.insertBefore(icon, first);
        cell.insertBefore(cb, icon);
    }
    if (typeof updateSelectedCount === 'function') updateSelectedCount();
})();
</script>
SCRIPT;
