<?
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* common ajax includes */
require("../includes/ajaxcommon.inc.php");

    $global_status = xmlrpc_getGlobalStatus($location);
    if (!empty($global_status)) {
        $disk_info = format_disk_info($global_status['disk_info']);
        $health = format_health($global_status['uptime'], $global_status['mem_info']);
        $short_status = $global_status['short_status'];
?>

<br/>
<h2><?php echo _T('Server status for this entity', 'imaging') ?></h2>

<div class="status">
<div class="status_block">
    <h3><?php echo _T('Space available on server', 'imaging') ?></h3>
    <?php echo $disk_info; ?>
</div>
<div class="status_block">
    <h3><?php echo _T('Load on server', 'imaging') ?></h3>
    <?php echo $health; ?>
</div>
</div>

<div class="status">
<!--<div class="status_block">
    <h3 style="display: inline"><?php echo _T('Synchronization state', 'imaging') ?> : </h3>
    <?
    $led = new LedElement('green');
    $led->display();
    echo "&nbsp;"._T("Up-to-date", "imaging");
    ?>
</div>-->
<div class="status_block">
    <h3><?php echo _T('Stats', 'imaging') ?></h3>
      <p class="stat"><img src="img/machines/icn_machinesList.gif" /> <strong><?php echo $short_status['rescue']; ?></strong>/<?php echo $short_status['total']; ?> <?php echo _T("client(s) have rescue image(s)", "imaging") ?></p>                                                       <p class="stat"><img src="img/common/cd.png" />
      <strong><?php echo $short_status['master']; ?></strong>
      <?php echo _T("masters are available", "imaging") ?>
</div>
</div>

<div class="spacer"></div>

<h2 class="activity"><?php echo _T('Recent activity in entity', 'imaging') ?></h2>

<?
        $ajax = new AjaxFilter("modules/imaging/manage/ajaxLogs.php", "container_logs", array(), "Logs");
        //$ajax->setRefresh(10000);
        $ajax->display();
        echo "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    } else {
        $e = new ErrorMessage(_T("Can't connect to the imaging server linked to the selected entity.", "imaging"));
        print $e->display();
    }
?>
