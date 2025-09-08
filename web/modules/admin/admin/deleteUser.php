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

if (isset($_GET['action'], $_GET['userId'], $_GET['userName']) && $_GET['action'] === 'deleteUser') {
    $userId     = (int) $_GET['userId'];
    $login      = (string) $_GET['userName'];
    $entityId   = isset($_GET['entities_id']) ? (int) $_GET['entities_id'] : 0;
    $entityName = isset($_GET['entity_name']) ? (string) $_GET['entity_name'] : '';

    try {
        $res = xmlrpc_delete_and_purge_user($userId);

        $ok = is_array($res) && (
            (!empty($res['ok']) && $res['ok'] === true) ||
            (isset($res['message']) && in_array($res['message'], ['purged','already absent'], true))
        );

        if ($ok) {
            del_user($login, "on");
            new NotifyWidgetSuccess(_T("The user ", "admin") . $login . " " . _T("deleted successfully.", "admin"));
        } else {
            $msg = is_array($res) ? ($res['error'] ?? $res['message'] ?? 'DELETE_FAILED') : 'DELETE_FAILED';
            new NotifyWidgetFailure(_T("Deletion failed: ", "admin") . $msg);
        }
    } catch (Throwable $e) {
        new NotifyWidgetFailure(_T("Deletion failed: ", "admin") . $e->getMessage());
    }

    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $entityId, 'entityName' => $entityName]
    ));
    exit;
}