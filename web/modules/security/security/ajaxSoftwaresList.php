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

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$location = isset($_GET["location"]) ? $_GET["location"] : "";

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

    // Max CVSS score with color
    $score = floatval($row['max_cvss']);
    $scoreClass = 'low';
    if ($score >= 9.0) $scoreClass = 'critical';
    elseif ($score >= 7.0) $scoreClass = 'high';
    elseif ($score >= 4.0) $scoreClass = 'medium';
    $maxScores[] = '<span class="risk-score risk-' . $scoreClass . '">' . number_format($score, 1) . '</span>';

    // Counts with badges
    $criticalCounts[] = $row['critical'] > 0 ?
        '<span class="badge badge-critical">' . $row['critical'] . '</span>' : '0';
    $highCounts[] = $row['high'] > 0 ?
        '<span class="badge badge-high">' . $row['high'] . '</span>' : '0';
    $mediumCounts[] = $row['medium'] > 0 ?
        '<span class="badge badge-medium">' . $row['medium'] . '</span>' : '0';
    $lowCounts[] = $row['low'] > 0 ?
        '<span class="badge badge-low">' . $row['low'] . '</span>' : '0';
    $totalCounts[] = $row['total_cves'];
    $machinesAffected[] = $row['machines_affected'];

    // Params for actions
    $params[] = array(
        'software_name' => $row['software_name'],
        'software_version' => $row['software_version']
    );
}

// Actions
$detailAction = new ActionItem(_T("View CVEs", "security"), "softwareDetail", "display", "", "security", "security");

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($softwareNames, _T("Software", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($versions, _T("Version", "security"));
    $n->addExtraInfo($maxScores, _T("Max CVSS", "security"));
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
    $n->addExtraInfo($machinesAffected, _T("Machines", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message">';
    echo '<p>' . _T("No vulnerable software found", "security") . '</p>';
    echo '</div>';
}
?>
