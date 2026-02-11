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
 * Security Module - Ajax Machines List
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
$result = xmlrpc_get_machines_summary($start, $maxperpage, $filter, $location);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$hostnames = array();
$riskScores = array();
$criticalCounts = array();
$highCounts = array();
$mediumCounts = array();
$lowCounts = array();
$totalCounts = array();
$params = array();

foreach ($data as $row) {
    $hostnames[] = $row['hostname'];
    $riskScores[] = SecurityBadge::score($row['risk_score']);
    $criticalCounts[] = SecurityBadge::count($row['critical'], 'critical');
    $highCounts[] = SecurityBadge::count($row['high'], 'high');
    $mediumCounts[] = SecurityBadge::count($row['medium'], 'medium');
    $lowCounts[] = SecurityBadge::count($row['low'], 'low');
    $totalCounts[] = $row['total_cves'];
    $params[] = array(
        'id_glpi' => $row['id_glpi'],
        'hostname' => $row['hostname'],
        'machine_id' => $row['id_glpi'],
        'machine_name' => $row['hostname']
    );
}

// Actions
$detailAction = new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security");
$scanAction = new ActionPopupItem(_T("Scan Machine", "security"), "ajaxScanMachine", "scan", "", "security", "security");
$scanAction->setWidth(500);
$excludeAction = new ActionPopupItem(_T("Exclude from reports", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
$excludeAction->setWidth(450);

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($riskScores, _T("Risk Score", "security"));
    if ($showSeverity['critical']) $n->addExtraInfo($criticalCounts, _T("Critical", "security"));
    if ($showSeverity['high']) $n->addExtraInfo($highCounts, _T("High", "security"));
    if ($showSeverity['medium']) $n->addExtraInfo($mediumCounts, _T("Medium", "security"));
    if ($showSeverity['low']) $n->addExtraInfo($lowCounts, _T("Low", "security"));
    $n->addExtraInfo($totalCounts, _T("Total", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->addActionItem($scanAction);
    $n->addActionItem($excludeAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    EmptyStateBox::show(
        _T("No machines found", "security"),
        _T("No machines with CVE data match your current filters. Try adjusting your search criteria or run a scan to collect vulnerability data.", "security")
    );
}
?>
