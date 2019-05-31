<?php
/**
 * (c) 2017 Siveo, http://http://www.siveo.net
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
 *
 * File createMachinesStaticGroupdeploy.php
 *
 */
require_once("modules/dyngroup/includes/dyngroup.php"); // For Group Class
require_once("modules/glpi/includes/xmlrpc.php"); // For total_machines
require_once("modules/xmppmaster/includes/xmlrpc.php"); // For machines_online
require_once("modules/dyngroup/includes/xmlrpc.php");
extract($_GET);

 function creategroup($grpname, $arraygrp, $datagr){
    $tmp = array();
    $groupname = sprintf (_T("Machines $grpname at %s", "glpi"), date("Y-m-d H:i:s"));
    foreach($arraygrp as $uuidmachine ){
        $tmp[$uuidmachine.'##'.$datagr[$uuidmachine][1]["cn"][0]] = ["hostname" => $datagr[$uuidmachine][1]["cn"][0], 'uuid' => $uuidmachine];
    }
    $group = new Group();
    $group->create($groupname, False);
    $group->addMembers($tmp);
    header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
    exit;
  };

$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");
$gr   = getRestrictedComputersList(0,-1, array('gid' =>$gid));
// getRestrictedComputersList(0,-1, {'uuid': ['UUID3','UUID1','UUID2']}, False)
$uuidgr      = array();
$uuidsuccess = array();
$uuiderror   = array();
$uuidprocess = array();
$uuiddefault = array();
$uuidall     = array();
$uuidwol     = array();
$uuidabort   = array();

foreach ($gr as $key => $val){
    $uuidgr[] =  $key;
}

foreach ($info['objectdeploy'] as  $val){
    switch($val['state']){
        case "DEPLOYMENT SUCCESS":
            $uuidsuccess[] = $val['inventoryuuid'];
            break;
        case "DEPLOYMENT ERROR":
            $uuiderror[] = $val['inventoryuuid'];
            break;
        case "DEPLOYMENT START (REBOOT)":
        case "DEPLOYMENT START":
        case "DEPLOYMENT DIFFERED":
            $uuidprocess[] = $val['inventoryuuid'];
            break;
        case "DEPLOYMENT ABORT":
            $uuidabort[] = $val['inventoryuuid'];
            break;
        default:
            $uuiddefault[] = $val['inventoryuuid'];
    }
    $uuidall[] = $val['inventoryuuid'];
}

// recherche wol in group
foreach ($uuidgr as $val){
    if (!in_array($val, $uuidall)) {
        $uuidwol[] = $val;
    }
}

switch($type){
    case "machinewol":
        creategroup("nopresent", $uuidwol, $gr);
        exit;
    break;
    case "machinesucess":
        creategroup("deployonsucess", $uuidsuccess, $gr);
        exit;
    break;
    case "machineerror":
        creategroup("deployonerror", $uuiderror, $gr);
        exit;
    break;
    case "machineprocess":
        creategroup("deployinprocess", $uuidprocess, $gr);
        exit;
    break;
    case "machineabort" :
        creategroup("deployabort", $uuidabort, $gr);
        exit;
    break;
}

?>
