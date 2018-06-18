<?php
/**
 *  (c) 2015-2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * file xmppmaster/ajaxGroupactionquick.php
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
?>
<?php
    global $conf;
    $maxperpage = $conf["global"]["maxperpage"];
    $filter  = isset($_GET['filter'])?$_GET['filter']:"";
    $start = isset($_GET['start'])?$_GET['start']:0;
    $end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);

    $machinegroup = xmlrpc_getCommand_action_time(10000, $start, $end, $filter);

    $dd = array();
    $dd = $machinegroup['result'];
    $nbitem = $machinegroup['nbtotal'];
$groupormachine = array();
foreach ($dd[4] as $val ){
    if ($val != "") $groupormachine[] = "Grp";else $groupormachine[] = "Mach";
}

$startdate =  array();
foreach ($dd[5] as $val ){
    $startdate[] = date('Y-m-d H:i:s', $val->timestamp);
}
$machinetarget =  array();
foreach ($dd[7] as $val ){
    $target = getRestrictedComputersList(0, -1, array('uuid' => $val), False);
    $machine = $target[$val][1];
    $namemachine = $machine['cn'][0];
    $usermachine = $machine['user'][0];
    $machinetarget[] = $namemachine;
}
$log = array();
$resultmachine = new ActionItem(_T("Os", "xmppmaster"),"QAcustommachgrp","logfile","computer", "xmppmaster", "xmppmaster");

$listnamegroup=[];
$params =  array();
for ($i=0;$i< count( $dd[0] );$i++){
    $param=array();
    $param['cmd_id'] = $dd[0][$i];
    $param['gid']    = $dd[5][$i];
    $param['uuid']   = $dd[7][$i];
    if($param['gid'] != ""){
        $gr = xmlCall("dyngroup.get_group", array($param['gid'], false, false));
        $listnamegroup[] = "Grp : ". $gr['name'];
        $param['groupname'] = $_GET["groupname"];
        $param['machname'] =  "";
    }
    else{
        $param['groupname'] = "";
        $machinelist = getRestrictedComputersList(0, -1, array('uuid' => $param['uuid']), False);
        $machine = $machinelist[$_GET['uuid']][1];
        $namemachine = $machine['cn'][0];
        $usermachine = $machine['user'][0];
        $listnamegroup[] = "Mach : ".$namemachine;
        $param['machname'] =  $namemachine;
    }
    $param['login']  = $dd[2][$i];
    $param['os']     = $dd[3][$i];
    $param['date']   = $startdate[$i];
    $param['namecmd'] = $_GET["namecmd"];
    $logs[] = $resultmachine;
    $params[] = $param;
}

$n = new OptimizedListInfos( $dd[1], _T("Custom Command", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $dd[3], _T("Os", "xmppmaster"));
$n->addExtraInfo( $startdate, _T("Start date", "xmppmaster"));
$n->addExtraInfo( $dd[2], _T("User", "xmppmaster"));
$n->addExtraInfo( $listnamegroup, _T("Type", "xmppmaster"));
$n->addExtraInfo( $machinetarget, _T("Computer", "xmppmaster"));
$n->setTableHeaderPadding(1);
$n->setItemCount($nbitem);
$n->setNavBar(new AjaxNavBar($nbitem, $filter));
$n->addActionItemArray($logs);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $nbitem;
$n->display();
echo "<br>";
?>
