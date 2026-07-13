<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/majorDetailsByMachinesLinux.php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * file: modules/updates/updates/majorDetailsByMachinesLinux.php
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");
require_once("includes/utils.inc.php");
/* if (function_exists('cleanNavParams')) {
    cleanNavParams($_GET);
} else {
    
} */

$entityName = !empty($_GET['name']) ? htmlentities($_GET['name']) : "";
$distribution = !empty($_GET['distribution']) ? htmlentities($_GET['distribution']) : "linux";
$title = sprintf(_T("List of machines to be upgraded (%s)", "updates"), ucfirst($distribution));
if ($entityName) {
    $title .= ' - ' . $entityName;
}

$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();


unset($_GET['action'], $_GET['module'], $_GET['submod'], $_GET['tab'], $_GET['page']);

$ajax = new AjaxFilter(
    urlStrRedirect("updates/updates/ajaxMajorDetailsByMachinesLinux"),
    "container",
    $_GET
);
$ajax->display();
$ajax->displayDivToUpdate(); 
?>