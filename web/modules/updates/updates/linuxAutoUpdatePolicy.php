<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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

// Traitement du formulaire de sauvegarde
if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'linux_auto_update_policy'
) {
    verifyCSRFToken($_POST);

    $kernelValues   = $_POST['auto_update_kernel']   ?? [];
    $securityValues = $_POST['auto_update_security'] ?? [];
    $otherValues    = $_POST['auto_update_other']    ?? [];

    $policyIds = array_unique(array_merge(
        array_keys($kernelValues),
        array_keys($securityValues),
        array_keys($otherValues)
    ));

    $updates = [];
    foreach ($policyIds as $policyId) {
        $updates[] = [
            'id'                   => (int) $policyId,
            'auto_update_kernel'   => isset($kernelValues[$policyId])   ? (int) $kernelValues[$policyId]   : 0,
            'auto_update_security' => isset($securityValues[$policyId]) ? (int) $securityValues[$policyId] : 0,
            'auto_update_other'    => isset($otherValues[$policyId])    ? (int) $otherValues[$policyId]    : 0,
        ];
    }

    $result  = xmlrpc_update_linux_auto_update_policy($updates);
    $success = is_array($result) && !empty($result['success']);

    if ($success) {
        new NotifyWidgetSuccess(_T("Auto-update policies saved.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Failed to save auto-update policies.", "updates"));
    }

    // header("Location: " . urlStrRedirect("updates/updates/linuxAutoUpdatePolicy"));
    // exit;
}

$selectedEntityIdRaw = $_POST['selected_location'] ?? $_GET['selected_location'] ?? null;
$selectedEntityIdStr = is_string($selectedEntityIdRaw) ? $selectedEntityIdRaw : strval($selectedEntityIdRaw);
$selectedEntityIdStr = preg_replace('/^UUID/i', '', $selectedEntityIdStr);
$selectedEntityId = ($selectedEntityIdStr !== null && $selectedEntityIdStr !== '') ? (int) $selectedEntityIdStr : null;

generateEntityPage(_T("Linux Auto-Update Policy", "updates"),
                   "ajaxLinuxAutoUpdatePolicy",
                   $sidemenu,
                   'updates',
                   $selectedEntityId);

