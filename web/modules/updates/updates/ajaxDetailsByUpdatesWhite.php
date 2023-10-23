<?php
/**
 * (c) 2023 Siveo, http://siveo.net/
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
require_once("modules/base/includes/computers.inc.php");

global $conf;
$p = new PageGenerator(_T("Details by White Updates", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$filterCTX = "Microsoft";
$field = "platform";

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filterCTX;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = htmlspecialchars($_GET['entity']);

$ctx['uuid'] = $uuid;

//$uuidCut = substr($uuid, -1);


$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$count_enabled_updates = 0;
$params = [];

$enabled_updates_list = xmlrpc_get_enabled_updates_list($uuid, 'white', $start, $maxperpage, $filter);

$count_enabled_updates = $enabled_updates_list['nb_element_total'];


if ($uuid == '')
{
    $typeOfDetail = "group";
}
else
{
    $typeOfDetail = "entitie";
}

$entityMachineList = xmlrpc_xmppmaster_get_machines_list($start, $end, $ctx);
$filterGid = array('gid' => $gid);
$groupMachineList = getRestrictedComputersList(0, -1, $filterGid, False);

function colorconf($conf){
    $colorDisplay=array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
    return $colorDisplay[intval(($conf-($conf%10))/10)];
}


$any_n = "/\d+? \d+? .*$/";

$detailsUpd = new ActionItem(_T("Details", "updates"),"detailsSpecificUpdate","auditbymachine","", "updates", "updates");

$kbs_gray = [];
$updateids_gray = [];
$titles = [];
$complRates = [];
$machineWithUpd = [];
$machineWithoutUpd = [];
$actionDetails = [];

$machineWithoutUpd = $enabled_updates_list['missing'];


for($i=0; $i < $count_enabled_updates; $i++)
{
    $in_unique_with_Upd = "False";
    $in_unique_without_Upd = "False";

    $params[] = array('kb' => $enabled_updates_list['kb'][$i], 'updateid' => $enabled_updates_list['updateid'][$i]);

    //$compliances = xmlrpc_get_count_machines_by_update($enabled_updates_list['updateid'][$i]);
    $with_Upd = xmlrpc_get_count_machine_with_update($enabled_updates_list['kb'][$i]);
    $titles[] = $enabled_updates_list['title'][$i];
    $actionDetails[] = $detailsUpd;

    $machineWithUpd[] = $with_Upd['nb_machines'] + $enabled_updates_list['installed'][$i];
    $totalMachines = $machineWithoutUpd[$i] + $with_Upd['nb_machines'];

    $compliance_rate = intval(($with_Upd['nb_machines'] / $totalMachines)*100);
    /*if ($without_Upd['0']['nb_machine_missing_update'] != "0")
    {
        $compliance_rate = intval(($with_Upd['nb_machines'] / ($without_Upd['0']['nb_machine_missing_update'] + $with_Upd['nb_machines'])) * 100);
    }
    else
    {
        $compliance_rate = '100';
    }*/

    $color = colorconf($compliance_rate);
    $complRates[] ="<div class='progress' style='width: ".$compliance_rate."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$compliance_rate."% </div>";
}

$n = new OptimizedListInfos($titles, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($machineWithUpd, _T("Machines with this update", "updates"));
$n->addExtraInfo($machineWithoutUpd, _T("Machines without this update (waiting)", "updates"));

$n->setItemCount($count_enabled_updates);
$n->setNavBar(new AjaxNavBar($count_enabled_updates, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actionDetails);

$n->display();
?>
