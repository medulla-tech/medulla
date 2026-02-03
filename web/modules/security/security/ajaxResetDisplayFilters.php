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
 * Security Module - AJAX Reset Display Filters Popup
 */

require_once("modules/security/includes/xmlrpc.php");

$currentUser = $_SESSION['login'] ?? 'unknown';

if (isset($_POST['bconfirm'])) {
    $result = xmlrpc_reset_display_policies($currentUser);

    if ($result) {
        new NotifyWidgetSuccess(_T("Display filters reset to defaults", "security"));
    } else {
        new NotifyWidgetFailure(_T("Failed to reset display filters", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabfilters")));
    exit;
}

// Show confirmation popup
$f = new PopupForm(_T("Reset Display Filters", "security"));
$f->addText("<br/>" . _T("Are you sure you want to reset display filters to default values?", "security") . "<br/><br/>");
$f->addValidateButton("bconfirm", _T("Reset", "security"));
$f->addCancelButton("bback");
$f->display();
?>
