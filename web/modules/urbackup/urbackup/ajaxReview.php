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

require_once("modules/urbackup/includes/xmlrpc.php");
require_once("modules/urbackup/includes/functions.inc.php");

global $conf;
global $maxperpage;

$array_progress = xmlrpc_get_progress();
$progress = $array_progress["progress"];
$array = (isset($array_progress["lastacts"])) ? $array_progress["lastacts"] : [];
$stats = xmlrpc_get_stats();

$entity = (isset($_GET['entity'])) ? $_GET['entity'] : '';
$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end = (isset($_GET['end'])) ? $_GET['end'] : 10;
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : '';

?>
<script>
    /*jQuery(document).ready(function($) {
        setInterval(function() {
            $("#progressBackups").load("modules/urbackup/urbackup/index.php");
        }, 10000);
    });*/

</script>
<br>
<br>
<h2><?php echo _T("Global statistics", 'urbackup'); ?></h2>
<?php
$all_size = 0;
$files_size = 0;
?>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
        <th> <?php echo _T("Space on disk used by all client", 'urbackup'); ?> </th>
        <th> <?php echo _T("Size", 'urbackup'); ?> </th>
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
            <td style='padding-left: 5px;'>All computers</td>
            <td><?php echo $files_size; ?></td>
        </tr>
    </tbody>
</table>
<?php

?>
<br>
<br>
<div id="progressBackups">
<?php

foreach($array_progress as $progress)
{

    if (!empty($progress))
    {
        echo '<h2>'._T("Progress", 'urackup').'</h2>';
        echo '<br>';
        if(empty($progress["eta_ms"])){
            continue;
            }
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
</div>



<h2><?php echo _T("Last activities", 'urbackup'); ?></h2>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
          <th> <?php echo _T("Id", 'urbackup'); ?> </th>
          <th> <?php echo _T("Name", 'urbackup'); ?> </th>
          <th> <?php echo _T("Date of backup", 'urbackup'); ?> </th>
          <th> <?php echo _T("Status", 'urbackup'); ?> </th>
          <th> <?php echo _T("Details", 'urbackup'); ?> </th>
          <th> <?php echo _T("Duration H:M:S", 'urbackup'); ?> </th>
          <th> <?php echo _T("Size", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php

foreach ($array as $review) {
    if ($review['del'] == "True")
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
    elseif ($review['del'] == "False")
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

    $seconds = round($duration);
 
    $output_duration = sprintf('%02d:%02d:%02d', ($seconds/ 3600),($seconds/ 60 % 60), $seconds% 60);
?>
        <tr>
            <td style='padding-left: 5px;'> <?php echo $review['id']; ?></td>
            <td> <?php echo $review['name']; ?></td>
            <td> <?php echo date('Y-m-d H:i:s', $review['backuptime']); ?></td>
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
