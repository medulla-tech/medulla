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

 function creategroup($filter, $uuids){
    $groupname = sprintf (_T('Machines '.$filter['criterion']. ' at %s', "glpi"), date("Y-m-d H:i:s"));

    $group = new Group();
    $group->create($groupname, False);
    $group->addMembers($uuids);
    header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
    exit;
  };

$statuslist = xmlrpc_get_log_status();
$criterion = '';
foreach($statuslist as $status){
  if($type == $status['label'])
    $criterion = $status['status'];
}

if($criterion == '')
{
  switch($type){
    case 'deploymentsuccess':
      $criterion = "DEPLOYMENT SUCCESS";
      break;
    case 'abortontimeout':
      $criterion = "ABORT ON TIMEOUT";
      break;
    case 'abortmissingagent':
      $criterion = "ABORT MISSING AGENT";
      break;
    case 'abortrelaydown':
      $criterion = "ABORT RELAY DOWN";
      break;
    case 'abortalternativerelaysdown':
      $criterion = "ABORT ALTERNATIVE RELAYS DOWN";
      break;
    case 'abortinforelaymissing':
      $criterion = "ABORT INFO RELAY MISSING";
      break;
    case 'errorunknownerror':
      $criterion = "ERROR UNKNOWN ERROR";
      break;
    case 'abortpackageidentifiermissing':
      $criterion = "ABORT PACKAGE IDENTIFIER MISSING";
      break;
    case 'abortpackagenamemissing':
      $criterion = "ABORT PACKAGE NAME MISSING";
      break;
    case 'abortpackageversionmissing':
      $criterion = "ABORT PACKAGE VERSION MISSING";
      break;
    case 'abortpackageworkflowerror':
      $criterion = "ABORT PACKAGE WORKFLOW ERROR";
      break;
    case 'abortdescriptormissing':
      $criterion = " DESCRIPTOR MISSING";
      break;
    case 'abortmachinedisappeared':
      $criterion = "ABORT MACHINE DISAPPEARED";
      break;
    case 'abortuserabort':
      $criterion = "ABORT USER ABORT";
      break;
    case 'abortuserabort':
      $criterion = "ABORT PACKAGE EXECUTION ERROR";
      break;
    case 'abortpackageexecutionerror':
      $criterion = "ABORT PACKAGE EXECUTION ERROR";
      break;
    case 'deploymentstart':
      $criterion = "DEPLOYMENT START";
      break;
    case 'wol1':
      $criterion = "WOL 1";
      break;
    case 'wol2':
      $criterion = "WOL 2";
      break;
    case 'wol3':
      $criterion = "WOL 3";
      break;
    case 'waitingmachineonline':
      $criterion = "WAITING MACHINE ONLINE";
      break;

    case 'deploymentpending':
      $criterion = "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)";
      break;
    case 'deploymentdiffered':
      $criterion = "DEPLOYMENT DIFFERED";
      break;
  }
}

$filter = ['filter'=>'status', 'criterion'=>$criterion];
$getdeployment = xmlrpc_getdeployment($cmd_id, $filter, 0,-1);

$uuids = $getdeployment['datas']['uuid'];
$names = $getdeployment['datas']['hostname'];
$tmp = [];

$raw = 0;
for($i = 0; $i < count($uuids); $i++){
  $name =  explode('.' , $names[$raw]);
  $name = $name[0];
  $uuid = $uuids[$raw];
  $tmp[$uuid.'##'.$name] = ["hostname" => $name, 'uuid' => $uuids[$raw]];
  $raw++;
}

creategroup($filter, $tmp);
?>
