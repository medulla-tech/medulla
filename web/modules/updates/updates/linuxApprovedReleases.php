<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");

if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'linux_approved_releases'
) {
    verifyCSRFToken($_POST);

    // $stableValues = $_POST['is_current_stable'] ?? []; // Colonne conservee pour reprise si besoin.
    $latestMajorVersionValues = $_POST['is_latest_major_version'] ?? ($_POST['is_recommended'] ?? []);
    $entityIdRaw = $_POST['entityid'] ?? ($_GET['entity'] ?? null);
    $entityIdStr = is_string($entityIdRaw) ? $entityIdRaw : strval($entityIdRaw);
    $entityIdStr = preg_replace('/^UUID/i', '', $entityIdStr);
    $entityId = ($entityIdStr !== null && $entityIdStr !== '') ? (int) $entityIdStr : null;

    if ($entityId === null) {
        new NotifyWidgetFailure(_T("Missing entity selection.", "updates"));
        header("Location: " . urlStrRedirect("updates/updates/linuxApprovedReleases"));
        exit;
    }

    $currentReleases = xmlrpc_get_linux_approved_releases($entityId);
    $currentStableByReleaseId = [];
    if (is_array($currentReleases) && isset($currentReleases['id']) && is_array($currentReleases['id'])) {
        foreach ($currentReleases['id'] as $index => $releaseId) {
            $currentStableByReleaseId[(int) $releaseId] = (int) ($currentReleases['is_current_stable'][$index] ?? 0);
        }
    }

    $releaseIds = array_unique(array_merge(
        // array_keys($stableValues),
        array_keys($latestMajorVersionValues)
    ));

    $updates = [];
    foreach ($releaseIds as $releaseId) {
        $releaseIdInt = (int) $releaseId;
        $updates[] = [
            $releaseIdInt,
            $currentStableByReleaseId[$releaseIdInt] ?? 0,
            isset($latestMajorVersionValues[$releaseId]) ? (int) $latestMajorVersionValues[$releaseId] : 0,
        ];
    }

    $result = xmlrpc_update_linux_approved_releases($updates, $entityId);
    $success = ($result === true) || (is_array($result) && !empty($result['success']));

    if ($success) {
        new NotifyWidgetSuccess(_T("Linux releases updated successfully.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Failed to update Linux releases.", "updates"));
    }

   // header("Location: " . urlStrRedirect("updates/updates/linuxApprovedReleases?entityid=" . $entityId));
   // exit;
}

$selectedEntityIdRaw = $_POST['entityid'] ?? $_GET['entityid'] ?? null;
$selectedEntityIdStr = is_string($selectedEntityIdRaw) ? $selectedEntityIdRaw : strval($selectedEntityIdRaw);
$selectedEntityIdStr = preg_replace('/^UUID/i', '', $selectedEntityIdStr);
$selectedEntityId = ($selectedEntityIdStr !== null && $selectedEntityIdStr !== '') ? (int) $selectedEntityIdStr : null;
generateEntityPage(_T("Approved Linux releases", "updates"),
                   "ajaxLinuxApprovedReleases",
                   $sidemenu,
                   'updates',
                   $selectedEntityId);
?>