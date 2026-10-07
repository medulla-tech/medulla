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
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$software_name = $_GET["software_name"] ?? "";
$software_version = $_GET["software_version"] ?? "";
$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$severity = SecurityFilter::severity();

if ($software_name === '') {
    echo '<div class="empty-message"><p>' . _T("Invalid software", "security") . '</p></div>';
    return;
}

$result = xmlrpc_get_software_cves($software_name, $software_version, $start, $maxperpage, $filter, $severity);
$count = $result['total'] ?? 0;

if ($count > 0) {
    SecurityLists::cves($result['data'] ?? array(), $count, $filter);
} else {
    $message = ($filter !== '' || $severity)
        ? _T("No CVEs match your filter criteria", "security")
        : _T("No CVEs found for this software", "security");
    echo '<div class="empty-message"><p>' . $message . '</p></div>';
}
?>
