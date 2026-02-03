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
 * Security Module - Scan Machine Popup
 */

require_once("modules/security/includes/xmlrpc.php");

$id_glpi = isset($_GET['id_glpi']) ? intval($_GET['id_glpi']) : (isset($_POST['id_glpi']) ? intval($_POST['id_glpi']) : 0);
$hostname = isset($_GET['hostname']) ? $_GET['hostname'] : (isset($_POST['hostname']) ? $_POST['hostname'] : '');

if (isset($_POST['bconfirm'])) {
    // Start the scan for this machine
    $result = xmlrpc_scan_machine($id_glpi);

    if ($result && isset($result['success']) && $result['success']) {
        $vulns = isset($result['vulnerabilities_found']) ? $result['vulnerabilities_found'] : 0;
        new NotifyWidgetSuccess(sprintf(_T("Scan completed for %s. %d vulnerabilities found.", "security"), htmlspecialchars($hostname), $vulns));
    } else {
        $error = isset($result['error']) ? $result['error'] : _T("Unknown error", "security");
        new NotifyWidgetFailure(sprintf(_T("Failed to scan %s: %s", "security"), htmlspecialchars($hostname), htmlspecialchars($error)));
    }

    header("Location: " . urlStrRedirect("security/security/machines"));
    exit;
}

// Show confirmation popup
$title = sprintf(_T("Scan Machine: %s", "security"), htmlspecialchars($hostname));
$f = new PopupForm($title);

// Hidden fields
$f->add(new HiddenTpl("id_glpi"), array("value" => $id_glpi, "hide" => True));
$f->add(new HiddenTpl("hostname"), array("value" => htmlspecialchars($hostname), "hide" => True));

$f->addText("<br/>" . _T("Start a CVE vulnerability scan on this machine?", "security"));
$f->addText("<br/><br/><em>" . _T("The scan runs in background.", "security") . "</em><br/>");

$f->addValidateButton("bconfirm", _T("Start Scan", "security"));
$f->addCancelButton("bback");
$f->display();
?>
