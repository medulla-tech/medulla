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

$p = new PageGenerator(_T("Restore file", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_id = htmlspecialchars($_GET["clientid"]);
$backup_id = htmlspecialchars($_GET["backupid"]);
$volume_name = htmlspecialchars($_GET["name"]);
$shahash = htmlspecialchars($_GET["shahash"]);
$path = dirname(htmlspecialchars($_GET["forward"]));
$filename = htmlspecialchars($_GET["name"]);

?>
<br>
<?php
if ($shahash == "")
{
    $client_restore_file = xmlrpc_client_download_backup_file($client_id, $backup_id, $path, $filename);
    if ($client_restore_file["ok"] == "true")
        $url = 'main.php?module=urbackup&submod=urbackup&action=all_files_backup&clientid='.$client_id.'&backupid='.$backup_id.'&volumename='.$path.'&restore=ok';
    else
        $url = 'main.php?module=urbackup&submod=urbackup&action=all_files_backup&clientid='.$client_id.'&backupid='.$backup_id.'&volumename='.$path.'&restore=ko';
}
else
{
    $client_restore_file_shahash = xmlrpc_client_download_backup_file_shahash($client_id, $backup_id, $path, $shahash, $filename);
    if ($client_restore_file_shahash["ok"] == "true")
        $url = 'main.php?module=urbackup&submod=urbackup&action=all_files_backup&clientid='.$client_id.'&backupid='.$backup_id.'&volumename='.$path.'&restore=ok';
    else
        $url = 'main.php?module=urbackup&submod=urbackup&action=all_files_backup&clientid='.$client_id.'&backupid='.$backup_id.'&volumename='.$path.'&restore=ko';
}

header("Location: ".$url);
?>