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
 * Security Module - Ajax Entities List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$userEntities = isset($_GET["user_entities"]) ? $_GET["user_entities"] : "";

// Get policies to determine which columns to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';
$showSeverity = SeverityHelper::getVisibility($minSeverity);

// Get data from backend (filtered by user's accessible entities)
$result = xmlrpc_get_entities_summary($start, $maxperpage, $filter, $userEntities);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$entityNames = array();
$machinesCounts = array();
$maxScores = array();
$criticalCounts = array();
$highCounts = array();
$mediumCounts = array();
$lowCounts = array();
$totalCounts = array();
$params = array();

foreach ($data as $row) {
    $entityNames[] = $row['entity_fullname'];
    $machinesCounts[] = $row['machines_count'];
    $maxScores[] = SecurityBadge::score($row['max_cvss']);
    $criticalCounts[] = SecurityBadge::count($row['critical'], 'critical');
    $highCounts[] = SecurityBadge::count($row['high'], 'high');
    $mediumCounts[] = SecurityBadge::count($row['medium'], 'medium');
    $lowCounts[] = SecurityBadge::count($row['low'], 'low');
    $totalCounts[] = $row['total_cves'];
    $params[] = array(
        'location' => 'UUID' . $row['entity_id'],
        'entity_id' => $row['entity_id'],
        'entity_name' => $row['entity_fullname']
    );
}

// Actions - view machines in this entity
$detailAction = new ActionItem(_T("View Machines", "security"), "machines", "display", "", "security", "security");
$scanAction = new ActionPopupItem(_T("Scan this entity", "security"), "ajaxStartScanEntity", "scan", "", "security", "security");

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($entityNames, _T("Entity", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($machinesCounts, _T("Machines", "security"));
    $n->addExtraInfo($maxScores, _T("Max CVSS", "security"));
    if ($showSeverity['critical']) $n->addExtraInfo($criticalCounts, _T("Critical", "security"));
    if ($showSeverity['high']) $n->addExtraInfo($highCounts, _T("High", "security"));
    if ($showSeverity['medium']) $n->addExtraInfo($mediumCounts, _T("Medium", "security"));
    if ($showSeverity['low']) $n->addExtraInfo($lowCounts, _T("Low", "security"));
    $n->addExtraInfo($totalCounts, _T("Total CVEs", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->addActionItem($scanAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    EmptyStateBox::show(
        _T("No entities found", "security"),
        _T("No entities with CVE data match your current filters. Try adjusting your search criteria or run a scan to collect vulnerability data.", "security")
    );
}
?>
