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

$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$location = SecurityFilter::location();

// A machine scan cannot start while a global scan is running
$summary = xmlrpc_get_dashboard_summary($location);
$globalScanRunning = ($summary['last_scan']['status'] ?? '') === 'running';

$result = xmlrpc_get_machines_summary(
    $start,
    $maxperpage,
    $filter,
    $location,
    SecurityFilter::platform(),
    false,
    SecurityFilter::group()
);
$data = $result['data'] ?? array();
$count = $result['total'] ?? 0;

$hostnames = array();
$params = array();
foreach ($data as $row) {
    $hostnames[] = htmlspecialchars($row['hostname']);
    $params[] = array(
        'id_glpi' => $row['id_glpi'],
        'hostname' => $row['hostname'],
        'machine_id' => $row['id_glpi'],
        'machine_name' => $row['hostname'],
        'back' => SecurityFilter::back()
    );
}

$detailAction = new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security");
if ($globalScanRunning) {
    $scanAction = new EmptyActionItem1(_T("Scan unavailable: a global scan is in progress", "security"), "ajaxScanMachine", "scang");
} else {
    $scanAction = new ActionPopupItem(_T("Scan Machine", "security"), "ajaxScanMachine", "scan", "", "security", "security");
    $scanAction->setWidth(500);
}
$excludeAction = new ActionPopupItem(_T("Exclude from reports", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
$excludeAction->setWidth(450);

if ($count > 0) {
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->setResizable();
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    SecurityColumns::add($n, $data, 'risk_score');
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
