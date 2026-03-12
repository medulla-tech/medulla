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
 * Security Module - AJAX Start Scan Popup
 */

require_once("modules/security/includes/xmlrpc.php");

if (isset($_POST['bconfirm'])) {
    // Check if a scan is already running
    $summary = xmlrpc_get_dashboard_summary('');
    if (isset($summary['last_scan']['status']) && $summary['last_scan']['status'] === 'running') {
        new NotifyWidgetWarning(_T("A global scan is already in progress. Please wait for it to finish.", "security"));
        header("Location: " . urlStrRedirect("security/security/index"));
        exit;
    }

    // Start the scan
    $scan_id = xmlrpc_create_scan();

    if ($scan_id) {
        $msg = sprintf(_T("CVE scan started successfully (ID: %s). The scan runs in background.", "security"), $scan_id);
        new NotifyWidgetSuccess($msg);
    } else {
        new NotifyWidgetFailure(_T("Failed to start CVE scan. Please check the configuration.", "security"));
    }

    // Redirect back to index page
    header("Location: " . urlStrRedirect("security/security/index"));
    exit;
}

// Show confirmation form using PopupForm
$title = _T("Start CVE Scan", "security");
$f = new PopupForm($title);
$f->addText("<br/>" . _T("Start a CVE vulnerability scan on all machines?", "security"));
$f->addText("<br/><br/><em>" . _T("The scan runs in background.", "security") . "</em><br/>");
$f->addValidateButton("bconfirm", _T("Start Scan", "security"));
$f->addCancelButton("bback");
$f->display();
?>
