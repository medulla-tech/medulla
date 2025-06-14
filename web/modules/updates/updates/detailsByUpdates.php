<?php
/*
 * (c) 2025 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

$p = new PageGenerator(_T("Details by Updates", 'updates'));
$p->setSideMenu($sidemenu);

// Merged list
$p->display();
$params = ['entity' => $_GET['entity'], 'completename' => $_GET['completename']];
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDetailsByUpdates"), "container", $params, 'form');
$ajax->display();
$ajax->displayDivToUpdate();

// To have the gray and white list unmerged, comment the "merged list" section and uncomment below.

// $params = ['entity' => $_GET['entity'], 'completename' => $_GET['completename']];
// $ajaxGray = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDetailsByUpdatesGray"), "container-gray", $params, 'formGray');
// $ajaxGray->display();
// $ajaxGray->displayDivToUpdate();

// $ajaxWhite = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDetailsByUpdatesWhite"), "container-white", $params, 'formWhite');
// $ajaxWhite->display();
// $ajaxWhite->displayDivToUpdate();
