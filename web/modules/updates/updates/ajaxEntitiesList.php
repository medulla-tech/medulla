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
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$entities = getUserLocations();

echo "<pre>";
//print_r($entities);
echo "</pre>";

$detailsByMach = new ActionItem(_T("Details by machines", "updates"),"detailsByMachines","auditbymachine","", "updates", "updates");
$detailsByUpd = new ActionItem(_T("Details by updates", "updates"),"detailsByUpdates","auditbyupdate","", "updates", "updates");
$deployAll = new ActionItem(_T("Deploy all updates", "updates"),"deployAllUpdates","updateall","", "updates", "updates");
$deploySpecific = new ActionItem(_T("Deploy specific updates", "updates"),"deploySpecificUpdate","updateone","", "updates", "updates");

$params = [];
$actiondetailsByMachs = [];
$actiondetailsByUpds = [];
$actiondeployAlls = [];
$actiondeploySpecifics = [];
$entityNames = [];
$complRates = [];

$count = count($entities);
foreach ($entities as $entity) {
    $actiondetailsByMachs[] = $detailsByMach;
    $actiondetailsByUpds[] = $detailsByUpd;
    $actiondeployAlls[] = $deployAll;
    $actiondeploySpecifics[] = $deploySpecific;
    
    $entityNames[] = $entity["completename"];
    $complRates[] = '';
}

$n = new OptimizedListInfos($entityNames, _T("Entity name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actiondetailsByMachs);
$n->addActionItemArray($actiondetailsByUpds);
$n->addActionItemArray($actiondeployAlls);
$n->addActionItemArray($actiondeploySpecifics);
$n->display();
?>
