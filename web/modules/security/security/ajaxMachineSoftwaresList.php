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
 * Security Module - Ajax Machine Softwares List (grouped by software)
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$id_glpi = isset($_GET["id_glpi"]) ? intval($_GET["id_glpi"]) : 0;
$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

if ($id_glpi <= 0) {
    echo '<p class="error">' . _T("Invalid machine ID", "security") . '</p>';
    return;
}

$result = xmlrpc_get_machine_softwares_summary($id_glpi, $start, $maxperpage, $filter, SecurityFilter::category());
$data = $result['data'] ?? array();
$count = $result['total'] ?? 0;

$names = array();
$params = array();
foreach ($data as $row) {
    $names[] = SecurityColumns::software($row);
    $params[] = array(
        'software_name' => $row['software_name'],
        'software_version' => $row['software_version'],
        'back' => SecurityFilter::back()
    );
}

if ($count > 0) {
    $n = new OptimizedListInfos($names, _T("Software", "security"));
    $n->setResizable();
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    SecurityColumns::add($n, $data, 'max_cvss');
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View CVEs", "security"), "softwareDetail", "display", "", "security", "security"));
    $n->start = 0;
    $n->end = $count;
    $n->display();
} else {
    echo '<div class="empty-message"><p>' . _T("No vulnerable software found on this machine", "security") . '</p></div>';
}
?>
