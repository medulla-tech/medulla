<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require("../includes/xmlrpc.inc.php");

$location = getCurrentLocation();
if (xmlrpc_doesLocationHasImagingServer($location)) {
    $global_status = xmlrpc_getGlobalStatus($location);
    $disk_info = format_disk_info($global_status['disk_info']);
    $health = format_health($global_status['uptime'], $global_status['mem_info']);
    $short_status = $global_status['stats'];
?>

<br/>
<h2><?=_T('Server status in entity', 'imaging')?></h2>

<div class="status">
    <div class="status_block">
        <h3><?=_T('Space available on server', 'imaging')?></h3>
        <?=$disk_info;?>
    </div>
    <div class="status_block">
        <h3><?=_T('Load on server', 'imaging')?></h3>
        <?=$health;?>
    </div>
</div>

<div class="status">
    <!--<div class="status_block">
        <h3 style="display: inline"><?=_T('Synchronization state', 'imaging')?> : </h3>
        <?
        $led = new LedElement('green');
        $led->display();
        echo "&nbsp;"._T("Up-to-date", "imaging");
        ?>
    </div>-->
    <div class="status_block">
        <h3><?=_T('Imaging stats', 'imaging')?></h3>
        <p class="stat"><img src="img/machines/icn_machinesList.gif" /> <strong><?=$short_status['rescue'];?></strong>/<?=$short_status['total'];?> clients have a rescue image</p>
        <p class="stat"><img src="img/common/cd.png" /> <strong><?=$short_status['master'];?></strong> masters are available</p>
    </div>
</div>

<div class="spacer"></div>

<h2 class="activity"><?=_T('Recent activity in entity', 'imaging')?></h2>

<?
    $ajax = new AjaxFilter("modules/imaging/manage/ajaxLogs.php", "container_logs", array(), "Logs");
    //$ajax->setRefresh(10000);
    $ajax->display();
    echo "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else {
    $ajax = new AjaxFilter(urlStrRedirect("imaging/manage/ajaxAvailableImagingServer"), "container", array('from'=>$_GET['from']));
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}
?>
