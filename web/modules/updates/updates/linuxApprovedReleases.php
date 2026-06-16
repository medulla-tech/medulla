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

$p = new PageGenerator(_T("Approved Linux releases", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'linux_approved_releases'
) {
    $stableValues = $_POST['is_current_stable'] ?? [];
    $recommendedValues = $_POST['is_recommended'] ?? [];

    $releaseIds = array_unique(array_merge(
        array_keys($stableValues),
        array_keys($recommendedValues)
    ));

    $updates = [];
    foreach ($releaseIds as $releaseId) {
        $updates[] = [
            (int) $releaseId,
            isset($stableValues[$releaseId]) ? (int) $stableValues[$releaseId] : 0,
            isset($recommendedValues[$releaseId]) ? (int) $recommendedValues[$releaseId] : 0,
        ];
    }

    $result = xmlrpc_update_linux_approved_releases($updates);
    $success = ($result === true) || (is_array($result) && !empty($result['success']));

    if ($success) {
        new NotifyWidgetSuccess(_T("Linux releases updated successfully.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Failed to update Linux releases.", "updates"));
    }

    header("Location: " . urlStrRedirect("updates/updates/linuxApprovedReleases"));
    exit;
}

$ajax = new AjaxFilter(
    urlStrRedirect("updates/updates/ajaxLinuxApprovedReleases"),
    "linuxApprovedReleasesContainer",
    [],
    "linuxApprovedReleasesForm"
);
$ajax->display();
$ajax->displayDivToUpdate();

?>