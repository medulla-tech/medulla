<?php
/*
 * (c) 2024 Siveo, http://www.siveo.net/
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

require_once("modules/urbackup/includes/xmlrpc.php");
require_once("modules/urbackup/includes/functions.inc.php");
global $maxperpage;

$clientname = htmlspecialchars($_GET["clientname"]);
$groupname = htmlspecialchars($_GET["groupname"]);
$groupid = htmlspecialchars($_GET["groupid"]);

$start = (!empty($_GET["start"])) ? htmlentities($_GET["start"]) : 0;
$end = (!empty($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : '';

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$ini_array_local = parse_ini_file("/etc/mmc/plugins/urbackup.ini.local");
$username_urbackup = isset($ini_array_local["usernameapi"]) ? $ini_array_local["usernameapi"] : $ini_array["usernameapi"];
$password_urbackup = isset($ini_array_local["passwordapi"]) ? $ini_array_local["passwordapi"] : $ini_array["passwordapi"];
$url_urbackup = isset($ini_array_local["url"]) ? $ini_array_local["url"] : $ini_array["url"];

$client_id = htmlspecialchars($_GET["clientid"]);
$backupstate = (!empty($_GET["backupstate"])) ? htmlspecialchars($_GET["backupstate"]) : "";
$backuptype = (!empty($_GET['backuptype'])) ? htmlspecialchars($_GET["backuptype"]) : "";
$jidmachine = htmlspecialchars($_GET["jidmachine"]);
$editStateClient = htmlspecialchars($_GET["editStateClient"]);
$errorEditStateClient = htmlspecialchars($_GET["error"]);
$newClient = htmlspecialchars($_GET["newClient"]);
$restart_service = htmlspecialchars($_GET["restart_service"]);

$backups = xmlrpc_get_backups($client_id, $start, $maxperpage, $filter);
$count = $backups["total"];
$backups = $backups["datas"];

$can_delete = $array['can_delete'];

if ($can_delete == "true")
    $delete = "true";
else
    $delete = "false";

// $_backups = $array['backups'];

//-----------------------------------END GET_BACKUPS


$stats = xmlrpc_get_stats();

$client_enable = xmlrpc_get_client_status($client_id);
?>
<h2><?php echo _T("Statistics by client", 'urbackup'); ?></h2>
<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
        <th> <?php echo _T("Computer name", 'urbackup'); ?> </th>
        <th> <?php echo _T("File size", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
    <?php
    foreach ($stats["usage"] as $stat)
    {
        if ($stat['name'] == $clientname)
        {
            $files_size = formatBytes($stat['files']);
            ?>
            <tr>
                <td style='padding-left: 5px;'> <?php echo $stat['name']; ?></td>
                <td> <?php echo $files_size; ?></td>
            </tr>
            <?php
        }
    }
    ?>
    </tbody>
</table>

<br>
<br>
<?php
if ($client_enable == 1)
{
?>
<a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Start incremental backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=incremental&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Start incremental backup</a>
<a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Start full backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=full&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Start full backup</a>
<?php
}
if ($client_enable == 0)
{
?>
    <a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Enable backup for this client", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_client&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>&amp;editclient=enable">Enable backup for this client</a>
<?php
}

if ($client_enable == 1)
{
?>
    <a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Disable backup for this client", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_client&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>&amp;editclient=disable">Disable backup for this client</a>
<?php
}
?>
<a class='btn btn-small btn-primary' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restart_service&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupname=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Restart Urbackup Service on client</a>
<br>
<br>
<?php echo _T("Profile name: ", 'urbackup'); ?><a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_computers_ongroup&amp;groupid=<?php echo $groupid ?>&groupname=<?php echo $groupname ?>"><?php echo $groupname; ?></a>
<br>
<br>
<?php

// Differents alert for users informations
if ($backupstate == "false")
{
    if ($backuptype == "incremental")
    {
        $str = _T("Incremental backup failed, be sure client urbackup is installed on computer or is online.", "urbackup");
        new NotifyWidgetFailure($str);
    }

    if ($backuptype == "full")
    {
        $str = _T("Full backup failed, be sure client urbackup is installed on computer or is online.", "urbackup");
        new NotifyWidgetFailure($str);
    }
}
if ($newClient == "true")
{
    $str = _T("The installation and configuration of the urbackup client on computers can take up to 10 minutes. This is required to have a fully operational client and enable the backups. After that, fully backup will be automatically created.", "urbackup");
    new NotifyWidgetSuccess($str);
    $newClient = "false";
}
if ($editStateClient == "disable")
{
    $str = _T("This client has been successfully disabled.", "urbackup");
    new NotifyWidgetSuccess($str);
}
if ($editStateClient == "enable")
{
    $str= _T("This client has been successfully enabled.", "urbackup");
    new NotifyWidgetSuccess($str);
}

if ($errorEditStateClient == "true")
{
    $str= _T("This client was offline, please wait until it is online and try again.", "urbackup");
    new NotifyWidgetFailure($str);
}

if ($restart_service == "true")
{
    $str= _T("Restart can take up to 5 seconds, please wait before taking any action.", "urbackup");
    new NotifyWidgetSuccess($str);
}

echo '<h2>'. _T("File save", 'urbackup').'</h2>';

if (!empty($backups) && $client_enable == 1)
{
    $detailAction = new ActionItem(_T("Backup files", "urbackup"), "all_files_backup", "display", "urbackup", "urbackup");
    $ids = [];
    $dts = [];
    $sizes = [];
    $incrementals = [];
    $archives = [];
    $detailActions = [];
    $params = [];
    foreach ($backups as $backup) {

        $id_backup = $backup['id'];
        $ids[] = $backup['id'];
        $dt = $backup['backuptime'];
        $dts[] = $backup['backuptime'];
        $size = formatBytes($backup['size_bytes']);
        $sizes[] = formatBytes($backup['size_bytes']);
        $detailActions[] = $detailAction;

        if ($backup['full'] == true){
            $incremental = _T("Full backup", 'urbackup');
            $incrementals[] = _T("Full backup", 'urbackup');
        }
        else{
            $incremental = _T("Incremental backup", 'urbackup');
            $incrementals[] = _T("Incremental backup", 'urbackup');
        }


        if ($backup['archived'] == false){
            $archive = _T("No", 'urbackup');
            $archives[] = _T("No", 'urbackup');
        }
        else{
            $archive = _T("Yes", 'urbackup');
            $archives[] = _T("Yes", 'urbackup');

        }
        $base_path = $backup["path"];

        $params[] = [
            "groupname"=>$groupname,
            "clientid"=>$client_id,
            "jidmachine"=>$jidmachine,
            "backupid"=>$backup["id"],
            "volumename"=>"/",
            "path"=>$base_path
        ];
    }

    $n = new OptimizedListInfos($incrementals, _T("Type", "urbackup"));
    $n->setcssIds($ids);
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($archives, _T("Archived ?", "urbackup"));
    $n->addExtraInfo($dts, _T("Time", "urbackup"));
    $n->addExtraInfo($sizes, _T("Size", "urbackup"));
    $n->setParamInfo($params);
    $n->addActionItemArray($detailActions);
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar((int)$count, $filter));
    $n->start = 0;
    $n->end = $count;
    $n->display();

}
else if (empty($backups) && $client_enable == 1)
{
    // echo '<table>'
    // echo "<tr style='text-align: center;'>";
        // echo '<td colspan="6">'._T("No backup", 'urbackup').'</td>';
    // echo '</tr>';
        echo _T("No backup", 'urbackup');

}
else if ($client_enable == 0)
{
    // echo "<tr style='text-align: center;'>";
    // echo '<td colspan="6">'._T("Client disabled", 'urbackup').'</td>';
    // echo '</tr>';
    echo _T("Client disabled", 'urbackup');
}
?>

    </tbody>
</table>
