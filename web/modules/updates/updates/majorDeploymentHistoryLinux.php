<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/majorDeploymentHistoryLinux.php

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");
require_once("includes/utils.inc.php");

$entityName = !empty($_GET['name']) ? $_GET['name'] : (!empty($_GET['completename']) ? $_GET['completename'] : "");
$distribution = !empty($_GET['distribution']) ? $_GET['distribution'] : "linux";
$title = sprintf(_T("Linux major deployment history (%s)", "updates"), htmlentities(ucfirst($distribution)));
if ($entityName !== "") {
    $title .= " - " . htmlentities($entityName);
}

$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();

unset($_GET['action'], $_GET['module'], $_GET['submod'], $_GET['tab'], $_GET['page']);

$ajax = new AjaxFilter(
    urlStrRedirect("updates/updates/ajaxMajorDeploymentHistoryLinux"),
    "container",
    $_GET,
    "MajorDeploymentHistoryLinux"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
