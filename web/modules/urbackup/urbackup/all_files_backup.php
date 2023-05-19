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
$backup_id = htmlspecialchars($_GET["backupid"]);
$volume_name = htmlspecialchars($_GET["volumename"]);
$groupname = htmlspecialchars($_GET["groupname"]);
$jidmachine = htmlspecialchars($_GET["jidmachine"]);

$files = xmlrpc_get_backup_files($client_id, $backup_id, $volume_name);
$path = $files['path'];

if ($path == "")
{
    $path = "/";
}

if ($volume_name == "")
{
    $volume_name = "/";
}
else
{
    $before_pathh = explode("/",$volume_name);
    array_pop($before_pathh);
    array_shift($before_pathh);
    foreach($before_pathh as $key)
    {
        $new_path .= "/".$key;
    }
}

$client_name = $files['clientname'];
$files = $files['files'];

$p = new PageGenerator(_T("Backups list for ".$client_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

function secs2date($secs,$date)
{
    if ($secs>2147472000)
        {
        $date->setTimestamp(2147472000);
        $s=$secs-2147472000;
        $date->add(new DateInterval('PT'.$s.'S'));
        }
    else
        $date->setTimestamp($secs);
}

function formatBytes($bytes, $precision = 2) { 
    $units = array('B', 'KB', 'MB', 'GB', 'TB'); 

    $bytes = max($bytes, 0); 
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024)); 
    $pow = min($pow, safeCount($units) - 1); 

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow]; 
}
?>

<br>
<label><?php echo _T(" Path: ", 'urbackup').$path; ?></label>
<br>
<?php 
if ($path != "/") { 
?>
    <a class='btn btn-small btn-primary' title=<?php echo _T("Back to previous path", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid=<?php echo $client_id ?>&amp;backupid=<?php echo $backup_id ?>&amp;volumename=<?php echo $new_path ?>"><?php echo _T("Back to previous path", 'urbackup'); ?></a>
<?php 
}
?>
<a class='btn btn-small btn-primary' title=<?php echo _T("Back to backup list", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $client_name ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidmachine ?>"><?php echo _T("Back to backup list", 'urbackup'); ?></a>
<form id="searchBest" method="post" style="width:285px; float:right;" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=result_search_file&amp;clientid=<?php echo $client_id ?>&amp;backupid=<?php echo $backup_id ?>">
    <input type="text" class="searchfieldreal" name="filenamesearch" id="filenamesearch">
    <img class="searchfield" src="graph/croix.gif" alt="suppression" style="position:relative;">
    <input type="submit" value="Search" style="margin-left: 15px;">
</form>

<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("File/Folder", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
          <th> <?php echo _T("Create date", 'urbackup'); ?> </th>
          <th> <?php echo _T("Last modification", 'urbackup'); ?> </th>
          <th> <?php echo _T("Last access", 'urbackup'); ?> </th>
          <th style='text-align: right;'> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php

if (empty($files))
{
    echo "<tr style='text-align: center;'>";
        echo '<td colspan="6">'._T("No file", 'urbackup').'</td>';
    echo '</tr>';
}

foreach ($files as $file)
{
    if (isset($file['shahash']))
        $shahash = $file['shahash'];
    else
        $shahash = "";

    if ($path != "/")
        $final_path = $path."/".$file['name'];
    else
        $final_path = $path.$file['name'];

    if ($file['dir'] == "false")
        $dir = "false";
    else
        $dir = "true";

    $date=new dateTime();

    $before_path = trim($path, $file['name']);

    $secs=$file['creat'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $create_date=$date->format('Y-m-d H:i:s');

    $secs=$file['access'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $access_date=$date->format('Y-m-d H:i:s');

    $secs=$file['mod'];  //2033-12-06 08:53:20
    secs2date($secs,$date);
    $mod_date=$date->format('Y-m-d H:i:s');

    $now = new DateTime;
    $secs=$now;
    secs2date($secs,$date);
    $nowtime=$date->format('Y-m-d H:i:s');

    if (isset($file['size']))
        $size = formatBytes($file['size']);
    else
        $size = "";
?>
        <tr>
            <td>
                <?php
                if ($dir == "false")
                {
                    echo '<a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid='.$client_id.'&amp;backupid='.$backup_id.'&amp;filename='.$file['name'].'&amp;beforepath='.$before_path.'&amp;volumename='.$final_path.'">'.$file['name'].'</a>';
                }
                ?>
            </td>
            <td> <?php echo $size; ?></td>
            <td> <?php echo $create_date; ?></td>
            <td> <?php echo $mod_date; ?></td>
            <td> <?php echo $access_date; ?></td>
            <td>
            <ul class="action">
                <?php
                if ($dir == "false")
                {
                    echo '<li class="display">';
                        echo '<a title='._T("Browse", 'urbackup').' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;clientid='.$client_id.'&amp;backupid='.$backup_id.'&amp;filename='.$file['name'].'&amp;beforepath='.$before_path.'&amp;volumename='.$final_path.'">&nbsp;</a>';
                    echo '</li>';
                }
                ?>
                <a class='btn btn-small btn-primary' title=<?php echo _T("DOWNLOAD", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=download_file&amp;timestamp=<?php echo $nowtime; ?>&amp;clientname=<?php echo $client_name; ?>&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;filename=<?php echo $file['name'] ?>&amp;path=<?php echo $path ?>">Download</a>
                <a class='btn btn-small btn-primary' title=<?php echo _T("RESTORE", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restore_file&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;shahash=<?php echo $shahash; ?>&amp;beforepath=<?php echo $path; ?>&amp;filename=<?php echo $file['name'] ?>">Restore</a>
            </ul>
            </td>
        </tr>
<?php
}
?>
    </tbody>
</table>
