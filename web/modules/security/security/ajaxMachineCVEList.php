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
 * Security Module - Ajax Machine CVE List
 */

require_once("modules/security/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$id_glpi = isset($_GET["id_glpi"]) ? intval($_GET["id_glpi"]) : 0;
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$severity = isset($_GET["severity"]) && $_GET["severity"] !== "" ? $_GET["severity"] : null;

if ($id_glpi <= 0) {
    echo '<div class="empty-message">';
    echo '<p>' . _T("Invalid machine ID", "security") . '</p>';
    echo '</div>';
    return;
}

// Get data from backend
$result = xmlrpc_get_machine_cves($id_glpi, $start, $maxperpage, $filter, $severity);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$cveIds = array();
$severities = array();
$cvssScores = array();
$softwareNames = array();
$softwareVersions = array();
$descriptions = array();
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

    // Software info
    $softwareNames[] = htmlspecialchars($row['software_name']);
    $softwareVersions[] = htmlspecialchars($row['software_version']);

    // Description (truncated)
    $desc = $row['description'] ? $row['description'] : '';
    if (strlen($desc) > 80) {
        $desc = substr($desc, 0, 80) . '...';
    }
    $descriptions[] = htmlspecialchars($desc);

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
    $n->addExtraInfo($softwareNames, _T("Software", "security"));
    $n->addExtraInfo($softwareVersions, _T("Version", "security"));
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
    if ($filter || $severity) {
        echo '<p>' . _T("No CVEs match your filter criteria", "security") . '</p>';
    } else {
        echo '<p>' . _T("No CVEs found for this machine", "security") . '</p>';
    }
    echo '</div>';
}
?>
