<?php
/**
 * (c) 2022 Siveo, http://siveo.net
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

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");

global $conf;
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$maxperpage = $conf['global']['maxperpage'];
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

if(isset($_SESSION['sharings'])){
    $sharings = $_SESSION['sharings'];
}
else{
    $sharings = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
}
if($sharings['config']['centralizedmultiplesharing'] == true){
}

else{
}
$result = xmlrpc_get_acknowledges_for_sharings($sharings, $start, $maxperpage, $filter);

$count = $result['total'];
$params = $result['datas'];
$modifyAction = new ActionPopupItem(_T("Modify Authorisations", "kiosk"), "modifyAcknowledge", "edit", "kiosk", "kiosk");

$status = [];
$package_uuids = [];
$package_names = [];
$profile_names = [];
$askusers = [];
$askdates = [];
$startdates = [];
$enddates = [];
$acknowledgedbyusers = [];
$modifyActions = [];

foreach($params as $elem){
    $status[] = $elem['status'];
    $package_names[] = $elem['package_name'];
    $package_uuids[] = $elem['package_uuid'];
    $profile_names[] = $elem['profile_name'];
    $askusers[] = $elem['askuser'];
    $askdates[] = $elem['askdate'];
    $startdates[] = $elem['startdate'];
    $enddates[] = $elem['enddate'];
    $acknowledgedbyusers[] = $elem['acknowledgedbyuser'];
    $modifyActions[] = $modifyAction;
}


$n = new OptimizedListInfos($package_names, _T("Package Name", "kiosk"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($profile_names, _T("Profile Name", "kiosk"));
// $n->addExtraInfo($package_uuids, _T("Package Uuids", "kiosk"));
$n->addExtraInfo($askusers, _T("Asked by User", "kiosk"));
$n->addExtraInfo($askdates, _T("Asked On", "kiosk"));
$n->addExtraInfo($startdates, _T("Starts On", "kiosk"));
$n->addExtraInfo($enddates, _T("Ends On", "kiosk"));
$n->addExtraInfo($status, _T("Status", "kiosk"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
$n->addActionItemArray($modifyActions);
// $n->addActionItemArray($editActions);
// $n->addActionItemArray($delActions);
$n->start = 0;
$n->end = $count;
$n->display();
?>
