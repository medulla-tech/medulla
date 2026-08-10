<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
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
require_once("modules/urbackup/includes/functions.inc.php");

$clientname = (isset($_GET["clientname"])) ? htmlentities($_GET['clientname']) : "";
$p = new PageGenerator(_T("Backups List ".$clientname, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$params = array(
    "client_id" => (isset($_GET["clientid"])) ? htmlentities($_GET['clientid']) : "",
    "clientname" => (isset($_GET["clientname"])) ? htmlentities($_GET['clientname']) : "",
    "jidmachine" => (isset($_GET["jidmachine"])) ? htmlentities($_GET['jidmachine']) : "",
    "groupid" => (isset($_GET["groupid"])) ? htmlentities($_GET['groupid']) : "",
    "groupname" => (isset($_GET["groupname"])) ? htmlentities($_GET['groupname']) : "",
    "groupuuid" => (isset($_GET["groupuuid"])) ? htmlentities($_GET['groupuuid']) : "",
    "authkey" => (isset($_GET["authkey"])) ? htmlentities($_GET['authkey']) : "",
);

$ajax = new AjaxFilter(urlStrRedirect("urbackup/urbackup/ajaxList_backups"), "container", $params);

$ajax->display();
$ajax->displayDivToUpdate();
?>
