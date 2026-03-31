<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");

$uuidpackage =  base64_decode ( $_GET['pid']);
//interoge la table syncthingsync
$infopackage = xmlrpc_pkgs_get_info_synchro_packageid($uuidpackage);


$nosynchrolist = $infopackage[0];
$relayserverlist =  $infopackage[1];

$listnosync = array();
$listrelaytotal  = array();

$listsearchsynchro=array();
$listsearchnosynchro = array();

foreach ($nosynchrolist as $rel){
        $pos = strpos($rel['relayserver_jid'], "rspulse@pulse");
        if ($pos === false){
            $listnosync[] =  $rel['relayserver_jid'];
        }
}


foreach ($relayserverlist as $rel){

        $listrelaytotal[$rel['jid'] ] = $rel['nameserver'];
}


foreach ($listrelaytotal as $key => $val){
    if(in_array($key, $listnosync)){
        $listsearchnosynchro[$key] = $val;
    }else{
        $listsearchsynchro[$key] = $val;
    }
}

$nbt  = safeCount($listrelaytotal);
$nbns = safeCount($listsearchnosynchro);
$nbs  = safeCount($listsearchsynchro);
$nbsp = ($nbs/$nbt)*100;
$nbnsp = ($nbns/$nbt)*100;


echo '<div class="quick-actions-popup">';
echo '<h1>'._T("Synchronization status", 'pkgs').'</h1>';

// Progress bar
$pct = ($nbt > 0) ? round(($nbs / $nbt) * 100) : 0;
$barColor = ($pct == 100) ? '#8CB63C' : (($pct >= 50) ? '#f48f42' : '#e03c3c');
echo '<div style="background:#edf2f7;border-radius:8px;height:8px;margin-bottom:20px;overflow:hidden;">';
echo '<div style="width:'.$pct.'%;height:100%;background:'.$barColor.';border-radius:8px;transition:width 0.3s;"></div>';
echo '</div>';

// Not yet synchronized
echo '<div class="actions-section" style="margin-bottom:12px;">';
echo '<h3 style="margin:0 0 8px 0;font-size:13px;font-weight:600;color:'.($nbns > 0 ? '#e03c3c' : '#999').';text-transform:uppercase;letter-spacing:0.5px;">'._T("Not yet synchronized", 'pkgs').' — '.$nbns.'/'.$nbt.'</h3>';
if ($nbns > 0) {
    foreach($listsearchnosynchro as $key=>$val){
        echo '<div style="padding:4px 0;color:#333;font-size:13px;">'.htmlspecialchars($val).'</div>';
    }
} else {
    echo '<div style="color:#999;font-size:13px;font-style:italic;">'._T("All servers are synchronized", 'pkgs').'</div>';
}
echo '</div>';

// Already synchronized
echo '<div class="actions-section" style="margin-bottom:0;">';
echo '<h3 style="margin:0 0 8px 0;font-size:13px;font-weight:600;color:#8CB63C;text-transform:uppercase;letter-spacing:0.5px;">'._T("Already synchronized", 'pkgs').' — '.$nbs.'/'.$nbt.'</h3>';
if ($nbs > 0) {
    foreach($listsearchsynchro as $key=>$val){
        echo '<div style="padding:4px 0;color:#333;font-size:13px;">'.htmlspecialchars($val).'</div>';
    }
}
echo '</div>';

echo '</div>';

?>
