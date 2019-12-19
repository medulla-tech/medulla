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

$nbt  = count($listrelaytotal);
$nbns = count($listsearchnosynchro);
$nbs  = count($listsearchsynchro);
$nbsp = ($nbs/$nbt)*100;
$nbnsp = ($nbns/$nbt)*100;


echo "<table class='listinfos'>";
    echo "<thead>";
    echo "<tr>";
    echo '<th headers="resultsync" colspan="1" >'._T("Relay servers already synchronized : ", 'pkgs').$nbs.'/'.$nbt.' ('.$nbsp .'%)</th>';
    echo "</tr>";
    echo "</thead>";

    echo "<tbody>";
    foreach($listsearchsynchro as $key=>$val){
        echo "<tr>";
            echo "<td>";
            echo $val;
            echo "</td>";
        echo "</tr>";
    }
    echo "</tbody>";
echo "</table>";


echo "<table class='listinfos'>";
    echo "<thead>";
    echo "<tr>";
    echo '<th headers="resultnosync" colspan="1" >'._T("Relay servers not yet synchronized : ", 'pkgs').$nbns.'/'.$nbt.' ('.$nbnsp .'%)</th>';
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";

    foreach($listsearchnosynchro as $key=>$val){
        echo "<tr>";
            echo "<td>";
            echo $val;
            echo "</td>";
        echo "</tr>";
    }
    echo "</tbody>";
echo "</table>";

?>
