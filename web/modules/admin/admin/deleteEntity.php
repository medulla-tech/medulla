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
 * file: deleteEntity.php
 */
require_once("modules/admin/includes/xmlrpc.php");

if (isset($_GET['entityId'])) {
    $entityId   = (int)$_GET['entityId'];
    $entityName = htmlspecialchars($_GET['entityName'] ?? _T("Unknown", "admin"), ENT_QUOTES, 'UTF-8');

    $result = xmlrpc_delete_entity($entityId);

    if (is_array($result)) {
        if (isset($result['success']) && $result['success']) {
            new NotifyWidgetSuccess(
                sprintf(
                    _T("Entity <strong>%s</strong> deleted successfully.", "admin"),
                    $entityName
                )
            );
        } elseif (isset($result['success']) && !$result['success']) {
            new NotifyWidgetFailure(
                sprintf(
                    _T("Failed to delete entity <strong>%s</strong>.<br>Reason: %s", "admin"),
                    $entityName,
                    htmlspecialchars($result['message'] ?? _T("Unknown error", "admin"), ENT_QUOTES, 'UTF-8')
                )
            );
        } else {
            new NotifyWidgetFailure(
                sprintf(
                    _T("Unexpected response while deleting entity <strong>%s</strong>.", "admin"),
                    $entityName
                )
            );
        }
    } else {
        new NotifyWidgetFailure(
            sprintf(
                _T("Failed to delete entity <strong>%s</strong>. Invalid server response.", "admin"),
                $entityName
            )
        );
    }

    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}