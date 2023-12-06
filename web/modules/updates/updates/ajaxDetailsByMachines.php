<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net/
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

function colorconf($conf){
    $colorDisplay = array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
    return $colorDisplay[intval(($conf - ($conf % 10)) / 10)];
}

$location = (isset($_GET['location'])) ? htmlentities($_GET['location']) : "";
$gid = (isset($_GET['gid'])) ? htmlentities($_GET['gid']) : "";
$groupname = (isset($_GET['groupname'])) ? htmlentities($_GET['groupname']) : "";
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$field = "allchamp";
$contains = (isset($_GET['contains'])) ? htmlentities($_GET['contains']) : "";

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? htmlentities($_GET['maxperpage']) : htmlentities($config['maxperpage']);
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage - 1;

$entity = !empty($_GET['entity']) ? htmlspecialchars($_GET['entity']) : "";
$entityName = !empty($_GET['completename']) ? htmlentities($_GET['completename']) : "";
$ctx = [];
// location generates a filter on entity
$ctx['location'] = !empty($location) ? $location : $entity;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;
$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$detailsByMach = new ActionItem(_T("View details", "updates"), "deploySpecificUpdate", "display", "", "updates", "updates");
$detailsByMachEmpty = new EmptyActionItem1(_T("View details", "updates"), "deploySpecificUpdate", "displayg", "", "updates", "updates");
$pendingByMach = new ActionItem(_T("Pending Updates", "updates"), "pendingUpdateByMachine", "pending", "", "updates", "updates");
$doneByMach = new ActionItem(_T("Updates History", "updates"), "auditUpdateByMachine", "history", "", "updates", "updates");

$all_enabled_updates = xmlrpc_get_count_updates_enable();
$all_enabled_updates = $all_enabled_updates['0']['nb_enabled_updates'];
$compliance_bloc = "";

$params = [];
$machineNames = [];
$complRates = [];
$detailsByMachs = [];
$actionPendingByMachines = [];
$actionDoneByMachines = [];
$missingUpdatesMachine = [];
$platform = [];
$filterOn = [];
$total = [];
$installed = [];
$missing = [];

if ($entity == '')
{
    $typeOfDetail = "group";
    $filterOn = array('gid' => $gid);
    $ctx['gid'] = $gid;

    // Needed all machines of the group to calculate the compliance rate
    $listGroup = getRestrictedComputersList(0, -1, $ctx, true, true);
    $group_compliance = xmlrpc_get_conformity_update_for_group(array_keys($listGroup));
    $group_compliance = $group_compliance['0'];

    $color_group_compliance = colorconf($group_compliance['compliance']);

    $compliance_bloc = sprintf(_T("<h2>Global compliance rate for %s</h2>", "updates"), $groupname);
    $compliance_bloc .= "<br>";
    $compliance_bloc .= "<div class='progress' style='max-width: 25%; width: ".$group_compliance['compliance']."%; background : ".$color_group_compliance."; font-weight: bold; color : black; text-align: right;'> ".intval($group_compliance['compliance'])."% </div>";


    $machines = getRestrictedComputersList($start, $end, $ctx, true);
    $count = getRestrictedComputersListLen($ctx, true);
    $tabletitle = sprintf(_T("Computers from group %s", "updates"), $groupname);

    foreach ($machines as $k => $v) {
        $actionPendingByMachines[] = $pendingByMach;
        $actionDoneByMachines[] = $doneByMach;
        $machineNames[] = $v[1]['cn'][0];

        //FUNCTION TO GET ID
        $id_machine = xmlrpc_get_idmachine_from_name($v[1]['cn'][0]);
        $id_machine = $id_machine[0]['id_machine'];
        $compliance_computer = xmlrpc_get_conformity_update_by_machines(['ids' => [$id_machine], 'uuids' => [$k]]);

        $compliance = round($compliance_computer['0']['compliance']);
        $missing[] = $compliance_computer['0']['missing'];
        $installed[] = $compliance_computer['0']['installed'];
        $total[] = $compliance_computer['0']['total'];

        $comp = $compliance_computer['0']['compliance'];
        $missingUpdatesMachine[] = $comp;
        $detailsByMachs[] = $detailsByMach;

        $color = colorconf($compliance);

        $complRates[] = "<div class='progress' style='width: ".$compliance."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$compliance."% </div>";
        $platform[] = $v[1]['os'];
        $params[] = [
            "machineid" => $id_machine,
            "inventoryid" => $k,
            "cn" => $v[1]['cn'][0]
        ];
    }

} else {
    $typeOfDetail = "entitie";
    $filterOn = array('entity' => $entity);

    $tabletitle = sprintf(_T("Computers from entity %s", "updates"), $entityName);
    $machines = xmlrpc_xmppmaster_get_machines_list($start, $maxperpage, $ctx);

    $countPartial = $machines['count'];
    $count = $machines['total'];
    $machines = $machines['data'];
    $compliance_computers = xmlrpc_get_conformity_update_by_machines(["uuids" => $machines['uuid_inventorymachine'], "ids" => $machines['id']]);
    $installed = [];
    $missing = [];
    $compliance = [];

    $machines["missing"] = array_fill(0, $countPartial, 0);
    $machines["installed"] = array_fill(0, $countPartial, 0);
    $machines["total"] = array_fill(0, $countPartial, 0);
    $machines["compliance"] = array_fill(0, $countPartial, 0);

    for($i=0; $i< $countPartial; $i++){
        foreach($compliance_computers as $compliance){
            if($compliance["id"] == $machines["id"][$i]){
                $machines["missing"][$i] = $compliance["missing"];
                $machines["installed"][$i] = $compliance["installed"];
                $machines["total"][$i] = $compliance["total"];
                break;
            }
        }
        if($machines["missing"][$i] == 0){
            $color = colorconf(100);
            $machines["compliance"][$i] = "<div class='progress' style='width: 100%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> 100% </div>";
        }
        else{
            $color = colorconf($compliance["compliance"]);
            $machines["compliance"][$i] = "<div class='progress' style='width: ".$compliance["compliance"]."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$compliance["compliance"]."% </div>";
        }

        $params[] = [
            "machineid" => $machines['id'][$i],
            "inventoryid" => $machines['uuid_inventorymachine'][$i],
            "cn" => $machines['hostname'][$i],
        ];

        $detailsByMachs[] = $detailsByMach;
        $actionPendingByMachines[] = $pendingByMach;
        $actionDoneByMachines[] = $doneByMach;
    }

    $machineNames = $machines['hostname'];
    $platform = $machines["platform"];
    $complRates = $machines["compliance"];
    $missing = $machines["missing"];
    $installed = $machines["installed"];
    $total = $machines["total"];
}

// Display group compliance, for entity, compliance_bloc == ""
echo $compliance_bloc;

echo "<br>";
echo "<br>";

echo '<h2>'.$tabletitle.'</h2>';


$n = new OptimizedListInfos($machineNames, _T("Machine name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($platform, _T("Platform", "updates"));
$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($missing, _T("Missing updates", "updates"));
$n->addExtraInfo($installed, _T("Installed updates", "updates"));
$n->addExtraInfo($total, _T("Total updates", "updates"));
$n->addActionItemArray($detailsByMachs);
$n->addActionItemArray($actionPendingByMachines);
$n->addActionItemArray($actionDoneByMachines);

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $ctx['filter']));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count;
$n->display();
?>
