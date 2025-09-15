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
 * file: deleteProfileUser.php
 */
require("modules/base/includes/users.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

if (isset($_GET['userId']) && !empty($_GET['userId']) &&
    isset($_GET['profile_id']) && !empty($_GET['profile_id']) &&
    isset($_GET['entities_id']) && !empty($_GET['entities_id'])) {

    $userId     = $_GET['userId'];
    $profileId  = $_GET['profile_id'];
    $entitiesId = $_GET['entities_id'];
    $token      = $_SESSION['glpi_user']['api_token'] ?? null;

    $result = xmlrpc_delete_user_profile_on_entity($userId, $profileId, $entitiesId, $token);

    if ($result) {
        new NotifyWidgetSuccess(
            _T("The Profile " . $_GET['profil_name'] . " has been removed for the user " . $_GET['userName'], "admin")
        );
        header("Location: " . urlStrRedirect(
            "admin/admin/listUsersofEntity",
            [
                'entityId' => $_GET['entities_id'],
                'entityName' => $_GET['entity_name'] ?? ''
            ]
        ));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to remove profile", "admin"));
    }
} else {
    new NotifyWidgetFailure(_T("Missing parameters to delete profile", "admin"));
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        [
            'entityId' => $_GET['entities_id'] ?? '',
            'entityName' => $_GET['entity_name'] ?? ''
        ]
    ));
    exit;
}
?>
