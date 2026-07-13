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
 * Adds an ACL profile: creates it in GLPI (cloned from the template profile)
 * and registers it in Medulla's acl_profiles. Its own action so the right can
 * be granted/revoked independently of the ACL matrix (admin#admin#addAclProfile).
 */
require_once("modules/admin/includes/xmlrpc.php");

$newName = trim((string)($_POST['profile_name'] ?? ''));
// Allow Unicode letters/digits (French/Spanish names like "Gestionnaire").
if ($newName === '' || !preg_match('/^[\p{L}\p{N}_\- ]+$/u', $newName)) {
    new NotifyWidgetFailure(_T("Invalid profile name", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}

$res = xmlrpc_create_glpi_profile_and_register($newName);
if (is_array($res) && !empty($res['ok'])) {
    if (!empty($res['created_in_glpi'])) {
        if (!empty($res['cloned_from'])) {
            new NotifyWidgetSuccess(sprintf(_T("Profile '%s' created in GLPI (cloned from '%s') and added to Medulla", "admin"), $newName, $res['cloned_from']));
        } else {
            new NotifyWidgetSuccess(sprintf(_T("Profile '%s' created in GLPI and added to Medulla", "admin"), $newName));
        }
    } else {
        new NotifyWidgetSuccess(sprintf(_T("Existing GLPI profile '%s' linked to Medulla", "admin"), $newName));
    }
} else {
    $errMsg = (is_array($res) && !empty($res['error'])) ? $res['error'] : _T("Unknown error", "admin");
    new NotifyWidgetFailure(sprintf(_T("Failed to add profile '%s': %s", "admin"), $newName, $errMsg));
}
header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
exit;
