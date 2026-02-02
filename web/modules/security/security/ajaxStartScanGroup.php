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
 * Security Module - AJAX Start Scan by Group Popup
 */

require_once("modules/security/includes/xmlrpc.php");

$group_id = isset($_GET['group_id']) ? intval($_GET['group_id']) : 0;
$group_name = isset($_GET['group_name']) ? htmlspecialchars($_GET['group_name']) : '';

if ($group_id <= 0) {
    new NotifyWidgetFailure(_T("Invalid group", "security"));
    return;
}

if (isset($_POST['bconfirm'])) {
    // Start the scan for group
    $scan_id = xmlrpc_create_scan_group($group_id);

    if ($scan_id) {
        $msg = sprintf(_T("CVE scan started for group '%s' (ID: %s). The scan runs in background.", "security"), $group_name, $scan_id);
        new NotifyWidgetSuccess($msg);
    } else {
        new NotifyWidgetFailure(_T("Failed to start CVE scan. Please check the configuration.", "security"));
    }

    // Redirect back to groups page
    header("Location: " . urlStrRedirect("security/security/groups"));
    exit;
}

// Show confirmation form using PopupForm
$title = sprintf(_T("Scan Group: %s", "security"), $group_name);
$f = new PopupForm($title);
$f->addText("<br/>" . _T("Start a CVE vulnerability scan on machines in this group?", "security"));
$f->addText("<br/><br/><em>" . _T("The scan runs in background.", "security") . "</em><br/>");
$f->addValidateButton("bconfirm", _T("Start Scan", "security"));
$f->addCancelButton("bback");
$f->display();
?>
