<?php
/**
 * (c) 2022-2024 Siveo, http://siveo.net/
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
require_once("modules/updates/includes/html.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

$_entities = getUserLocations();
$filtered_entities = [];
foreach($_entities as $entity) {
    if(preg_match("#".$filter."#i", $entity['name']) || preg_match("#".$filter."#i", $entity['completename'])) {
        $filtered_entities[] = $entity;
    }
}
$count = count($filtered_entities);
$entities = array_slice($filtered_entities, $start, $maxperpage, false);
$source = isset($_GET['source']) ? $_GET['source'] : "xmppmaster";
$entitycompliances = xmlrpc_get_conformity_update_by_entity($entities, $source);

$detailsByMach = new ActionItem(_T("Details by machines", "updates"), "detailsByMachines", "auditbymachine", "", "updates", "updates");
$detailsByUpd = new ActionItem(_T("Details by updates", "updates"), "detailsByUpdates", "auditbyupdate", "", "updates", "updates");
$deployAll = new ActionItem(_T("Deploy all updates", "updates"), "deployAllUpdates", "updateall", "", "updates", "updates");
$emptyDeployAll = new EmptyActionItem1(_T("Deploy all updates", "updates"), "deployAllUpdates", "updateallg", "", "updates", "updates");
$deploySpecific = new ActionItem(_T("Deploy specific updates", "updates"), "deploySpecificUpdate", "updateone", "", "updates", "updates");
$emptyDeploySpecific = new EmptyActionItem1(_T("Deploy specific updates", "updates"), "deploySpecificUpdate", "updateoneg", "", "updates", "updates");

$params = [];
$actiondetailsByMachs = [];
$actiondetailsByUpds = [];
$actiondeployAlls = [];
$actiondeploySpecifics = [];
$entityNames = [];
$complRates = [];
$totalMachine = [];
$nbupdate = [];
$identity = array();

foreach ($entitycompliances as $entitycompliance) {
    $identity[$entitycompliance['entity']] = array(
        "conformite" => $entitycompliance['conformite'],
        "totalmach" => $entitycompliance['totalmach'],
        "nbupdate" => $entitycompliance['nbupdate'],
        "nbmachines" => $entitycompliance['nbmachines'],
        "entity" => $entitycompliance['entity']);
}

foreach ($entities as $entity) {
    $nbmachines = 0;
    $id_entity = intval(substr($entity["uuid"], 4));
    $actiondetailsByMachs[] = $detailsByMach;
    $actiondetailsByUpds[] = $detailsByUpd;
    $entityNames[] = $entity["completename"];
    $params[] = array(
        'entity' => $entity['uuid'],
        'completename' => $entity['completename'],
        'source' => $source
    );
    $color = colorconf(100);
    if (isset($identity[$id_entity])) {
        $conformite = intval($identity[$id_entity]['conformite']);
        $color = colorconf($conformite);
        $totalmach = intval($identity[$id_entity]['totalmach']);
        $nbupdateentity = intval($identity[$id_entity]['nbupdate']);
        $nbmachines = intval($identity[$id_entity]['nbmachines']);

        if($conformite == 100) {
            $actiondeployAlls[] = $emptyDeployAll;
            $actiondeploySpecifics[] = $emptyDeploySpecific;

        } else {
            $actiondeployAlls[] = $deployAll;
            $actiondeploySpecifics[] = $deploySpecific;
        }
    } else {
        $conformite = "100";
        $totalmach = 0;
        $nbupdateentity = 0;
        $actiondeployAlls[] = $emptyDeployAll;
        $actiondeploySpecifics[] = $emptyDeploySpecific;
    }
    $complRates[] = "<div class='progress' style='width: ".$conformite."%; background : ".$color."; font-weight: bold; color : black; text-align: right;'> ".$conformite."% </div>";
    $totalMachine[] = $totalmach;
    $nbupdate[] = $nbupdateentity ;
    $nbMachines[] = $nbmachines;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_entity = [];
foreach($entityNames as $name_entity) {
    $ids_entity[] = 'e_'.$name_entity;
}

$n = new OptimizedListInfos($entityNames, _T("Entity name", "updates"));
$n->setcssIds($ids_entity);
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
$n->addExtraInfo($nbupdate, _T("Missing updates", "updates"));
$n->addExtraInfo($nbMachines, _T("Non-compliant machines", "updates"));
$n->addExtraInfo($totalMachine, _T("Total machines", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actiondetailsByMachs);
$n->addActionItemArray($actiondetailsByUpds);
//$n->addActionItemArray($actiondeployAlls);
$n->addActionItemArray($actiondeploySpecifics);
$n->start = 0;
$n->end = $count;
$n->display();
