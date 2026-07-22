<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * Confirms then deletes an ACL profile from both Medulla (acl_profiles +
 * acl_profile_features) and GLPI (via REST). Follows the same pattern as
 * deleteCluster.php / deleteEntity.php (PopupForm + POST bconfirm).
 */
require_once("modules/admin/includes/xmlrpc.php");

$profileName = isset($_REQUEST['profile_name']) ? (string)$_REQUEST['profile_name'] : '';
$protectedProfiles = ['Super-Admin', 'Admin', 'Technician'];

if ($profileName === '' || in_array($profileName, $protectedProfiles, true)) {
    new NotifyWidgetFailure(_T("Built-in profiles cannot be deleted", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}

if (isset($_POST["bconfirm"])) {
    $tokenuser = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']))
        ? ($_SESSION['glpi_user']['api_token'] ?? null) : null;
    $res = xmlrpc_delete_acl_profile($profileName, $tokenuser);

    if (is_array($res) && !empty($res['ok'])) {
        if (!empty($res['deleted_in_glpi'])) {
            new NotifyWidgetSuccess(sprintf(_T("Profile '%s' deleted from Medulla and GLPI", "admin"), $profileName));
        } else {
            $note = !empty($res['error']) ? $res['error'] : _T("not found in GLPI", "admin");
            new NotifyWidgetSuccess(sprintf(_T("Profile '%s' removed from Medulla (GLPI: %s)", "admin"), $profileName, $note));
        }
    } else {
        $err = (is_array($res) && !empty($res['error'])) ? $res['error'] : _T("Unknown error", "admin");
        new NotifyWidgetFailure(sprintf(_T("Failed to delete profile '%s': %s", "admin"), $profileName, $err));
    }
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}

$f = new PopupForm(_T("Delete profile", "admin") . " : " . htmlspecialchars($profileName));
$f->setLevel('danger');
$f->addText(sprintf(_T("All ACL settings of profile '%s' will be removed in Medulla and GLPI. This cannot be undone.", "admin"), htmlspecialchars($profileName)));
$hidden = new HiddenTpl("profile_name");
$f->add($hidden, array("value" => $profileName, "hide" => True));
$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
