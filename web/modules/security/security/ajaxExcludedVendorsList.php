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
 * Security Module - AJAX Excluded Vendors List
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
$excludedVendors = $policies['exclusions']['vendors'] ?? array();

// Filter by search term
if (!empty($filter)) {
    $excludedVendors = array_filter($excludedVendors, function($vendor) use ($filter) {
        return stripos($vendor, $filter) !== false;
    });
}

// Re-index array after filtering
$excludedVendors = array_values($excludedVendors);
$count = count($excludedVendors);

// Paginate
$pagedVendors = array_slice($excludedVendors, $start, $maxperpage);

// Prepare arrays for display
$vendorNames = array();
$params = array();

foreach ($pagedVendors as $vendor) {
    $vendorNames[] = htmlspecialchars($vendor);
    $params[] = array(
        'name' => $vendor,
        'type' => 'vendor'
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
        _T("No excluded vendors", "security"),
        _T("Use the form above to add vendors to the exclusion list.", "security")
    );
} else {
    // Create and display list
    $list = new OptimizedListInfos($vendorNames, _T("Vendor name", "security"));
    $list->disableFirstColumnActionLink();
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamcontainerExcludedVendors", $maxperpage));
    $list->setParamInfo($params);
    $list->addActionItem($removeAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();
}
?>
