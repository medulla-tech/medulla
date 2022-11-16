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

$p = new PageGenerator(_T("Logs", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$logs_global = xmlrpc_get_logs();
$logs = $logs_global['logdata'];

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
foreach ($logs as $log)
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
?>
    </tbody>
</table>
