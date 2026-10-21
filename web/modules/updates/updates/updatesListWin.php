<?php
// SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/updatesListWin.php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Approval", "updates"), $sidemenu);
    return;
}

$entity = updatesWinProductsEntity();
$currentStatus = updatesApprovalStatus($_GET['status'] ?? null);

// Bulk action on the selected Windows rows of the current status.
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['approval_bulk'])) {
    verifyCSRFToken($_POST);
    $status = is_string($_POST['approval_bulk']) ? $_POST['approval_bulk'] : '';
    $page = updatesApprovalActionPage($status);
    $ids = array();
    foreach ((array) ($_POST['update_ids'] ?? array()) as $value) {
        $id = updatesApprovalId($value);
        if ($id !== null) {
            $ids[$id] = true;
        }
    }
    $messages = array(
        'approved' => _T("Selection approved.", "updates"),
        'declined' => _T("Selection declined.", "updates"),
    );
    if (!$entity || !isset($messages[$status]) || !hasCorrectAcl("updates", "updates", $page)) {
        new NotifyWidgetFailure(_T("The selection could not be saved.", "updates"));
    } elseif (empty($ids)) {
        new NotifyWidgetFailure(_T("No update selected.", "updates"));
    } elseif (xmlrpc_set_windows_approval(updatesEntityId($entity), array_keys($ids), $status) === true) {
        new NotifyWidgetSuccess($messages[$status]);
    } else {
        new NotifyWidgetFailure(_T("The selection could not be saved.", "updates"));
    }
    header("Location: " . updatesApprovalUrl($entity, $currentStatus));
    exit;
}

$p = new PageGenerator(_T("Approval", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
updatesStaleNotice();

if (!$entity) {
    EmptyStateBox::show(_T("No entity available for this user.", "updates"));
    return;
}

$p = new TabbedPageGenerator();
$tabParams = array('location' => $entity['uuid']);
$p->addTab("tabwin", _T("Windows", "updates"), "", "modules/updates/updates/approval/windowsApprovals.php", $tabParams);
$p->addTab("tablinux", _T("Linux", "updates"), "", "modules/updates/updates/approval/windowsApprovals.php", $tabParams);
$p->display();
?>
