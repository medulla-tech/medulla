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
 * Security Module - Ajax Softwares List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$location = isset($_GET["location"]) ? $_GET["location"] : "";

// Get policies to determine which columns to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';
$showSeverity = SeverityHelper::getVisibility($minSeverity);

// Get data from backend
$result = xmlrpc_get_softwares_summary($start, $maxperpage, $filter, $location);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$softwareNames = array();
$versions = array();
$maxScores = array();
$criticalCounts = array();
$highCounts = array();
$mediumCounts = array();
$lowCounts = array();
$totalCounts = array();
$machinesAffected = array();
$params = array();

foreach ($data as $row) {
    $softwareNames[] = $row['software_name'];
    $versions[] = $row['software_version'];
    $maxScores[] = SecurityBadge::score($row['max_cvss']);
    $criticalCounts[] = SecurityBadge::count($row['critical'], 'critical');
    $highCounts[] = SecurityBadge::count($row['high'], 'high');
    $mediumCounts[] = SecurityBadge::count($row['medium'], 'medium');
    $lowCounts[] = SecurityBadge::count($row['low'], 'low');
    $totalCounts[] = $row['total_cves'];
    $machinesAffected[] = $row['machines_affected'];
    $params[] = array(
        'software_name' => $row['software_name'],
        'software_version' => $row['software_version']
    );
}

// Actions
$detailAction = new ActionItem(_T("View CVEs", "security"), "softwareDetail", "display", "", "security", "security");
$excludeAction = new ActionPopupItem(_T("Exclude this software", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
$excludeAction->setWidth(400);

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($softwareNames, _T("Software", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($versions, _T("Version", "security"));
    $n->addExtraInfo($maxScores, _T("Max CVSS", "security"));
    if ($showSeverity['critical']) $n->addExtraInfo($criticalCounts, _T("Critical", "security"));
    if ($showSeverity['high']) $n->addExtraInfo($highCounts, _T("High", "security"));
    if ($showSeverity['medium']) $n->addExtraInfo($mediumCounts, _T("Medium", "security"));
    if ($showSeverity['low']) $n->addExtraInfo($lowCounts, _T("Low", "security"));
    $n->addExtraInfo($totalCounts, _T("Total", "security"));
    $n->addExtraInfo($machinesAffected, _T("Machines", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->addActionItem($excludeAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    EmptyStateBox::show(
        _T("No vulnerable software found", "security"),
        _T("No software with CVE data match your current filters.", "security")
    );
}
?>
