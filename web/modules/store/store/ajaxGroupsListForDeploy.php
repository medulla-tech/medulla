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
 * Medulla Store - Groups list for deployment
 * List of machine groups with checkboxes for deployment selection
 */

require_once('modules/dyngroup/includes/dyngroup.php');

global $conf;
$maxperpage = $conf["global"]["maxperpage"] ?? 20;

$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";
$start = (isset($_GET['start'])) ? intval($_GET['start']) : 0;

$params = array('min'=>$start, 'max'=>$start + $maxperpage, 'filter'=>$filter);

// Get machine groups (not profiles)
$list = getAllGroups($params);
$count = countAllGroups($params);

if (empty($list)) {
    echo '<p style="text-align:center;color:#888;padding:20px;">' . _T('No groups found', 'store') . '</p>';
    return;
}

$packageUuid = $_GET['packageUuid'] ?? '';
$pid = $_GET['pid'] ?? '';

// Prepare data
$names = [];
$types = [];
$counts = [];
$paramsInfo = [];

foreach ($list as $group) {
    $groupId = $group->id;
    $groupName = $group->getName();

    // Checkbox + group name
    $names[] = '<input type="checkbox" class="group-checkbox" name="groups[]" value="' . htmlspecialchars($groupId) . '" data-name="' . htmlspecialchars($groupName) . '" style="vertical-align:middle;margin-right:8px;"/>'
        . '<img src="modules/base/graph/navbar/group.svg" width="18" height="18" style="vertical-align:middle;margin-right:5px;"/>'
        . htmlspecialchars($groupName);

    // Type (dynamic or static)
    if ($group->isDyn()) {
        $types[] = (!($group->isRequest())
            ? sprintf(_T('Dynamic (%s)', 'store'), $group->countResult())
            : _T('Query', 'store'));
        $machineCount = $group->countResult();
    } else {
        $types[] = _T('Static', 'store');
        $machineCount = $group->countResult();
    }

    $counts[] = $machineCount . ' ' . _T('machines', 'store');

    $paramsInfo[] = [
        'gid' => $groupId,
        'groupName' => $groupName
    ];
}

// CSS IDs
$css_ids = [];
foreach ($list as $group) {
    $css_ids[] = 'g_' . $group->id;
}

$n = new OptimizedListInfos($names, _T('Group name', 'store'));
$n->setCssIds($css_ids);
$n->disableFirstColumnActionLink();
$n->setParamInfo($paramsInfo);
$n->addExtraInfo($types, _T('Type', 'store'));
$n->addExtraInfo($counts, _T('Size', 'store'));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchGroupsDeploy", $maxperpage));
$n->start = 0;
$n->end = count($names);
$n->display();
