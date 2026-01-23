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
 * Security Module - Ajax Group Machines List
 */

require_once("modules/security/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$group_id = isset($_GET["group_id"]) ? intval($_GET["group_id"]) : 0;
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

// Get policies to determine which columns to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';

// Determine which severity columns to show based on min_severity
$severityOrder = array('None' => 0, 'Low' => 1, 'Medium' => 2, 'High' => 3, 'Critical' => 4);
$minSevIndex = isset($severityOrder[$minSeverity]) ? $severityOrder[$minSeverity] : 0;
$showLow = $minSevIndex <= 1;
$showMedium = $minSevIndex <= 2;
$showHigh = $minSevIndex <= 3;
$showCritical = true; // Always show Critical

if ($group_id <= 0) {
    echo '<div class="empty-message">';
    echo '<p>' . _T("Invalid group", "security") . '</p>';
    echo '</div>';
    return;
}

// Get data from backend
$result = xmlrpc_get_group_machines($group_id, $start, $maxperpage, $filter);
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

    // Risk score with color
    $score = floatval($row['risk_score']);
    $scoreClass = 'low';
    if ($score >= 9.0) $scoreClass = 'critical';
    elseif ($score >= 7.0) $scoreClass = 'high';
    elseif ($score >= 4.0) $scoreClass = 'medium';
    $riskScores[] = '<span class="risk-score risk-' . $scoreClass . '">' . number_format($score, 1) . '</span>';

    // Counts with badges
    $criticalCounts[] = $row['critical'] > 0 ?
        '<span class="badge badge-critical">' . $row['critical'] . '</span>' : '0';
    $highCounts[] = $row['high'] > 0 ?
        '<span class="badge badge-high">' . $row['high'] . '</span>' : '0';
    $mediumCounts[] = $row['medium'] > 0 ?
        '<span class="badge badge-medium">' . $row['medium'] . '</span>' : '0';
    $lowCounts[] = isset($row['low']) && $row['low'] > 0 ?
        '<span class="badge badge-low">' . $row['low'] . '</span>' : '0';
    $totalCounts[] = $row['total_cves'];

    // Params for actions
    $params[] = array('id_glpi' => $row['id_glpi'], 'hostname' => $row['hostname']);
}

// Actions
$detailAction = new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security");

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($riskScores, _T("Risk Score", "security"));
    // Only show severity columns that are >= min_severity
    if ($showCritical) {
        $n->addExtraInfo($criticalCounts, _T("Critical", "security"));
    }
    if ($showHigh) {
        $n->addExtraInfo($highCounts, _T("High", "security"));
    }
    if ($showMedium) {
        $n->addExtraInfo($mediumCounts, _T("Medium", "security"));
    }
    if ($showLow) {
        $n->addExtraInfo($lowCounts, _T("Low", "security"));
    }
    $n->addExtraInfo($totalCounts, _T("Total", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message">';
    echo '<p>' . _T("No machines in this group", "security") . '</p>';
    echo '</div>';
}
?>
