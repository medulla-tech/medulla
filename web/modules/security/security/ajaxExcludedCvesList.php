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
 * Security Module - AJAX Excluded CVEs List
 */

require_once("modules/security/includes/xmlrpc.php");

global $conf;
$maxperpage = 10;

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

// Get current exclusions from policies
$policies = xmlrpc_get_policies();
$excludedCves = $policies['exclusions']['cve_ids'] ?? array();

// Build CVE data with software info (needed for filtering)
$cveData = array();
foreach ($excludedCves as $cveId) {
    $cveDetails = xmlrpc_get_cve_details($cveId);
    $softwareList = '';
    $softwareNames = array();
    if ($cveDetails && isset($cveDetails['softwares']) && is_array($cveDetails['softwares'])) {
        foreach ($cveDetails['softwares'] as $sw) {
            $softwareNames[] = $sw['name'] . ' ' . $sw['version'];
        }
        $softwareList = implode(', ', array_slice($softwareNames, 0, 3));
        if (count($softwareNames) > 3) {
            $softwareList .= ' (+' . (count($softwareNames) - 3) . ')';
        }
    }
    $cveData[] = array(
        'cve_id' => $cveId,
        'software_list' => $softwareList,
        'software_names' => $softwareNames
    );
}

// Filter by search term (CVE ID or software name)
if (!empty($filter)) {
    $cveData = array_filter($cveData, function($item) use ($filter) {
        // Search in CVE ID
        if (stripos($item['cve_id'], $filter) !== false) {
            return true;
        }
        // Search in software names
        foreach ($item['software_names'] as $swName) {
            if (stripos($swName, $filter) !== false) {
                return true;
            }
        }
        return false;
    });
}

// Re-index array after filtering
$cveData = array_values($cveData);
$count = count($cveData);

// Paginate
$pagedData = array_slice($cveData, $start, $maxperpage);

// Prepare arrays for display
$cveIds = array();
$softwares = array();
$params = array();

foreach ($pagedData as $item) {
    $cveIds[] = htmlspecialchars($item['cve_id']);
    $softwares[] = $item['software_list'] ?: '<i style="color:#999">' . _T("Unknown", "security") . '</i>';
    $params[] = array(
        'name' => $item['cve_id'],
        'type' => 'cve'
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
    echo '<p style="color:#666; font-style:italic;">' . _T("No excluded CVEs", "security") . '</p>';
} else {
    // Create and display list
    $list = new OptimizedListInfos($cveIds, _T("CVE ID", "security"));
    $list->addExtraInfo($softwares, _T("Affected Software", "security"));
    $list->disableFirstColumnActionLink();
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamcontainerExcludedCves", $maxperpage));
    $list->setParamInfo($params);
    $list->addActionItem($removeAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();
}
?>
