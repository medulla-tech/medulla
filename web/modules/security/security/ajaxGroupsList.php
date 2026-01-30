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
 * Security Module - Ajax Groups List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get filter parameters
$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$userLogin = isset($_GET["user_login"]) ? $_GET["user_login"] : "";

// Get policies to determine which columns to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';
$showSeverity = SeverityHelper::getVisibility($minSeverity);

// Get data from backend (filtered by ShareGroup for this user)
$result = xmlrpc_get_groups_summary($start, $maxperpage, $filter, $userLogin);
$data = $result['data'];
$count = $result['total'];

// Prepare arrays for display
$groupNames = array();
$groupTypes = array();
$machinesCounts = array();
$maxScores = array();
$criticalCounts = array();
$highCounts = array();
$mediumCounts = array();
$lowCounts = array();
$totalCounts = array();
$params = array();

foreach ($data as $row) {
    $groupNames[] = $row['group_name'];
    $groupTypes[] = _T($row['group_type'], 'security');
    $machinesCounts[] = $row['machines_count'];
    $maxScores[] = SecurityBadge::score($row['max_cvss']);
    $criticalCounts[] = SecurityBadge::count($row['critical'], 'critical');
    $highCounts[] = SecurityBadge::count($row['high'], 'high');
    $mediumCounts[] = SecurityBadge::count($row['medium'], 'medium');
    $lowCounts[] = SecurityBadge::count($row['low'], 'low');
    $totalCounts[] = $row['total_cves'];
    $params[] = array(
        'group_id' => $row['group_id'],
        'group_name' => $row['group_name']
    );
}

// Actions - view details for this group
$detailAction = new ActionItem(_T("View Details", "security"), "groupDetail", "display", "", "security", "security");
$scanAction = new ActionPopupItem(_T("Scan this group", "security"), "ajaxStartScanGroup", "scan", "", "security", "security");
$excludeAction = new ActionPopupItem(_T("Exclude from reports", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
$excludeAction->setWidth(450);

// Display the list
if ($count > 0) {
    $n = new OptimizedListInfos($groupNames, _T("Group", "security"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($groupTypes, _T("Type", "security"));
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
    $n->addActionItem($excludeAction);
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    EmptyStateBox::show(
        _T("No groups found", "security"),
        _T("No groups with CVE data match your current filters. Try adjusting your search criteria or run a scan to collect vulnerability data.", "security")
    );
}
?>
