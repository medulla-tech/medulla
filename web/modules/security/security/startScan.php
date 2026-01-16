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
 * Security Module - Start CVE Scan Action
 */

require_once("modules/security/includes/xmlrpc.php");

// Start the scan
$scan_id = xmlrpc_create_scan();

if ($scan_id) {
    $msg = sprintf(_T("CVE scan started successfully (ID: %s)", "security"), $scan_id);
    new NotifyWidgetSuccess($msg);
} else {
    new NotifyWidgetFailure(_T("Failed to start CVE scan", "security"));
}

// Redirect back to index
header("Location: " . urlStrRedirect("security/security/index"));
exit;
?>
