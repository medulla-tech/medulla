<?php
/*
 * (c) 2022-2024 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse.
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

if(empty($_SESSION['urbackup'])){
    $_SESSION['urbackup'] = [
        'files'=>[],
        'folders' => []
    ];
}

$client_name = htmlspecialchars($_GET["clientname"]);

$p = new PageGenerator(_T("Content list for ".$client_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$params = $_GET;
unset($params['action']);
$ajax = new AjaxFilter(urlStrRedirect("urbackup/urbackup/ajaxAll_files_backup"), 'container', $params);
$ajax->display();
$ajax->displayDivToUpdate();
