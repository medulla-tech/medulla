<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/deployWinGroup.php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Deploy an update", "updates"), $sidemenu);
    return;
}

$group = updatesWinRequestGroup();

if (!$group) {
    $p = new PageGenerator(_T("Deploy an update", "updates"));
    $p->setSideMenu($sidemenu);
    $p->display();
    EmptyStateBox::show(_T("Unknown group.", "updates"));
    return;
}

$p = new PageGenerator(sprintf(_T("Deploy an update on group %s", "updates"),
                               htmlspecialchars($group['name'], ENT_QUOTES, 'UTF-8')));
$p->setSideMenu($sidemenu);
$p->display();
if (hasCorrectAcl("base", "computers", "display")) {
    $groupUrl = urlStrRedirect("base/computers/display",
                               array('id' => $group['id'], 'gid' => $group['id'], 'groupname' => $group['name']));
    echo '<a class="updates-back-link" href="' . htmlspecialchars($groupUrl, ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars(_T("See the group machines", "updates"), ENT_QUOTES, 'UTF-8') . '</a>';
}
updatesStaleNotice();

$linux = xmlrpc_get_linux_group_summary($group['id']);
$windows = xmlrpc_get_windows_group_updates($group['id']);
if (updatesReadFailed($linux) || updatesReadFailed($windows)) {
    updatesReadFailedBox();
    return;
}

$hasLinux = (updatesWinNumber($linux['machines'] ?? null) ?? 0) > 0;
if ($hasLinux) {
    updatesLinuxGroupSummary($group['id'], $linux);
}
if (!$hasLinux || (updatesWinNumber($windows['machines'] ?? null) ?? 0) > 0) {
    $ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDeployWinGroup"), "container",
                           array('gid' => $group['id']));
    $ajax->display();
    $ajax->displayDivToUpdate();
}
?>
