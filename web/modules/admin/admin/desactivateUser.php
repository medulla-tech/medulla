<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * file: desactivateUser.php
 */
require("modules/base/includes/users.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    exit;
}

verifyCSRFToken($_POST);

if (isset($_POST['userId'], $_POST['entities_id']) &&
    $_POST['userId'] !== '' &&
    $_POST['entities_id'] !== '') {

    $userId     = (int)$_POST['userId'];
    $isActive   = isset($_POST['is_active']) ? (int)$_POST['is_active'] : 0;
    $entityId   = (int)$_POST['entities_id'];
    $userName   = isset($_POST['userName']) ? htmlspecialchars($_POST['userName']) : _T("Unknown", "admin");
    $caller     = $_SESSION['glpi_user']['profile_name'];
    $token      = $_SESSION['glpi_user']['api_token'] ?? null;

    $result = xmlrpc_toggle_user_active($userId, $caller, $token);

    if ($result !== null) {
        $newStatus = $isActive ? "deactivated" : "activated";

        new NotifyWidgetSuccess(
            sprintf(
                _T("User <strong>%s</strong> has been <strong>%s</strong> successfully.", "admin"),
                $userName,
                _T($newStatus, "admin")
            )
        );
    } else {
        new NotifyWidgetFailure(
            sprintf(
                _T("Failed to update status for user <strong>%s</strong>.", "admin"),
                $userName
            )
        );
    }

    // redirection to the list of entity users
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        [
            'entityId'   => $entityId,
            'entityName' => $_POST['entity_name'] ?? ''
        ]
    ));
    exit;
} else {
    new NotifyWidgetFailure(_T("Missing parameters: User ID or Entity ID not provided.", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}


