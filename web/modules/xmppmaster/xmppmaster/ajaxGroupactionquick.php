<?php
/**
 *  (c) 2015-2022 Siveo, http://www.siveo.net
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
    $logs = array();
    $machinegroup = xmlrpc_getCommand_action_time(10000, $start, $end, $filter);

    $dd = array();
    $dd = $machinegroup['result'];
    $nbitem = $machinegroup['nbtotal'];

$startdate =  array();
foreach ($dd[4] as $val ){
    $startdate[] = timestamp_to_datetime($val->timestamp);
}
$machinetarget =  array();
$row = 0;
foreach ($dd[7] as $val ){
    if($val != ""){
        $target = getRestrictedComputersList(0, -1, array('uuid' => $val), False);
        $machine = $target[$val][1];
        $namemachine = $machine['cn'][0];
        $usermachine = $machine['user'][0];
        $machinetarget[]= '<a href="'.urlStrRedirect("base/computers/glpitabs", ["cn"=>$namemachine, "objectUUID"=>$val]).'">'.$namemachine.'</a>';
    }
    else if($val == "" && $dd[8][$row] != ""){
        $xmppmachine = xmlrpc_getMachinefromjid($dd[8][$row]);
        $namemachine = $xmppmachine["hostname"];
        $usermachine = "";
        $machinetarget[]= $namemachine;
    }
    else{
        $namemachine = "";
        $usermachine = "";
        $machinetarget[]= 'undefined';
    }
    $row++;
}
$log = array();
$resultmachine = new ActionItem(_T("Os", "xmppmaster"),"QAcustommachgrp","audit","computer", "xmppmaster", "xmppmaster");
$emptyAction = new EmptyActionItem();

$listnamegroup=[];
$params =  array();
for ($i=0;$i< safeCount( $dd[0] );$i++){
    $param=array();
    $param['cmd_id'] = $dd[0][$i];
    $param['gid']    = $dd[5][$i];
    $param['uuid']   = $dd[7][$i];
    $param['jid']   = $dd[8][$i];
    if($param['gid'] != ""){
        $gr = xmlCall("dyngroup.get_group", array($param['gid'], false, false));
        $listnamegroup[] = _T("Group : ") . $gr['name'];
        $param['groupname'] = isset($_GET["groupname"]) ? $_GET["groupname"] : "";
        $param['machname'] =  "";
    }
    else{
        $param['groupname'] = "";
        if($param['uuid'] != ""){
            $machinelist = getRestrictedComputersList(0, -1, array('uuid' => $param['uuid']), False);
            $machine = $machinelist[$_GET['uuid']][1];
            $namemachine = $machine['cn'][0];
            $usermachine = $machine['user'][0];
            $listnamegroup[] = _T("Computer") .$namemachine;
            $param['machname'] =  $namemachine;
        }
        else if($param['uuid'] == "" && $param['jid'] != ''){
            $xmppmachine = xmlrpc_getMachinefromjid($param['jid']);
            $namemachine = $xmppmachine["hostname"];
            $machinetarget[]= $namemachine;
            $param['machname'] =  $namemachine;
        }
        else{
            $listnamegroup[] = _T("Computer");
            $param['machname'] =  "undefined";
        }
    }
    $param['login']  = $dd[2][$i];
    $param['os']     = $dd[3][$i];
    $param['date']   = $startdate[$i];
    $param['namecmd'] =  isset($_GET["namecmd"]) ? $_GET["namecmd"] : "";
    $logs[] = $dd[7][$i] != "" ? $resultmachine : $emptyAction;
    $params[] = $param;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_grpqa = [];
foreach($dd['1'] as $name_grpqa){
    $ids_grpqa[] = 'rqa_'.$name_grpqa;
}

$n = new OptimizedListInfos( $dd[1], _T("Custom Command", "xmppmaster"));
$n->setcssIds($ids_grpqa);
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
