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

$client_id = htmlspecialchars($_GET["clientid"]);
$client_name = htmlspecialchars($_GET["clientname"]);
$groupe_name = htmlspecialchars($_GET["groupname"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);

$p = new PageGenerator(_T("Restart service", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$restart_service = xmlrpc_restart_urbackup_service($jidMachine);
?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$client_id."&clientname=".$client_name."&groupname=".$groupe_name."&jidmachine=".$jidMachine."&restart_service=true";

header("Location: ".$url);
?>
