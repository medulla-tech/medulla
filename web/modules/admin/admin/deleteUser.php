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
 * file: deleteUser.php
 */
require("modules/base/includes/users.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    exit;
}

verifyCSRFToken($_POST);

if (($_GET['action'] ?? '') === 'deleteUser' && isset($_POST['userId'], $_POST['userName'])) {
    $userId     = (int) $_POST['userId'];
    $login      = htmlspecialchars((string) $_POST['userName'], ENT_QUOTES);
    $entityId   = isset($_POST['entities_id']) ? (int) $_POST['entities_id'] : 0;
    $entityName = isset($_POST['entity_name']) ? htmlspecialchars((string) $_POST['entity_name'], ENT_QUOTES) : _T("Unknown", "admin");

    try {
        // Deletion in GLPI
        $res = xmlrpc_delete_and_purge_user($userId);

        $ok = is_array($res) && (
            (!empty($res['ok']) && $res['ok'] === true) ||
            (isset($res['message']) && in_array($res['message'], ['purged', 'already absent'], true))
        );

        if ($ok) {
            // Deletion in the system (LDAP)
            del_user($login, "on");

            new NotifyWidgetSuccess(
                sprintf(
                    _T("User <strong>%s</strong> deleted successfully from entity <strong>%s</strong>.", "admin"),
                    $login,
                    $entityName
                )
            );
        } else {
            $msg = is_array($res)
                ? ($res['error'] ?? $res['message'] ?? _T("Unknown error", "admin"))
                : _T("Unknown error", "admin");

            new NotifyWidgetFailure(
                sprintf(
                    _T("Failed to delete user <strong>%s</strong> from entity <strong>%s</strong>: %s", "admin"),
                    $login,
                    $entityName,
                    $msg
                )
            );
        }
    } catch (Throwable $e) {
        new NotifyWidgetFailure(
            sprintf(
                _T("Failed to delete user <strong>%s</strong> from entity <strong>%s</strong>: %s", "admin"),
                $login,
                $entityName,
                $e->getMessage()
            )
        );
    }

    // redirection to the list of entity users
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $entityId, 'entityName' => $entityName]
    ));
    exit;
}