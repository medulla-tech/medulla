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

$updates_list = [];
if(!empty($_GET['entity'])){
    $entityId = (!empty($_GET['entity'])) ? htmlentities($_GET['entity']) : '';
    $entityCompleteName = htmlentities($_GET['completename']);

    $updates_list = xmlrpc_get_updates_by_entity($entityId, $start, $end, $filter);
    $deployThisUpdate = new ActionPopupItem(_T(sprintf("Deploy this update on entity %s", $entityCompleteName), "updates"),"deployUpdate","updateone","", "updates", "updates");
}
else if(!empty($_GET['group'])){
    $gid = htmlentities($_GET['group']);
    $groupname = htmlentities($_GET['groupname']);
    $group = getPGobject($gid, true);
    $deployThisUpdate = new ActionPopupItem(_T(sprintf("Deploy this update on group %s", $groupname), "updates"),"deployUpdate","updateone","", "updates", "updates");
    $machinesListGlpi = getRestrictedComputersList(0,-1,['gid'=>$gid]);
    $machinesList = array_keys($machinesListGlpi);
    $updates_list = xmlrpc_get_updates_by_uuids($machinesList, $start, $end, $filter);

}
else if(!empty($_GET['machineid']) || !empty($_GET['inventoryid'])){
    $updates_list = ["datas"=>[], "count"=>0];
    $machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET['machineid']) : '';
    $inventoryid = (!empty($_GET['inventoryid'])) ? htmlentities($_GET['inventoryid']) : '';
    $machinename = (!empty($_GET['cn']) )? htmlentities($_GET['cn']) : '';
    $deployThisUpdate = new ActionPopupItem(_T(sprintf("Deploy this update on machine %s", $machinename), "updates"),"deployUpdate","updateone","", "updates", "updates");
    $updates_list = xmlrpc_get_updates_by_uuids([$inventoryid], $start, $end, $filter);
}

$params = [];
$names_updates = [];
$kb_updates = [];
$actionspeclistUpds = [];

$count = $updates_list['total'];
$updates_list = $updates_list['datas'];
$row = 0;

$hostnames = [];
$jids = [];
$severities = [];

foreach ($updates_list as $update) {
    $actionspeclistUpds[] = $deployThisUpdate;
    $kb_updates[] = 'KB'.$update['kb'];
    $names_updates[] = $updates_list[$row]["pkgs_label"];
    $version_updates[] = $updates_list[$row]['pkgs_version'];

    if(!empty($updates_list[$row]['hostname'])){
        $hostnames[] = $updates_list[$row]['hostname'];
    }
    if(!empty($updates_list[$row]['jid'])){
        $jids[] =  $updates_list[$row]['jid'];
    }

    if(!empty($updates_list[$row]['severity'])){
        $severities[] =  $updates_list[$row]['severity'];
    }

    $tmp = [
        "pid" => $updates_list[$row]["update_id"],
        "kb" => $updates_list[$row]["kb"],
        "title"=>$updates_list[$row]["pkgs_description"],
        "ltitle"=>$updates_list[$row]["pkgs_label"],
        "version"=>$updates_list[$row]['pkgs_version'],
    ];
    if(!empty($_GET['entity'])){
        $tmp["entity"] = $entityId;
        $tmp["completeName"] = $entityCompleteName;
    }
    else if(!empty($_GET['group'])){
        $tmp["gid"] = $gid;
        $tmp["groupname"] = $groupname;
    }
    else if(!empty($_GET['machineid']) || !empty($_GET['inventoryid'])){
        $tmp["inventoryid"] = $inventoryid;
        $tmp["machineid"] = $machineid;
        $tmp["cn"] = $machinename;
    }
    $params[] = $tmp;
    $row++;
}

$n = new OptimizedListInfos($severities, _T("Severity", "updates"));
$n->addExtraInfo($names_updates, _T("Update name", "updates"));
$n->addExtraInfo($kb_updates, _T("KB", "updates"));
if($hostnames != []){
    $n->addExtraInfo($hostnames, _T("Machine", "xmppmaster"));
}
if($jids != []){
    $n->addExtraInfo($jids, _T("Jid", "xmppmaster"));
}

$n->disableFirstColumnActionLink();
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count;
$n->addActionItemArray($actionspeclistUpds);

$n->display();
?>
