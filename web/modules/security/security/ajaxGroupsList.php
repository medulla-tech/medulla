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

$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$result = xmlrpc_get_groups_summary($start, $maxperpage, $filter, $_SESSION['login'] ?? '');
$data = $result['data'] ?? array();
$count = $result['total'] ?? 0;

$names = array();
$types = array();
$machines = array();
$params = array();
foreach ($data as $row) {
    $names[] = htmlspecialchars($row['group_name']);
    $types[] = htmlspecialchars(_T($row['group_type'], 'security'));
    $machines[] = intval($row['machines_count']);
    $params[] = array(
        'group_id' => $row['group_id'],
        'group_name' => $row['group_name'],
        'back' => SecurityFilter::back()
    );
}

$excludeAction = new ActionPopupItem(_T("Exclude from reports", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
$excludeAction->setWidth(450);

if ($count > 0) {
    $n = new OptimizedListInfos($names, _T("Group", "security"));
    $n->setResizable();
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($types, _T("Type", "security"));
    SecurityColumns::add($n, $data, 'max_cvss');
    $n->addExtraInfoCentered($machines, _T("Machines", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View Details", "security"), "groupDetail", "display", "", "security", "security"));
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
