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
 * Security Module - AJAX Excluded Software List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = 10;

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

// Get current exclusions from policies
$policies = xmlrpc_get_policies();
$excludedNames = $policies['exclusions']['names'] ?? array();

// Filter by search term
if (!empty($filter)) {
    $excludedNames = array_filter($excludedNames, function($name) use ($filter) {
        return stripos($name, $filter) !== false;
    });
}

// Re-index array after filtering
$excludedNames = array_values($excludedNames);
$count = count($excludedNames);

// Paginate
$pagedNames = array_slice($excludedNames, $start, $maxperpage);

// Prepare arrays for display
$softwareNames = array();
$params = array();

foreach ($pagedNames as $name) {
    $softwareNames[] = htmlspecialchars($name);
    $params[] = array(
        'name' => $name,
        'type' => 'software'
    );
}

// Create remove action (uses "remove" CSS class for red minus icon)
$removeAction = new ActionPopupItem(
    _T("Remove from exclusions", "security"),
    "ajaxRemoveExclusion",
    "remove",
    "",
    "security",
    "security"
);
$removeAction->setWidth(400);

// Display message if no exclusions
if ($count == 0) {
    EmptyStateBox::show(
        _T("No excluded software", "security"),
        _T("Use the form above to add software to the exclusion list.", "security")
    );
} else {
    // Create and display list
    $list = new OptimizedListInfos($softwareNames, _T("Software name", "security"));
    $list->disableFirstColumnActionLink();
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamcontainerExcludedSoftware", $maxperpage));
    $list->setParamInfo($params);
    $list->addActionItem($removeAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();
}
?>
