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
 * Security Module - Ajax CVE List
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"] ?? "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;
$severity = SecurityFilter::severity();
$exploitedOnly = SecurityFilter::exploitedOnly();

$result = xmlrpc_get_cves(
    $start,
    $maxperpage,
    $filter,
    $severity,
    SecurityFilter::location(),
    'cvss_score',
    'desc',
    SecurityFilter::platform(),
    $exploitedOnly
);
$count = $result['total'] ?? 0;

if ($count > 0) {
    SecurityLists::cves($result['data'] ?? array(), $count, $filter, true);
} elseif ($filter !== '' || $severity || $exploitedOnly) {
    EmptyStateBox::show(
        _T("No CVEs found", "security"),
        _T("No CVEs match your filter criteria", "security")
    );
} else {
    EmptyStateBox::show(
        _T("No CVEs found", "security"),
        _T("Run a scan to populate the database.", "security")
    );
}
?>
