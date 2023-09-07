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

$p = new PageGenerator(_T("Reviews", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];
$url_urbackup = $ini_array['url'];

function formatBytes($bytes, $precision = 2)
{ 
    $units = array('B', 'KB', 'MB', 'GB', 'TB'); 

    $bytes = max($bytes, 0); 
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024)); 
    $pow = min($pow, safeCount($units) - 1); 

    $bytes /= pow(1024, $pow);

    return round($bytes, $precision) . ' ' . $units[$pow]; 
}

//Formatage de date
function secs2date($secs,$date)
{
    if ($secs>2147472000)    //2038-01-19 expire dt
    {
        $date->setTimestamp(2147472000);
        $s=$secs-2147472000;
        $date->add(new DateInterval('PT'.$s.'S'));
    }
    else
        $date->setTimestamp($secs);
}

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
foreach($datas as $key=>$val)
{
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
    $result = (array)json_decode($response);

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1)
    $session = $result['session'];
//-----------------------------------END LOGIN

//-----------------------------------START GET_PROGRESS FUNCTION
$url = $url_urbackup."?a=progress";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val)
{
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
    $result = (array)json_decode($response);

curl_close($curlid);

$reviews = $result["lastacts"];
$array = json_decode(json_encode($reviews), true);

$progress = $result['progress'];
$array_progress = json_decode(json_encode($progress), true);
//-----------------------------------END GET_PROGRESS

$stats = xmlrpc_get_stats();

?>
<script>
    setTimeout(function(){
        window.location.reload(1);
    }, 5000);
</script>
<br>
<br>
<h2><?php echo _T("Global statistics", 'urbackup'); ?></h2>
<?php
$all_size = 0;
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
        $all_size = $all_size + $stat['files'];
        $files_size = formatBytes($all_size);
    }
    ?>
        <tr>
            <td style='padding-left: 5px;'> Space on disk used by all client</td>
            <td> <?php echo $files_size; ?></td>
        </tr>
    </tbody>
</table>
<?php

?>
<br>
<br>
<?php


foreach($array_progress as $progress)
{
    if (!empty($progress))
    {
        echo '<h2>'._T("Progress", 'urackup').'</h2>';
        echo '<br>';
        $eta = $progress['eta_ms'];
        $eta = $eta/1000;

        if ($eta < "0")
        {
            $eta = "0";
        }

        $progresss = $progress['pcdone'];

        if ($progresss == "100")
        {
            $eta = "0";
            $progresss = "Ending of backup, available soon... ".$progresss;
        }

        if ($progress['action'] == "1")
        {
            $action = "Incremental Backup";
        }

        if ($progress['action'] == "2")
        {
            $action = "Full Backup";
        }

        if ($progresss == "-1")
        {
            $progresss = "0";
        }

        switch(intval($progresss)){
            case $progresss <= 10:
                $color = "#ff0000";
                break;
            case $progresss <= 20:
                $color = "#ff3535";
                break;
            case $progresss <= 30:
                $color = "#ff5050";
                break;
            case $progresss <= 40:
                $color = "#ff8080";
                break;
            case $progresss <  50:
                $color = "#ffA0A0";
                break;
            case $progresss <=  60:
                $color = "#c8ffc8";
                break;
            case $progresss <= 70:
                $color = "#97ff97";
                break;
            case $progresss <= 80:
                $color = "#64ff64";
                break;
            case $progresss <=  90:
                $color = "#2eff2e";
                break;
            case $progresss >90:
                $color = "#00ff00";
                break;
        }

        $seconds = $eta;

        $secs = $seconds % 60;
        $hrs = $seconds / 60;
        $mins = $hrs % 60;

        $hrs = $hrs / 60;

        ?>
        <table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
            <thead>
                <tr style='text-align: left;'>
                <th> <?php echo _T("Computer name", 'urbackup'); ?> </th>
                <th> <?php echo _T("Action", 'urbackup'); ?> </th>
                <th> <?php echo _T("Details", 'urbackup'); ?> </th>
                <th> <?php echo _T("Progress", 'urbackup'); ?> </th>
                <th> <?php echo _T("ETA (approximation)", 'urbackup'); ?> </th>
                <th> <?php echo _T("Speed (bpms)", 'urbackup'); ?> </th>
                <th> <?php echo _T("File in queue", 'urbackup'); ?> </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style='padding-left: 5px;'> <?php echo $progress['name']; ?></td>
                    <td> <?php echo $action; ?></td>
                    <td> <?php echo $progress['details']; ?></td>
                    <td> <span style='background-color:<?php echo $color; ?>;'><?php echo $progresss."%"; ?></span> </td>
                    <td> <?php echo (int)$hrs." heures " .(int)$mins." minutes ".(int)$secs." secondes"; ?></td>
                    <td> <?php echo $progress['speed_bpms']; ?></td>
                    <td> <?php echo $progress['queue']; ?></td>
                </tr>
            </tbody>
        </table>
        <?php
        echo '<br>';
        echo '<br>';
    }
}
?>

