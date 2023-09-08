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

$clientname = htmlspecialchars($_GET["clientname"]);
$groupname = htmlspecialchars($_GET["groupname"]);
$groupid = htmlspecialchars($_GET["groupid"]);

$p = new PageGenerator(_T("Backups List ".$clientname, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];
$url_urbackup = $ini_array['url'];

$client_id = htmlspecialchars($_GET["clientid"]);
$backupstate = htmlspecialchars($_GET["backupstate"]);
$backuptype = htmlspecialchars($_GET["backuptype"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);
$disableClient = htmlspecialchars($_GET["disableclient"]);

//-----------------------------------START LOGIN FUNCTION
$url = $url_urbackup."?a=login";

$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);
$datas = [
'username'=>$username_urbackup,
'password'=>$password_urbackup,
'plainpw'=>1
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid)) 
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
{
$result = (array)json_decode($response);
}

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1){
    $session = $result['session'];
}
//-----------------------------------END LOGIN

//-----------------------------------START GET_BACKUPS FUNCTION
$url = $url_urbackup."?a=backups";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'backups',
    'clientid'=>$client_id,
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid))
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
{
    $result = (array)json_decode($response);
}
curl_close($curlid);

$reviews = $result;
$array = json_decode(json_encode($reviews), true);

$can_delete = $array['can_delete'];

if ($can_delete == "true")
    $delete = "true";
else
    $delete = "false";

$backups = $array['backups'];

//Formatage de date
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

function formatBytes($bytes, $precision = 2) 
{ 
    $units = array('B', 'KB', 'MB', 'GB', 'TB'); 

    $bytes = max($bytes, 0); 
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024)); 
    $pow = min($pow, count($units) - 1); 

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow]; 
}

$stats = xmlrpc_get_stats();

?>
<h2><?php echo _T("Statistics by client", 'urbackup'); ?></h2>
<?php

?>
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

<a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Start incremental backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=incremental&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupename=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Start incremental backup</a>
<a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Start full backup", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=full&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupename=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Start full backup</a>
<a onclick="confirmAction()" class='btn btn-small btn-primary' title=<?php echo _T("Disable backup for this client", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_client&amp;clientid=<?php echo $client_id ?>&amp;clientname=<?php echo $clientname ?>&amp;groupename=<?php echo $groupname ?>&amp;jidmachine=<?php echo $jidMachine ?>">Disable backup for this client</a>
<br>
<br>
<?php echo _T("Profile name: ", 'urbackup'); ?><a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_computers_ongroup&amp;groupid=<?php echo $groupid ?>&groupname=<?php echo $groupname ?>"><?php echo $groupname; ?></a>
<br>
<br>
<?php
if ($backupstate == "false")
{
    if ($backuptype == "incremental") 
    {
        ?>
        <script>
            alert("Incremental backup failed, be sure client urbackup is installed on computer or is online.");
        </script>
        <?php
    }
    
    if ($backuptype == "full")
    {
        ?>
        <script>
            alert("Full backup failed, be sure client urbackup is installed on computer or is online.");
        </script>
        <?php
    }
}

if ($disableClient == "true")
{
    ?>
    <script>
        alert("The backups for this client has been disabled successfully.");
    </script>
    <?php
}
?>
<h2> <?php echo _T("File save", 'urbackup'); ?> </h2>

<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Type", 'urbackup'); ?> </th>
          <th> <?php echo _T("Archived ?", 'urbackup'); ?> </th>
          <th> <?php echo _T("Time", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
          <th style='text-align: right;'> <?php echo _T("Action", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php

if (empty($backups))
{
    echo "<tr style='text-align: center;'>";
        echo '<td colspan="6">'._T("No backup", 'urbackup').'</td>';
    echo '</tr>';
}

foreach ($backups as $backup) {
    $id_backup = $backup['id'];
    $date=new dateTime();

    if (isset($file['dir']))
        $dir = "false";
    else
        $dir = "true";

    $secs=$backup['backuptime'];
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');

    $size = formatBytes($backup['size_bytes']);

    if ($backup['incremental'] == "0")
        $incremental = _T("Full backup", 'urbackup');
    else
        $incremental = _T("Incremental backup", 'urbackup');

    if ($backup['archived'] == "0")
        $archive = _T("No", 'urbackup');
    else
        $archive = _T("Yes", 'urbackup');
?>
        <tr >
            <td>
                <a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;groupname=<?php echo $groupname; ?>&amp;clientid=<?php echo $client_id; ?>&amp;jidmachine=<?php echo $jidMachine; ?>&amp;backupid=<?php echo $id_backup; ?>&amp;volumename=<?php echo "/" ?>"><?php echo $backup['id']; ?></a>
            </td>
            <td> <?php echo $incremental; ?></td>
            <td> <?php echo $archive; ?></td>
            <td> <?php echo $dt; ?></td>
            <td> <?php echo $size; ?></td>
            <td>
            <ul class="action">
                <li class="display">
                    <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=all_files_backup&amp;groupname=<?php echo $groupname; ?>&amp;clientid=<?php echo $client_id; ?>&amp;jidmachine=<?php echo $jidMachine; ?>&amp;backupid=<?php echo $id_backup; ?>&amp;volumename=<?php echo "/" ?>">&nbsp;</a>
                </li>
                <?php
                if ($delete == "true")
                {
                    if (isset($backup['disable_delete']))
                    {
                        if ($backup['disable_delete'] == "false")
                        {
                            echo '<li class="delete">';
                            echo '<a title='._T("Delete", 'urbackup').' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_backup&amp;clientid='.$client_id.'&amp;backupid='.$id_backup.'">&nbsp;</a>';
                            echo '</li>';
                        }
                    }
                    else
                    {
                        echo '<li class="delete">';
                            echo '<a title='._T("Delete", 'urbackup').' href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_backup&amp;clientid='.$client_id.'&amp;backupid='.$id_backup.'">&nbsp;</a>';
                        echo '</li>';
                    }
                }
                ?>
            </ul>
            </td>
        </tr>
<?php
}
?>
    </tbody>
</table>
