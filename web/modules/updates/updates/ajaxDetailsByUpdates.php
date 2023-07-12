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
require_once("modules/base/includes/computers.inc.php");

global $conf;
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

$uuid = htmlspecialchars($_GET['uuid']);
$ctx['uuid'] = $uuid;

//$uuidCut = substr($uuid, -1);

$enabled_updates_list = xmlrpc_get_enabled_updates_list($start, $maxperpage, $filter);

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

foreach($groupMachineList[UUID1][1][cn] as $member)
{
    $id_machine = xmlrpc_get_idmachine_from_name($member);

    array_push($groupMachineList[UUID1][1], $id_machine[0]);
}

for($i=0; $i < $count_enabled_updates; $i++)
{
    $in_unique_with_Upd = "False";
    $in_unique_without_Upd = "False";

    $params[] = array('kb' => $enabled_updates_list['kb'][$i]);

    $with_Upd = xmlrpc_get_machine_with_update($enabled_updates_list['kb'][$i]);

    $without_Upd = xmlrpc_get_count_machine_as_not_upd($enabled_updates_list['kb'][$i]);

    $unique_with_Upd = array_unique($with_Upd);
    $unique_without_Upd = array_unique($without_Upd);

    if ($typeOfDetail == "entitie")
    {
        foreach ($unique_with_Upd['hostname'] as $unique)
        {
            if (in_array($unique, $entityMachineList))
            {
                $in_unique_with_Upd = "True";
            }
        }

        foreach ($unique_without_Upd['id_machine'] as $unique)
        {
            if (in_array($unique, $entityMachineList))
            {
                $in_unique_without_Upd = "True";
            }
        }
    }

    if ($typeOfDetail == "group")
    {
        foreach ($unique_with_Upd['hostname'] as $unique)
        {
            if (in_array($unique, $groupMachineList))
            {
                $in_unique_with_Upd = "True";
            }
        }

        foreach ($unique_without_Upd['id_machine'] as $unique)
        {
            if (in_array($unique, $groupMachineList))
            {
                $in_unique_without_Upd = "True";
            }
        }
    }

    /*if ($in_unique_with_Upd == "True" || $in_unique_without_Upd == "True")
    {*/
        $titles[] = $enabled_updates_list['title'][$i];
        $actionDetails[] = $detailsUpd;

        $count_machine = array_unique($with_Upd['hostname']);
        $count_machine = sizeof($count_machine);
        $machineWithUpd[] = $count_machine;

        $machineWithoutUpd[] = $without_Upd['0']['nb_machine_missing_update'];

        if ($without_Upd['0']['nb_machine_missing_update'] != "0")
        {
            $compliance_rate = intval(($count_machine / $without_Upd['0']['nb_machine_missing_update']) * 100);
        }
        else
        {
            $compliance_rate = '100';
        }

        $color = colorconf($compliance_rate);
        $complRates[] ="<div class='progress' style='width: ".$compliance_rate."%; background : ".$color."; font-weight: bold; color : white; text-align: right;'> ".$compliance_rate."% </div>";
    //}
}


$n = new OptimizedListInfos($titles, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($machineWithUpd, _T("Machine with this updates", "updates"));
$n->addExtraInfo($machineWithoutUpd, _T("Machine without this updates (waiting)", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actionDetails);

$n->display();
?>
