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

$p = new PageGenerator(_T("File research by name", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_id = htmlspecialchars($_GET["clientid"]);
$backup_id = htmlspecialchars($_GET["backupid"]);
$filename = $_POST["filenamesearch"];

$result_array = array();

?>
<br>
<?php

?>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
            <th> <?php echo _T("File", 'urbackup'); ?> </th>
            <th> <?php echo _T("Path", 'urbackup'); ?> </th>
            <th> <?php echo _T("Creation date", 'urbackup'); ?> </th>
            <th> <?php echo _T("Size", 'urbackup'); ?> </th>
            <th style='text-align: right;'> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php

$spath = "/";

#$files = xmlrpc_get_backup_files($client_id, $backup_id, $spath);
#print_r($files);

get_backup_with_filename($client_id, $backup_id, "/", $filename, $spath, $result_array);

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
    $pow = min($pow, count($units) - 1);

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow];
}


function get_backup_with_filename($client_id, $backup_id, $path, $filename, $new_path, $result_array)
{
    $files = xmlrpc_get_backup_files($client_id, $backup_id, $path);
    $files = $files['files'];

    foreach ($files as $file)
    {
        if ($file["dir"] == "1")
        {
            $new_path = $path."/".$file["name"];

            if ($file["name"] != "Documents and Settings")
            {
                if ($file["name"] != "Application Data")
                {
                    get_backup_with_filename($client_id, $backup_id, $new_path, $filename, $new_path, $result_array);
                }
            }

            $date=new dateTime();

            $secs=$file['creat'];  //2033-12-06 08:53:20
            secs2date($secs,$date);
            $create_date=$date->format('Y-m-d H:i:s');

            $size = formatBytes($file['size']);

            if ($file['name'] == $filename)
            {
                ?>
                <tr>
                    <td> <?php echo $file['name']; ?> </td>
                    <td> <?php echo $path; ?></td>
                    <td> <?php echo $create_date; ?></td>
                    <td> <?php echo $size; ?></td>
                    <td>
                    <ul class="action">
                        <a class='btn btn-small btn-primary' title=<?php echo _T("DOWNLOAD", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=download_file&amp;timestamp=<?php echo $nowtime; ?>&amp;clientname=<?php echo $client_name; ?>&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;filename=<?php echo $file['name'] ?>&amp;path=<?php echo $path ?>">Download</a>
                        <a class='btn btn-small btn-primary' title=<?php echo _T("RESTORE", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restore_file&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $path; ?>&amp;shahash=<?php echo $file["shahash"]; ?>&amp;filename=<?php echo $file['name'] ?>">Restore</a>
                    </ul>
                    </td>
                </tr>
                <?php
            }
        }
        else
        {
            $date=new dateTime();

            $secs=$file['creat'];  //2033-12-06 08:53:20
            secs2date($secs,$date);
            $create_date=$date->format('Y-m-d H:i:s');

            $size = formatBytes($file['size']);

            if ($file['name'] == $filename)
            {
                ?>
                <tr>
                    <td> <?php echo $file['name']; ?> </td>
                    <td> <?php echo $path; ?></td>
                    <td> <?php echo $create_date; ?></td>
                    <td> <?php echo $size; ?></td>
                    <td>
                    <ul class="action">
                        <a class='btn btn-small btn-primary' title=<?php echo _T("DOWNLOAD", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=download_file&amp;timestamp=<?php echo $nowtime; ?>&amp;clientname=<?php echo $client_name; ?>&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $final_path; ?>&amp;filename=<?php echo $file['name'] ?>&amp;path=<?php echo $path ?>">Download</a>
                        <a class='btn btn-small btn-primary' title=<?php echo _T("RESTORE", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restore_file&amp;clientid=<?php echo $client_id; ?>&amp;backupid=<?php echo $backup_id; ?>&amp;volumename=<?php echo $path; ?>&amp;shahash=<?php echo $file["shahash"]; ?>&amp;filename=<?php echo $file['name'] ?>">Restore</a>
                    </ul>
                    </td>
                </tr>
                <?php
            }
        }
    }
}
?>
    </tbody>
</table>
<?php
