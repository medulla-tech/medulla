<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse
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

$type_backup = htmlspecialchars($_GET["backuptype"]);
$client_id = htmlspecialchars($_GET["clientid"]);

$p = new PageGenerator(_T("Start ".$type_backup." backup", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

if ($type_backup == "incremental")
    $backup = xmlrpc_create_backup_incremental_file($client_id);
else
    $backup = xmlrpc_create_backup_full_file($client_id);


$start_backup = $backup["result"];
?>
<br>
<?php
foreach($start_backup as $back)
{
    if ($back["start_ok"] == "1")
    {
        $url = 'main.php?module=urbackup&submod=urbackup&action=index&clientid='.$client_id;
        header("Location: ".$url);  
    }
    else
    {
        $backupstate = "false";
        $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$client_id."&backupstate=".$backupstate."&backuptype=".$type_backup;
        header("Location: ".$url);  
    }
}
?>
