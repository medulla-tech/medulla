<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

function colorconf($conf){
    $colorDisplay=array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
    return $colorDisplay[intval(($conf-($conf%10))/10)];
}

//$updates = getUserLocations();
//$updatesCompliances = xmlrpc_get_conformity_update_by_entity();

$params = [];

$updateNames = [];
$complRates = [];
$machineWithoutUpd = [];
$machineWithUpd = [];


$count = count($updates);
foreach ($updates as $update) {
    $updateNames[] = $update["title"];

    //$color = colorconf(100);
    //$complRates[] ="<div class='progress' style='width: ".$conformite."%; background : ".$color."; font-weight: bold; color : white; text-align: right;'> ".$conformite."% </div>";
    
    //$machineWithoutUpd[] = $updatesCompliances;
    //$machineWithUpd[] = $updatesCompliances;
}

$n = new OptimizedListInfos($updateNames, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($machineWithUpd, _T("Machine with this updates", "updates"));
$n->addExtraInfo($machineWithoutUpd, _T("Machine without this updates", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->display();
?>
