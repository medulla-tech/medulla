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
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;

$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

if(!empty($_GET['entity'])){
    $entityId = (!empty($_GET['uuid'])) ? htmlentities($_GET['uuid']) : htmlentities($_GET['entity']);
    $entityCompleteName = htmlentities($_GET['completename']);

    $updates_list = xmlrpc_get_updates_by_entity($entityId, $start, $end, $filter);

    $deployThisUpdate = new ActionItem(_T(sprintf("Deploy this update on entity %s", $entityCompleteName), "updates"),"deployUpdate","quick","", "updates", "updates");
}
else if(!empty($_GET['group'])){
    $gid = htmlentities($_GET['group']);
    $groupname = htmlentities($_GET['groupname']);
    $group = getPGobject($gid, true);
    $deployThisUpdate = new ActionItem(_T(sprintf("Deploy this update on group %s", $groupname), "updates"),"deployUpdate","quick","", "updates", "updates");
    $machinesListGlpi = getRestrictedComputersList(0,-1,['gid'=>$gid]);
    $machinesList = array_keys($machinesListGlpi);
    $updates_list = xmlrpc_get_updates_by_uuids($machinesList, $start, $end, $filter);

}
else if(!empty($_GET['id']) || !empty($_GET['glpi_id'])){
    $updates_list = ["datas"=>[], "count"=>0];
    $machineid = (!empty($_GET['id'])) ? htmlentities($_GET['id']) : '';
    $inventoryid = (!empty($_GET['glpi_id'])) ? htmlentities($_GET['glpi_id']) : '';
    $machinename = (!empty($_GET['cn']) )? htmlentities($_GET['cn']) : '';
    $deployThisUpdate = new ActionItem(_T(sprintf("Deploy this update on machine %s", $machinename), "updates"),"deployUpdate","quick","", "updates", "updates");
    $updates_list = xmlrpc_get_updates_by_uuids([$inventoryid], $start, $end, $filter);

}
$params = [];
$names_updates = [];
$kb_updates = [];
$actionspeclistUpds = [];

$count = $updates_list['total'];
$updates_list = $updates_list['datas'];

$row = 0;

foreach ($updates_list as $update) {
    $actionspeclistUpds[] = $deployThisUpdate;
    $kb_updates[] = 'KB'.$update['kb'];
    $names_updates[] = $updates_list[$row]["pkgs_label"];
    $version_updates[] = $updates_list[$row]['pkgs_version'];
    $params[] = [
        "entity"=>$entityId,
        "pid" => $updates_list[$row]["update_id"],
        "kb" => $updates_list[$row]["kb"],
        "entity"=> $entityId,
        "completeName" => $entityCompleteName,
        "ltitle"=>$updates_list[$row]["pkgs_label"],
        "version"=>$updates_list[$row]['pkgs_version'],
    ];
    $row++;
}

$n = new OptimizedListInfos($names_updates, _T("Update name", "updates"));
$n->addExtraInfo($kb_updates, _T("KB", "updates"));
$n->disableFirstColumnActionLink();
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count;
$n->addActionItemArray($actionspeclistUpds);

$n->display();
?>
