<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
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

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");
require_once("includes/xmlrpc.inc.php");

$result = xmlrpc_getAllVMList();

foreach ($result as $key => $value) {
    $id[] = $value['id'];
    $name[] = $value['name'];
    $name_clean[] = remove_underscore($value['name']);
    if($value['status'] == "Shutoff"){
        $presencesClass[] = "machineName";
        $actionGuac[] = new EmptyActionItem1(_T("VNC", "testenv"), "launch", "guacag", "name", "testenv", "testenv", null, 800);
        $actionStart[] = new ActionItem(_T("Start", "testenv"), "start", "start", "name", "testenv", "testenv");
        $actionStop[] = new EmptyActionItem1(_T("Stop", "testenv"), "stop", "stopg", "name", "testenv");
    }
    else{
        $presencesClass[] = "machineNamepresente";
        $actionGuac[] = new ActionPopupItem(_T("VNC", "testenv"), "launch", "guaca", "name", "testenv", "testenv", null, 800);
        $actionStart[] = new EmptyActionItem1(_T("Start", "testenv"), "start", "startg", "name", "testenv", "testenv");
        $actionStop[] = new ActionItem(_T("Stop", "testenv"), "stop", "stop", "name", "testenv");
    }
}

foreach($name as $value){
    $info = xmlrpc_getVMInfo($value);
    $info_all_vm[] = $info;
}

foreach($info_all_vm as $key => $value){
    $architecture[] = $value['architecture'];
    $uuid[] = $value['uuid'];
    $cpu[] = $value['currentCpu'];
    $ram[] = $value['maxMemory'] . " Mo";
    $port_vnc[] = ($value['port_vnc'] != -1) ? $value['port_vnc'] : 'Pas de port';
}

foreach($uuid as $value){
    $ids[] = 'guacamole_'.$value;
}

$n = new OptimizedListInfos($name_clean, _T("Statut", "testenv"));
$n->setNavBar(new AjaxNavBar(count($name_clean), $filter));
$n->setTableHeaderPadding(1);
$n->setCssIds($ids);
$n->start = 0;
$n->end = 10;
$n->setItemCount(count($name));
$n->setNavBar(new AjaxNavBar(count($name), $filter));
$n->setParamInfo($params);
$n->setMainActionClasses($presencesClass);

$n->addActionItem(new ActionItem(_T("Edit", "testenv"), "edit", "edit", "name", "testenv"));

$n->addActionItem($actionGuac);
$n->addActionItem($actionStart, "name", "testenv");
$n->addActionItem($actionStop, "name", "testenv");

$n->addActionItem(new ActionItem(_T("Delete", "testenv"), "delete", "delete", "name", "testenv"));

$n->addExtraInfo($architecture, _T("Architecture", "testenv"));
$n->addExtraInfo($cpu, _T("CPU", "testenv"));
$n->addExtraInfo($ram, _T("RAM", "testenv"));
$n->addExtraInfo($port_vnc, _T("Port VNC", "testenv"));

$n->display();
?>

<style>
    li.startg a {
        padding: 5px 0px 5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("img/actions/play.svg");
        background-repeat: no-repeat;
        background-position: left top;
        background-size: 25px 25px;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity: 0.5;
    }

    li.stopg a {
        padding: 5px 0px 5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("img/actions/stop.svg");
        background-repeat: no-repeat;
        background-position: left top;
        background-size: 25px 25px;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity: 0.5;
    }
</style>
