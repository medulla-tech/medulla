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
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/widgets.inc.php");

function quick_get($param, $is_checkbox = False) {
    if ($is_checkbox) {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    }
    else if (isset($_POST[$param]) && $_POST[$param] != '') {
        return (isset($_POST[$param])) ? $_POST[$param] : '';
    }
    else
      return (isset($_GET[$param])) ? $_GET[$param]: '';
}
require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Deploy specific Update", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();


$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);



$entity="";
if(isset($_GET['entity'])){
    $entity = htmlentities($_GET['entity']);
}

$entityName = "";
if(isset($_GET['completeName'])){
    $entityName= htmlentities($_GET['completeName']);
}

$title = "";
if(isset($_GET["title"])){
    $title = htmlentities($_GET['title']);
}

$pid = "";
if(isset($_GET["pid"])){
    $pid = htmlentities($_GET['pid']);
}

$kb = "";
if(!empty($_GET['kb'])){
    $kb = htmlentities($_GET['kb']);
}
if($_POST['bconfirm']){
    // Lance ici le déclancheur
    xmlrpc_pending_entity_update_by_pid($entity, $pid, $startdate, $enddate);
}

$label = htmlentities($_GET['ltitle']);
$version = htmlentities($_GET['version']);

$machines = xmlrpc_get_updates_machines_by_entity($entity, $pid, $start, $end, $filter);
$deployName = get_def_package_label($label, $version, "-@upd@");

$groupName = sprintf(_T("Install %s on entity %s"), $kb, $entityName);
$grp = [];
foreach($machines as $machine){
    $grp[$machine['uuid_inventorymachine'].'##'.$machine['hostname']] = ["hostname"=> $machine['hostname'], 'uuid'=>$machine['uuid_inventorymachine'], 'groupname'=>$groupName];
}
$group = new Group();
$gid = $group->create($groupName, false);
$group->addMembers($grp);

// Used to set start and end date
$current = time();
$start_date = date("Y-m-d h:i:s", $current);
$end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d h:i:s", $end_date);

$params = [];
$familyNames = [];

$paramsToSend =[
    "papi"=>"IyMjIyMj",
    "name"=>"",
    "hostname"=>"",
    "uuid"=>"",
    "gid"=>$gid,
    "from"=>"base|computers|groupmsctabs|tablogs",
    "pid"=>$pid,
    "ltitle"=> $deployName,
    "create_directory"=>"on",
    "start_script"=>"on",
    "clean_on_success"=>"on",
    "do_reboot"=>"",
    "do_wol"=>"",
    "do_inventory"=>"on",
    "next_connection_delay"=>60,
    "max_connection_attempt"=>3,
    "maxbw"=>0,
    "copy_mode"=>"push",
    "deployment_intervals"=>"",
    "tab"=>"tablaunch",
    "badvanced"=>1,
    "start_date"=>$start_date,
    "end_date"=>$end_date
];
header("location:".urlStrRedirect("base/computers/groupmsctabs", $paramsToSend));

?>
