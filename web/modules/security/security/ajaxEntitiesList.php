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
 * Security Module - Ajax Entities List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$result = xmlrpc_get_entities_summary($start, $maxperpage, $filter, SecurityFilter::location());
$data = $result['data'] ?? array();
$count = $result['total'] ?? 0;

$names = array();
$machines = array();
$params = array();
foreach ($data as $row) {
    $names[] = htmlspecialchars($row['entity_fullname']);
    $machines[] = intval($row['machines_count']);
    $params[] = array('location' => 'UUID' . intval($row['entity_id']));
}

if ($count > 0) {
    $n = new OptimizedListInfos($names, _T("Entity", "security"));
    $n->setResizable();
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    SecurityColumns::add($n, $data, 'max_cvss');
    $n->addExtraInfoCentered($machines, _T("Machines", "security"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View Machines", "security"), "machines", "display", "", "security", "security"));
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    EmptyStateBox::show(
        _T("No entities found", "security"),
        _T("No entities with CVE data match your current filters. Try adjusting your search criteria or run a scan to collect vulnerability data.", "security")
    );
}
?>
