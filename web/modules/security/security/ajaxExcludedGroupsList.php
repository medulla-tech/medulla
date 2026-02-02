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
 * Security Module - AJAX Excluded Groups List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

global $conf;
$maxperpage = 10;

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

// Get current exclusions from policies
$policies = xmlrpc_get_policies();
$excludedGroups = $policies['exclusions']['groups_ids'] ?? array();

// Display message if no exclusions
if (empty($excludedGroups)) {
    EmptyStateBox::show(
        _T("No excluded groups", "security"),
        _T("Groups can be excluded directly from the 'Results by Group' view using the exclude action.", "security")
    );
} else {
    // Build group data with info from dyngroup
    $groupData = array();

    foreach ($excludedGroups as $groupId) {
        $groupId = intval($groupId);
        // Load group info
        $group = new Group($groupId, true, false, true);

        if ($group->exists) {
            // Determine group type - a group is dynamic if it has a non-empty query
            $groupType = _T("Static", "security");
            if ($group->isDyn()) {
                $groupType = _T("Dynamic", "security");
            }

            $groupData[] = array(
                'group_id' => $groupId,
                'group_name' => $group->name,
                'group_type' => $groupType
            );
        } else {
            // Group not found (maybe deleted)
            $groupData[] = array(
                'group_id' => $groupId,
                'group_name' => _T("Unknown", "security") . ' (ID: ' . $groupId . ')',
                'group_type' => ''
            );
        }
    }

    // Filter by search term
    if (!empty($filter)) {
        $groupData = array_filter($groupData, function($item) use ($filter) {
            if (stripos(strval($item['group_id']), $filter) !== false) return true;
            if (stripos($item['group_name'], $filter) !== false) return true;
            if (stripos($item['group_type'], $filter) !== false) return true;
            return false;
        });
    }

    // Re-index array after filtering
    $groupData = array_values($groupData);
    $count = count($groupData);

    // Paginate
    $pagedData = array_slice($groupData, $start, $maxperpage);

    // Prepare arrays for display
    $groupNames = array();
    $groupTypes = array();
    $params = array();

    foreach ($pagedData as $item) {
        $groupNames[] = htmlspecialchars($item['group_name']);
        $groupTypes[] = htmlspecialchars($item['group_type']);
        $params[] = array(
            'name' => $item['group_id'],
            'type' => 'group'
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
            _T("No groups match your search", "security"),
            _T("Try a different search term.", "security")
        );
    } else {
        // Create and display list
        $list = new OptimizedListInfos($groupNames, _T("Group", "security"));
        $list->addExtraInfo($groupTypes, _T("Type", "security"));
        $list->disableFirstColumnActionLink();
        $list->setItemCount($count);
        $list->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamcontainerExcludedGroups", $maxperpage));
        $list->setParamInfo($params);
        $list->addActionItem($removeAction);
        $list->start = 0;
        $list->end = $count;
        $list->display();
    }
}
?>
