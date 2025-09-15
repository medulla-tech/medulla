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

if (isset($_GET['userId']) && !empty($_GET['userId']) &&
    isset($_GET['entities_id']) && !empty($_GET['entities_id'])) {

    $userId     = (int)$_GET['userId'];
    $isActive   = isset($_GET['is_active']) ? (int)$_GET['is_active'] : 0;
    $entityId   = (int)$_GET['entities_id'];
    $userName   = isset($_GET['userName']) ? htmlspecialchars($_GET['userName']) : _T("Unknown", "admin");
    $token      = $_SESSION['glpi_user']['api_token'] ?? null;

    $result = xmlrpc_toggle_user_active($userId, $token);

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
            'entityName' => $_GET['entity_name'] ?? ''
        ]
    ));
    exit;
} else {
    new NotifyWidgetFailure(_T("Missing parameters: User ID or Entity ID not provided.", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}


