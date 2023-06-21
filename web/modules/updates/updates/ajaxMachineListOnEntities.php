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
    $colorDisplay=array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
    return $colorDisplay[intval(($conf-($conf%10))/10)];
}

$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$groupname = (isset($_GET['groupname'])) ? $_GET['groupname'] : "";
$filter = "Microsoft";
$field = "platform";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : $config['maxperpage'];
$end = (isset($_GET['end'])) ? $_GET['end'] : $maxperpage - 1;

$uuid = !empty($_GET['uuid']) ? htmlspecialchars($_GET['uuid']) : "";
$entityName = !empty($_GET['completename']) ? htmlentities($_GET['completename']) : "";
$ctx = [];
// location generates a filter on entity
$ctx['location'] = !empty($location) ? $location: $uuid;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;
$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;


$detailsByMach = new ActionItem(_T("View details", "updates"),"deploySpecificUpdate","display","", "updates", "updates");
$detailsByMachEmpty = new EmptyActionItem1(_T("View details", "updates"),"deploySpecificUpdate","displayg","", "updates", "updates");

$all_grey_enable = xmlrpc_get_count_grey_list_enable();
$all_grey_enable = $all_grey_enable['0']['enable_grey'];

$params = [];
$machineNames = [];
$complRates = [];
$detailsByMachs = [];
$missingUpdatesMachine = [];
$platform = [];
$filterOn = [];
if ($uuid == '')
{
    $typeOfDetail = "group";
    $filterOn = array('gid' => $gid);

    // Needed all machines of the group to calculate the compliance rate
    $listGroup = getRestrictedComputersList(0, -1, $filterOn, true, true);

    $group_compliance = xmlrpc_get_conformity_update_for_group(array_keys($listGroup));
    $group_compliance = $group_compliance['0'];

    $color_group_compliance = colorconf($group_compliance['compliance']);

    $compliance_bloc = sprintf(_T("<h2>Global compliance rate for %s</h2>", "updates"), $groupname);
    $compliance_bloc .= "<br>";
    $compliance_bloc .= "<div class='progress' style='max-width: 25%; width: ".$group_compliance['compliance']."%; background : ".$color_group_compliance."; font-weight: bold; color : black; text-align: right;'> ".$group_compliance['compliance']."% </div>";


    $machines = getRestrictedComputersList($start, $end, $filterOn, true);
    $count = getRestrictedComputersListLen($filterOn, True);
    $tabletitle = sprintf(_T("Computers from group %s","updates"), $groupname);

    foreach ($machines as $k => $v) {
        $detailsByMachs[] = $detailsByMach;
        $machineNames[] = $v[1]['cn'][0];

        //FUNCTION TO GET ID
        $id_machine = xmlrpc_get_idmachine_from_name($v[1]['cn'][0]);
        $id_machine = $id_machine[0]['id_machine'];
        $compliance_computer = xmlrpc_get_conformity_update_by_machine($id_machine);

        $comp = $compliance_computer['0']['update_waiting'];
        $missingUpdatesMachine[] = $comp;

        if ($all_grey_enable != '0' and $comp != '0')
        {
            $comp = $comp / $all_grey_enable * 100;
        }

        if ($comp == '0')
        {
            $comp = '100';
        }

        $color = colorconf($comp);

        $complRates[] = "<div class='progress' style='width: ".$comp."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$comp."% </div>";
        $platform[] = $v[1]['os'];
        $params[] = [
            "id"=>$id_machine,
            "glpi_id"=>$k,
            "cn"=>$v[1]['cn'][0],
        ];
    }

}
else
{
    $typeOfDetail = "entitie";
    $filterOn = array('entity' => $uuid);

    $tabletitle = sprintf(_T("Computers from entity %s","updates"), $entityName);
    // No usage
    $match = (int)str_replace('UUID', '', $uuid);

    $compliance_bloc = "";

    $machines = xmlrpc_xmppmaster_get_machines_list($start, $end, $ctx);
    $count = $machines['count'];
    $machines = $machines['data'];
    $compliance_computers = xmlrpc_get_conformity_update_by_machines($machines['id']);

    for($i=0; $i < $count; $i++){
        $machineNames[] = $machines['hostname'][$i];
        $comp = $compliance_computers[(string)$machines['id'][$i]];
        $missingUpdatesMachine[] = $comp;
        $detailsByMachs[] = ($comp == 0) ? $detailsByMachEmpty : $detailsByMach;

        if ($all_grey_enable != '0' and $comp != '0')
        {
            $comp = $comp / $all_grey_enable * 100;
        }

        if ($comp == '0')
        {
            $comp = '100';
        }

        $color = colorconf($comp);

        $complRates[] = "<div class='progress' style='width: ".$comp."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$comp."% </div>";

        $platform[] = $machines['platform'][$i];

        $params[] = [
            "id"=>$machines['id'][$i],
            "glpi_id" => $machines['uuid_inventorymachine'][$i],
            "cn"=>$machines['hostname'][$i],
        ];
    }
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
$n->addExtraInfo($missingUpdatesMachine, _T("Missing updates", "updates"));
$n->addActionItemArray($detailsByMachs);

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $ctx['filter']));
$n->setParamInfo($params);
$n->display();
?>
