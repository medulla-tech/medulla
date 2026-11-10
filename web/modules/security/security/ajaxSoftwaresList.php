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
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$result = xmlrpc_get_softwares_summary(
    $start,
    $maxperpage,
    $filter,
    SecurityFilter::location(),
    SecurityFilter::category(),
    SecurityFilter::platform()
);
$count = $result['total'] ?? 0;

if ($count > 0) {
    SecurityLists::softwares($result['data'] ?? array(), $count, $filter);
} else {
    EmptyStateBox::show(
        _T("No vulnerable software found", "security"),
        _T("No software with CVE data match your current filters.", "security")
    );
}
?>
