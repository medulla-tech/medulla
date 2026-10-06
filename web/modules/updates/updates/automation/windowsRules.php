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
 */

require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");

if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'montableau' && isset($_POST['entityid'])
) {
    $submittedCheckValues = $_POST['check'] ?? [];
    $result = [];
    foreach ($submittedCheckValues as $key => $value) {
        $result[] = [$key, $value];
    }

    $success = xmlrpc_update_auto_approve_rules($result, $_POST['entityid']);

    if ($success) {
        new NotifyWidgetSuccess(_T("Rules updated successfully.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Failed to update rules.", "updates"));
    }
}

$selectedEntityIdRaw = $_POST['entityid'] ?? $_GET['entityid'] ?? null;
$selectedEntityIdStr = is_string($selectedEntityIdRaw) ? $selectedEntityIdRaw : strval($selectedEntityIdRaw);
$selectedEntityIdStr = preg_replace('/^UUID/i', '', $selectedEntityIdStr);
$selectedEntityId = ($selectedEntityIdStr !== null && $selectedEntityIdStr !== '') ? (int) $selectedEntityIdStr : null;

generateEntityPage("", "ajaxApproveRules", null, 'updates', $selectedEntityId);
?>
