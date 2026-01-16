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
 * Security Module - Ajax CVE List
 */

require_once("modules/security/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$severity = isset($_GET["severity"]) && $_GET["severity"] !== "" ? $_GET["severity"] : null;
$location = isset($_GET["location"]) ? $_GET["location"] : "";

// Get data from backend
$result = xmlrpc_get_cves($start, $maxperpage, $filter, $severity, $location);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$cveIds = array();
$severities = array();
$cvssScores = array();
$descriptions = array();
$machinesCounts = array();
$softwaresList = array();
$params = array();
$cssClasses = array();

foreach ($data as $row) {
    $cveIds[] = $row['cve_id'];

    // Severity with color badge
    $sev = $row['severity'];
    $sevClass = strtolower($sev);
    $severities[] = '<span class="badge badge-' . $sevClass . '">' . $sev . '</span>';

    // CVSS Score
    $cvss = floatval($row['cvss_score']);
    $cvssScores[] = number_format($cvss, 1);

    // Description (truncated)
    $desc = $row['description'] ? $row['description'] : '';
    if (strlen($desc) > 80) {
        $desc = substr($desc, 0, 80) . '...';
    }
    $descriptions[] = htmlspecialchars($desc);

    // Machines affected
    $machinesCounts[] = $row['machines_affected'];

    // Softwares affected
    $swList = array();
    if (isset($row['softwares']) && is_array($row['softwares'])) {
        foreach ($row['softwares'] as $sw) {
            $swList[] = htmlspecialchars($sw['name'] . ' ' . $sw['version']);
        }
    }
    $softwaresList[] = implode(', ', array_slice($swList, 0, 2)) . (count($swList) > 2 ? '...' : '');

    // Params for actions
    $params[] = array('cve_id' => $row['cve_id']);

    // CSS class
    $cssClasses[] = 'severity-' . $sevClass;
}

// Actions
$detailAction = new ActionItem(_T("View Details", "security"), "cveDetail", "display", "", "security", "security");

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($cveIds, _T("CVE ID", "security"));
    $n->disableFirstColumnActionLink();
    $n->setCssClasses($cssClasses);
    $n->addExtraInfo($severities, _T("Severity", "security"));
    $n->addExtraInfo($cvssScores, _T("CVSS", "security"));
    $n->addExtraInfo($softwaresList, _T("Software", "security"));
    $n->addExtraInfo($machinesCounts, _T("Machines", "security"));
    $n->addExtraInfo($descriptions, _T("Description", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message">';
    echo '<p>' . _T("No CVEs found. Run a scan to populate the database.", "security") . '</p>';
    echo '</div>';
}
?>
