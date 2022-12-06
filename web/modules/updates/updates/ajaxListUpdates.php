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

$grey_list = xmlrpc_get_grey_list($start, $maxperpage, $filter);
$white_list = xmlrpc_get_white_list($start, $maxperpage, $filter);

$count_grey = $grey_list['nb_element_total'];
$count_partial_grey = count($grey_list['title']);

$count_white = $white_list['nb_element_total'];
$count_partial_white = count($white_list['title']);

$final_partial_count = $count_partial_grey + $count_partial_white;

function colorconf($conf){
    $colorDisplay=array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
    return $colorDisplay[intval(($conf-($conf%10))/10)];
}

$all_update = [];
array_push($all_update, $grey_list);
array_push($all_update, $white_list);

$any_n = "/\d+? \d+? .*$/";

$detailsUpd = new ActionItem(_T("Details", "updates"),"test","auditbymachine","", "updates", "updates");

$kbs_gray = [];
$updateids_gray = [];
$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$actionDetails = [];

// ########## Boucle greyList ########## //
for($i=0; $i < $count_partial_grey; $i++){
    $titles[] = $all_update['0']['title'][$i];

    $actionDetails[] = $detailsUpd;

    $with_Upd = xmlrpc_get_machine_with_update($all_update['0']['kb'][$i]);

    $count_machine = array_unique($with_Upd['hostname']);
    $count_machine = sizeof($count_machine);

    $machineWithUpd[] = $count_machine;

    $without_Upd = xmlrpc_get_count_machine_as_not_upd($all_update['0']['kb'][$i]);

    $machineWithoutUpd[] = $without_Upd['0']['nb_machine_missing_update'];

    if ($without_Upd['0']['nb_machine_missing_update'] != "0")
    {
        $compliance_rate = ($count_machine / $without_Upd['0']['nb_machine_missing_update']) * 100;
    }
    else
    {
        $compliance_rate = '100';
    }

    $color = colorconf($compliance_rate);

    $complRates[] ="<div class='progress' style='width: ".$compliance_rate."%; background : ".$color."; font-weight: bold; color : white; text-align: right;'> ".$compliance_rate."% </div>";
}

for($i=0; $i < $count_partial_white; $i++)
{
    $titles[] = $all_update['1']['title'][$i];

    $actionDetails[] = $detailsUpd;

    $with_Upd = xmlrpc_get_machine_with_update($all_update['1']['kb'][$i]);

    $count_machine = array_unique($with_Upd['hostname']);
    $count_machine = sizeof($count_machine);

    $machineWithUpd[] = $count_machine;

    $without_Upd = xmlrpc_get_count_machine_as_not_upd($all_update['1']['kb'][$i]);

    $machineWithoutUpd[] = $without_Upd['0']['nb_machine_missing_update'];

    if ($without_Upd['0']['nb_machine_missing_update'] != "0")
    {
        $compliance_rate = ($count_machine / $without_Upd['0']['nb_machine_missing_update']) * 100;
    }
    else
    {
        $compliance_rate = '100';
    }

    $color = colorconf($compliance_rate);

    $complRates[] ="<div class='progress' style='width: ".$compliance_rate."%; background : ".$color."; font-weight: bold; color : white; text-align: right;'> ".$compliance_rate."% </div>";
}

$n = new OptimizedListInfos($titles, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($machineWithUpd, _T("Machine with this updates", "updates"));
$n->addExtraInfo($machineWithoutUpd, _T("Machine without this updates", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actionDetails);

$n->display();
?>
