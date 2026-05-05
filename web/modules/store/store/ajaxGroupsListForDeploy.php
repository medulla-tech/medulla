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
$groupIds = [];

foreach ($list as $group) {
    $groupId = $group->id;
    $groupName = $group->getName();

    $names[] = '<strong>' . htmlspecialchars($groupName) . '</strong>';
    $groupIds[] = $groupId;

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

// Inject checkboxes + group icon
$groupIdsJson = json_encode($groupIds);
echo <<<SCRIPT
<script>
(function() {
    var ids = {$groupIdsJson};
    // Select all rows (not just .alternate which is the zebra stripe class)
    var rows = document.querySelectorAll('#tab-groups .listinfos tbody tr, .listinfos tbody tr');
    var injected = 0;
    for (var i = 0; i < rows.length && injected < ids.length; i++) {
        var cell = rows[i].children[0];
        if (!cell) continue;
        // Skip if already injected (avoid double injection)
        if (cell.querySelector('.group-checkbox')) continue;
        cell.classList.add('bulk-active');

        var icon = new Image();
        icon.src = 'img/other/machinegroup.svg';
        icon.style.cssText = 'width:22px;height:22px;flex-shrink:0;margin:0 4px;';

        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'group-checkbox';
        cb.name = 'groups[]';
        cb.value = ids[injected];
        // Same nested-form problem as the machines tab: the AJAX-injected row
        // ends up outside the deploy form. The HTML5 'form' attribute pins
        // the input to the right form regardless of DOM parentage.
        cb.setAttribute('form', 'deploy-form-groups');
        cb.style.cssText = 'width:15px;height:15px;cursor:pointer;flex-shrink:0;margin:0 2px;';

        var first = cell.firstChild;
        cell.insertBefore(icon, first);
        cell.insertBefore(cb, icon);
        injected++;
    }
    if (typeof updateSelectedGroupsCount === 'function') updateSelectedGroupsCount();
})();
</script>
SCRIPT;
