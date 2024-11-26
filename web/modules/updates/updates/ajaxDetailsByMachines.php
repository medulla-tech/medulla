<?php
/**
 * (c) 2022-2024 Siveo, http://siveo.net/
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
require_once("modules/updates/includes/html.inc.php");

$location = (isset($_GET['location'])) ? htmlentities($_GET['location']) : "";
$gid = (isset($_GET['gid'])) ? htmlentities($_GET['gid']) : "";
$groupname = (isset($_GET['groupname'])) ? htmlentities($_GET['groupname']) : "";
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$field = "";
$contains = (isset($_GET['contains'])) ? htmlentities($_GET['contains']) : "";

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? htmlentities($_GET['maxperpage']) : htmlentities($config['maxperpage']);
$end = (isset($_GET['end'])) ? (int)htmlentities($_GET['end']) : $start+$maxperpage;
$entity = !empty($_GET['entity']) ? htmlspecialchars($_GET['entity']) : "";
$entityName = !empty($_GET['completename']) ? htmlentities($_GET['completename']) : "";
$ctx = [];
// location generates a filter on entity
$ctx['location'] = !empty($location) ? $location : $entity;
$ctx['filter'] = $filter;
$ctx['field'] = $field;
$ctx['contains'] = $contains;
$ctx['start'] = $start;
$ctx["end"] = $end;
$ctx['maxperpage'] = $maxperpage;

$params = [];
$filterOn = [];

if ($entity == '') {
    $typeOfDetail = "group";
    $filterOn = array('gid' => $gid);
    $ctx['gid'] = $gid;

    // Needed all machines of the group to calculate the compliance rate
    $_machines = getRestrictedComputersList($start, $start+$maxperpage, $ctx, true);

    $machines = [
        "uuid"=>[],
        "cn" => [],
        "os" =>[],
        "missing"=>[],
        "installed"=>[],
        "total"=>[],
        "compliance"=>[],
        "complianceRate"=>[],
        "actionDetailByMachines"=>[],
        "actionPendingByMachines"=>[],
        "actionDoneByMachines"=>[],
    ];
    foreach($_machines as $uuid=> $mach){
        $machines["uuid"][] = $uuid;
        $machines["cn"][] = $mach[1]["cn"][0];
        $machines["os"][] = $mach[1]["os"];

        $machines["actionPendingByMachines"][] = $pendingByMach;
        $machines["actionDetailByMachines"][] = $detailsByMach;
        $machines["actionDoneByMachines"][] = $doneByMach;

        //FUNCTION TO GET ID
        $xmppdatas = xmlrpc_get_idmachine_from_name($mach[1]["cn"][0]);
        $id_machine = $xmppdatas[0]['id_machine'];
        $compliance_computer = xmlrpc_get_conformity_update_by_machines(['ids' => [$id_machine], 'uuids' => [$uuid]]);
        $compliance = round($compliance_computer[$uuid]['compliance']);
        $missing = !empty($compliance_computer[$uuid]['missing']) ? $compliance_computer[$uuid]['missing'] : 0;
        $installed = !empty($compliance_computer[$uuid]['installed']) ? $compliance_computer[$uuid]['installed'] : 0;
        $total = !empty($compliance_computer[$uuid]['total']) ? $compliance_computer[$uuid]['total'] : 0;

        $color = colorconf($compliance);

        $complRate = "<div class='progress' style='width: ".$compliance."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$compliance."% </div>";
        $params[] = [
            "machineid" => $id_machine,
            "inventoryid" => $k,
            "cn" => $v[1]['cn'][0]
        ];
        $machines["installed"][] = $installed;
        $machines["missing"][] = $missing;
        $machines["inprogress"] = [];
        $machines["total"][] = $total;
        $machines["compliance"][] = ($missing == 0) && ($installed == 0) ? 0 : $compliance;
        $machines["complianceRate"][] = ($missing == 0) && ($installed == 0) ? "-" : $complRate;
    }
    $count = getRestrictedComputersListLen($ctx, true);
    $tabletitle = sprintf(_T("Computers from group %s", "updates"), $groupname);

} else {
    $typeOfDetail = "entitie";
    $filterOn = array('entity' => $entity);

    $tabletitle = sprintf(_T("Computers from entity %s", "updates"), $entityName);
    // No usage
    $match = (int)str_replace('UUID', '', $entity);

    $compliance_bloc = "";

    $source = isset($_GET['source']) ? $_GET['source'] : "xmppmaster";

    if ($source == "glpi") {
        $detailsByMachDefault = new EmptyActionItem1(_T("View details", "updates"), "deploySpecificUpdate", "displayg", "", "updates", "updates");
        $pendingByMachDefault = new EmptyActionItem1(_T("Pending Updates", "updates"), "pendingUpdateByMachine", "pendingg", "", "updates", "updates");
        $doneByMachDefault = new EmptyActionItem1(_T("Updates History", "updates"), "auditUpdateByMachine", "historyg", "", "updates", "updates");

        $machines = xmlrpc_get_machines_list1($start, $maxperpage, $ctx);
    } else {
        $detailsByMachDefault = new ActionItem(_T("View details", "updates"), "deploySpecificUpdate", "display", "", "updates", "updates");
        $pendingByMachDefault = new ActionItem(_T("Pending Updates", "updates"), "pendingUpdateByMachine", "pending", "", "updates", "updates");
        $doneByMachDefault = new ActionItem(_T("Updates History", "updates"), "auditUpdateByMachine", "history", "", "updates", "updates");

        $machines = xmlrpc_get_machines_xmppmaster($start, $maxperpage, $ctx);
    }

    $count = $machines['count'];
    $xmppdatas = $machines["xmppdata"];
    $machines = $machines['data'];

    $machinesIds = [
        "uuids" => [],
        "ids" => []
    ];
    foreach($machines["uuid"] as $glpiId){
        $uuid = "UUID".$glpiId;
        $machinesIds["uuids"][] = $uuid;
        $machinesIds["ids"][] = !empty($xmppdatas[$uuid]) ? $xmppdatas[$uuid]["id"] : 0;
    }

    $actionsPerMachine = [];
    foreach ($machinesIds["uuids"] as $uuid) {
        $check_machine = xmlrpc_get_machine_in_both_sources($uuid);
        $actionsPerMachine[$uuid] = (!empty($check_machine) && isset($check_machine[$uuid]) && $check_machine[$uuid])
            ? [
                "details" => new ActionItem(_T("View details", "updates"), "deploySpecificUpdate", "display", "", "updates", "updates"),
                "pending" => new ActionItem(_T("Pending Updates", "updates"), "pendingUpdateByMachine", "pending", "", "updates", "updates"),
                "done" => new ActionItem(_T("Updates History", "updates"), "auditUpdateByMachine", "history", "", "updates", "updates"),
            ]
            : [
                "details" => $detailsByMachDefault,
                "pending" => $pendingByMachDefault,
                "done" => $doneByMachDefault,
            ];
    }

    $compliance_computers = xmlrpc_get_conformity_update_by_machines($machinesIds);

    $machines["missing"] = [];
    $machines["inprogress"] = [];
    $machines["installed"] = [];
    $machines["total"] = [];
    $machines["compliance"] = [];
    $machines["complianceRate"] = [];
    $machines["actionDetailByMachines"] = [];
    $machines["actionPendingByMachines"] = [];
    $machines["actionDoneByMachines"] = [];

    $_count = count($machines['uuid']);
    for($i = 0; $i < $_count; $i++) {
        $uuid = 'UUID'.$machines["uuid"][$i];

        $missing = !empty($compliance_computers[$uuid]) ? $compliance_computers[$uuid]["missing"] : 0;
        $inprogress = !empty($compliance_computers[$uuid]) ? $compliance_computers[$uuid]["inprogress"] : 0;
        $installed = !empty($compliance_computers[$uuid]) ? $compliance_computers[$uuid]["installed"] : 0;
        $compliance = !empty($compliance_computers[$uuid]) ? round($compliance_computers[$uuid]["compliance"]) : 0;

        $machines["missing"][] = $missing;
        $machines["inprogress"][] = $inprogress;
        $machines["installed"][] = $installed;
        $machines["compliance"][] = $compliance;

        $color = colorconf($compliance);
        $complianceRate = ($missing == 0 && $installed == 0) ? '-'
            : "<div class='progress' style='width: {$compliance}%; background : {$color}; font-weight: bold; color : black; text-align: right;'> {$compliance}% </div>";
        $machines["complianceRate"][] = $complianceRate;

        $machines["total"][] = !empty($compliance_computers[$uuid]) ? $compliance_computers[$uuid]["total"] : 0;

        $machines["actionDetailByMachines"][] = $actionsPerMachine[$uuid]["details"];
        $machines["actionPendingByMachines"][] = $actionsPerMachine[$uuid]["pending"];
        $machines["actionDoneByMachines"][] = $actionsPerMachine[$uuid]["done"];
    }

    $params = [];
    foreach ($machines["uuid"] as $i => $uuid) {
        $params[] = [
            "machineid" => isset($xmppdatas["UUID" . $uuid]["id"]) ? $xmppdatas["UUID" . $uuid]["id"] : null,
            "inventoryid" => $uuid,
            "cn" => $machines["cn"][$i]
        ];
    }
}

// Display group compliance, for entity, compliance_bloc == ""
echo $compliance_bloc;

echo "<br>";
echo "<br>";

echo '<h2>'.$tabletitle.'</h2>';


$n = new OptimizedListInfos($machines["cn"], _T("Machine name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($machines["os"], _T("Platform", "updates"));
$n->addExtraInfo($machines["complianceRate"], _T("Compliance rate", "updates"));
$n->addExtraInfo($machines["missing"], _T("Missing updates", "updates"));
$n->addExtraInfo($machines["inprogress"], _T("In progress", "updates"));
$n->addExtraInfo($machines["installed"], _T("Installed updates", "updates"));
$n->addExtraInfo($machines["total"], _T("Total updates", "updates"));
$n->addActionItemArray($machines["actionDetailByMachines"]);
$n->addActionItemArray($machines["actionPendingByMachines"]);
$n->addActionItemArray($machines["actionDoneByMachines"]);
$n->start = 0;
$n->end = $count;
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $ctx['filter']));
$n->setParamInfo($params);
$n->display();
?>

<script>
    function showPopup(event, text) {
        const popup = document.getElementById('popup');
        popup.textContent = text;
        popup.style.display = 'block';

        const offsetX = 15;
        const offsetY = 15;

        let popupLeft = event.pageX - popup.offsetWidth - offsetX;
        if (popupLeft < 0) {
            popupLeft = event.pageX + offsetX;
        }

        popup.style.left = popupLeft + 'px';
        popup.style.top = (event.pageY + offsetY) + 'px';
    }

    function hidePopup() {
        const popup = document.getElementById('popup');
        popup.style.display = 'none';
    }

    const message = <?php echo json_encode(_T("Actions are disabled for this machine (MISSING AGENT)")); ?>;
    document.querySelectorAll('.displayg, .historyg, .pendingg').forEach(function(element) {
        element.addEventListener('mouseover', function(event) {
            showPopup(event, message);
        });

        element.addEventListener('mouseout', hidePopup);
    });
</script>