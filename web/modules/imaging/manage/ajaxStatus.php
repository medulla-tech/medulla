<?php
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

$t = new TitleElement(_T("Status", "imaging"), 3);
$t->display();

$customMenu_count = xmlrpc_getCustomMenuCount($location);
$global_status = xmlrpc_getGlobalStatus($location);
if (!empty($global_status)) {
    $disk_info = format_disk_info($global_status['disk_info']);
    $health = format_health($global_status['uptime'], $global_status['mem_info']);
    $short_status = $global_status['short_status'];
    ?>

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
        <?php
        $led = new LedElement('green');
        $led->display();
        echo "&nbsp;" . _T("Up-to-date", "imaging");
        ?>
        </div>-->
        <div class="status_block">
            <?php //<a href=" echo urlStrRedirect("imaging/imaging/createCustomMenuStaticGroup"); &location=UUID1">ZZZ</a> ?>
            <h3><?php echo _T('Stats', 'imaging') ?></h3>
            <p class="stat"><img src="img/machines/icn_machinesList.gif" /> <strong><?php echo $short_status['total']; ?></strong> <?php echo _T("client(s) registered", "imaging") ?> (<?php echo $customMenu_count; ?> <?php echo _T("with custom menu", "imaging") ?>)</p>
            <p class="stat"><img src="img/machines/icn_machinesList.gif" /> <strong><?php echo $short_status['rescue']; ?></strong>/<?php echo $short_status['total']; ?> <?php echo _T("client(s) have rescue image(s)", "imaging") ?></p>
            <p class="stat"><img src="img/common/cd.png" />
                <strong><?php echo $short_status['master']; ?></strong>
                <?php echo _T("masters are available", "imaging") ?>
        </div>
    </div>
 <!-- //jfk -->
 <!--// regles de gestions affichage.
 
 // fichier /tmp/multicast.sh n'existe pas "ne pas afficher cadre Multicast Current Location"
 
 // fichier /tmp/multicast.sh existe
 // multicast lancer "affichage seulement bouton arrêt" voir aprés pour bar de progression
 // multicast non lancer "affichage seulement bouton stop"
 
 
 // cas extreme 
 // cas si  fichier /tmp/multicast.sh n'existe plus et /tmp/multicast.sh lancer normalement possible
 // stoper /tmp/multicast.sh
 
 // action bouton arret
 // 1)  stoper /tmp/multicast.sh
 // 2)  supprimer le fichier /tmp/multicast.sh
 // 3) regénéré les menus  unicast
 
 // action bouton marche
 // 1) start /tmp/multicast.sh
 -->
 <?php
 $scriptmulticast = 'multicast.sh';
 $path="/tmp/";
 $objprocess=array();
 $objprocess['location']=$_GET['location'];
 $objprocess['process'] = $path.$scriptmulticast;
// detection si multicast terminer 
echo '<script type="text/javascript">';
echo '
var locations = "'.$_GET['location'].'";';
echo 'var path = "'.$path.'";';
echo 'var scriptmulticast = "'.$scriptmulticast.'";';
echo'
var interval = setInterval(function() {
        var request = jQuery.ajax({
            url: "modules/imaging/manage/ajaxcheckstatusmulticast.php",
            type: "GET",
            data: {"location" :locations,"path": path,"scriptmulticast" : scriptmulticast}
    });
    request.done(function(msg) {
        if(msg==1){ jQuery("#checkprocess").hide(); }
    });
},1000);
 </script>';

    echo '
        <div class="status" id="checkprocess">
        <div class="status_block">  ';
    // fichier /tmp/multicast.sh n'existe pas "ne pas afficher cadre Multicast Current Location"
    $objprocess['process'] = $scriptmulticast;
    if (xmlrpc_check_process_multicast($objprocess)){
        // script /tmp/multicast.sh run
        // "affichage bouton arrêt"
        // voir apres pour bar de progression
        echo'<h3>';
        echo _T('STOP Multicast Current Location', 'imaging');
        echo'</h3>';
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/");
        echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="stop" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Stop multicast deploy", "imaging");
        echo '" />    
        </form>';
    }
    else{
        // script arreter afficher bouton start
        echo'<h3>';
        echo _T('START Multicast Current Location', 'imaging');
        echo'</h3>';
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/"); echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="start" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Start multicast deploy", "imaging");
        echo '" />    
        </form>';
        echo "<br>";
        echo '<form action="'; 
        echo urlStr("imaging/manage/multicastaction/"); echo '" method="POST">';
        echo '<input name="multicast"  type="hidden" value="clear" />';
        echo '<input name="location"  type="hidden" value="'.$objprocess['location'].'" />';
        echo '<input name="process"  type="hidden" value="'.$scriptmulticast.'" />';
        echo '<input name="path" type="hidden" value="'.$path.'" />
        <input name="bgo" type="submit" class="btnPrimary"
        value="';
        echo _T("Clear multicast deploy", "imaging");
        echo '" />    
        </form>';
    }
    echo'
            </div>
        </div>';
}else{
    $objprocess['process'] = $scriptmulticast;
    if (xmlrpc_check_process_multicast($objprocess)){
        // if /tmp/multicast.sh is running then stoping
        $objprocess['process'] = $scriptmulticast;
        xmlrpc_stop_process_multicast ($objprocess);
        $objprocess['process'] = $path.$scriptmulticast;
        xmlrpc_clear_script_multicast($objprocess);
    }
}
?>
    
    <div class="spacer"></div>

    <h3 class="activity"><?php echo _T('Recent activity', 'imaging') ?></h3>

    <?php
    $ajax = new AjaxFilter("modules/imaging/manage/ajaxLogs.php", "container_logs", array(), "Logs");
    //$ajax->setRefresh(10000);
    $ajax->display();
    echo "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else {
    $e = new ErrorMessage(_T("Can't connect to the imaging server linked to the selected entity.", "imaging"));
    print $e->display();
}

require("../includes/ajaxcommon_bottom.inc.php");
?>
