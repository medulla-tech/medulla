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
 * Security Module - Ajax Software CVE List
 */

require_once("modules/security/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$software_name = isset($_GET["software_name"]) ? $_GET["software_name"] : "";
$software_version = isset($_GET["software_version"]) ? $_GET["software_version"] : "";
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$severity = isset($_GET["severity"]) && $_GET["severity"] !== "" ? $_GET["severity"] : null;

if (empty($software_name)) {
    echo '<div class="empty-message">';
    echo '<p>' . _T("Invalid software", "security") . '</p>';
    echo '</div>';
    return;
}

// Get data from backend
$result = xmlrpc_get_software_cves($software_name, $software_version, $start, $maxperpage, $filter, $severity);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$cveIds = array();
$severities = array();
$cvssScores = array();
$descriptions = array();
$publishedDates = array();
$params = array();
$cssClasses = array();

foreach ($data as $row) {
    $cveIds[] = $row['cve_id'];

    // Severity with color badge
    $sev = $row['severity'];
    $sevClass = $sev === 'N/A' ? 'na' : strtolower($sev);
    $severities[] = '<span class="badge badge-' . $sevClass . '">' . $sev . '</span>';

    // CVSS Score
    $cvss = floatval($row['cvss_score']);
    $cvssScores[] = number_format($cvss, 1);

    // Description (truncated)
    $desc = $row['description'] ? $row['description'] : '';
    if (strlen($desc) > 100) {
        $desc = substr($desc, 0, 100) . '...';
    }
    $descriptions[] = htmlspecialchars($desc);

    // Published date
    $pubDate = '';
    if (!empty($row['published_at'])) {
        $pubDate = date('Y-m-d', strtotime($row['published_at']));
    }
    $publishedDates[] = $pubDate;

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
    $n->addExtraInfo($descriptions, _T("Description", "security"));
    $n->addExtraInfo($publishedDates, _T("Published", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem($detailAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message">';
    if ($filter || $severity) {
        echo '<p>' . _T("No CVEs match your filter criteria", "security") . '</p>';
    } else {
        echo '<p>' . _T("No CVEs found for this software", "security") . '</p>';
    }
    echo '</div>';
}
?>
