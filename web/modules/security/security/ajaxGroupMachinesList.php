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
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$group_id = isset($_GET["group_id"]) ? intval($_GET["group_id"]) : 0;
$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

if ($group_id <= 0) {
    echo '<div class="empty-message"><p>' . _T("Invalid group", "security") . '</p></div>';
    return;
}

$result = xmlrpc_get_group_machines($group_id, $start, $maxperpage, $filter);
$data = $result['data'] ?? array();
$count = $result['total'] ?? 0;

$hostnames = array();
$params = array();
foreach ($data as $row) {
    $hostnames[] = htmlspecialchars($row['hostname']);
    $params[] = array('id_glpi' => $row['id_glpi'], 'hostname' => $row['hostname'], 'back' => SecurityFilter::back());
}

if ($count > 0) {
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->setResizable();
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    SecurityColumns::add($n, $data, 'risk_score');
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security"));
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message"><p>' . _T("No machines in this group", "security") . '</p></div>';
}
?>