<h2><?php echo _T("Last activities", 'urbackup'); ?></h2>



<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Name", 'urbackup'); ?> </th>
          <th> <?php echo _T("Backuptime", 'urbackup'); ?> </th>
          <th> <?php echo _T("Status", 'urbackup'); ?> </th>
          <th> <?php echo _T("Details", 'urbackup'); ?> </th>
          <th> <?php echo _T("Duration H:M:S", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php
foreach ($array as $review) {
    if ($review['del'] == true)
    {
        if ($review['incremental'] > 0)
        {
            if ($review['image'] == 0)
                $status = _T("Delete of incremental backup", "urbackup");
        }

        if ($review['incremental'] == 0)
        {
            if ($review['image'] == 0)
                $status = _T("Delete of full backup", "urbackup");
        }
    }
    elseif ($review['del'] == false)
    {
        if ($review['restore'] == 1)
        {
            if ($review['incremental'] > 0)
            {
                if ($review['image'] == 0)
                {
                    if ($review['details'] != "")
                        $status = _T("Restoration of file", "urbackup");
                }
            }
            else
            {
                if ($review['image'] == 0)
                {
                    if ($review['details'] != "")
                        $status = _T("Restoration of file", "urbackup");
                }
            }
        }
        else
        {
            if ($review['incremental'] > 0)
            {
                if ($review['image'] == 0)
                    $status = _T("Incremental backup", "urbackup");
                else
                    $status = _T("Incremental image", "urbackup");
            }

            if ($review['incremental'] == 0)
            {
                if ($review['image'] == 0)
                    $status = _T("Full files backup", "urbackup");
                else
                    $status = _T("Full files image", "urbackup");
            }
        }
    }
    else
    {

    }

    if ($review['details'] == "")
        $details = "-";
    else
        $details = $review['details'];

    $size = formatBytes($review['size_bytes']);
    $duration = $review['duration'];
    $duration = $duration*10;
    $duration = $duration." seconds";

    $seconds = round($duration);
 
    $output_duration = sprintf('%02d:%02d:%02d', ($seconds/ 3600),($seconds/ 60 % 60), $seconds% 60);

    $date=new dateTime();

    $secs=$review['backuptime'];
    secs2date($secs,$date);
    $dt=$date->format('Y-m-d H:i:s');
?>
        <tr>
            <td style='padding-left: 5px;'> <?php echo $review['id']; ?></td>
            <td> <?php echo $review['name']; ?></td>
            <td> <?php echo $dt; ?></td>       
            <td> <?php echo $status; ?></td>
            <td> <?php echo $details; ?></td>
            <td> <?php echo $output_duration; ?></td>
            <td> <?php echo $size; ?></td>
        </tr>
<?php
}
?>
    </tbody>
</table>

<br>
<h2>Logs</h2>

<?php
$logs_global = xmlrpc_get_logs();
$logs = $logs_global['logdata'];

?>

<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Message", 'urbackup'); ?> </th>
          <th> <?php echo _T("Time", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php 

array_multisort(array_column($logs, 'id'), SORT_DESC, $logs);

foreach ($logs as $log)
{
    if (strpos($log['msg'], "Looking") === 0 or strpos($log['msg'], "Session") === 0)
    {

    }
    else
    {
        $date=new dateTime();

        $secs=$log['time'];  //2033-12-06 08:53:20
        secs2date($secs,$date);
        $dt=$date->format('Y-m-d H:i:s');
    
        $msg = "<td>".$log['msg']."</td>";
    
        $need_show_msg = "True";
    
        if (strpos($log['msg'], 'FATAL:') !== false) {
            $msg = $log['msg'];
            $msg = "<td class='log_error'>".$msg."</td>";
        }
    
        if (strpos($log['msg'], 'Backup failed') !== false) {
            $msg = $log['msg'];
            $msg = "<td class='log_error'>".$msg."</td>";
        }
    
        if (strpos($log['msg'], 'Backup failed because of disk problems') !== false) {
            $msg = $log['msg'];
            $msg = "<td class='log_error'>"._T("Backup failed because of disk problems, no space left on disk (see previous messages)")."</td>";
        }
    
        if (strpos($log['msg'], 'Loading files') !== false) {
            $need_show_msg = "False";
        }
    
        if ($need_show_msg == "True")
        {
    ?>
            <tr >
                <td> <?php echo $log['id']; ?></td>
                <?php echo $msg; ?>
                <td> <?php echo $dt; ?></td>
            </tr>
    <?php
        }
    }
}
?>
    </tbody>
</table>
