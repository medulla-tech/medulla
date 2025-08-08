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
 *
 */

require_once("modules/admin/includes/xmlrpc.php");

if (isset($_GET['entityId'])) {
    $entityId   = $_GET['entityId'];
    $entityName = $_GET['entityName'];

    $result = xmlrpc_delete_entity($entityId);

    if (is_array($result) && isset($result['success']) && !$result['success']) {
        new NotifyWidgetFailure(
            _T("Failed to delete the entity ", "admin") . $entityName . ".<br> " . $result['message']
        );
    } elseif (is_array($result) && isset($result['success']) && $result['success']) {
        new NotifyWidgetSuccess(
            _T("The entity " . $entityName . " was deleted successfully.", "admin")
        );
    } else {
        new NotifyWidgetFailure(
            _T("Unexpected error while deleting the entity ", "admin") . $entityName
        );
    }

    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}