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
// file : modules/updates/updates/ajaxMajorDetailsByMachines.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");

$location = (isset($_GET['location'])) ? htmlentities($_GET['location']) : "";
$gid = (isset($_GET['gid'])) ? htmlentities($_GET['gid']) : "";
$groupname = (isset($_GET['groupname'])) ? htmlentities($_GET['groupname']) : "";
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$field = "";
$contains = (isset($_GET['contains'])) ? htmlentities($_GET['contains']) : "";

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage'])) ? htmlentities($_GET['maxperpage']) : htmlentities($config['maxperpage']);
$end = (isset($_GET['end'])) ? (int)htmlentities($_GET['end']) : $start+$maxperpage;
$entity = !empty($_GET['entity']) ? htmlspecialchars($_GET['entity']) : "";
$entityName = !empty($_GET['name']) ? htmlentities($_GET['name']) : "";
$entityCompleteName = !empty($_GET['completename']) ? htmlentities($_GET['completename']) : "";
$p = new PageGenerator(sprintf("%s [%s]",_T("Entitie", 'updates'),$entityName));
$p->setSideMenu($sidemenu);
$p->display();
    if ($_GET['source'] == "xmppmaster" ){
        $statglpiversion = xmlrpc_get_os_xmpp_update_major_details($_GET['entity'],$filter);
    }else{
        $statglpiversion=xmlrpc_get_os_update_major_details($_GET['entity'],$filter );
    };

// Nom machine	Système d'exploitation	Mises à jour Major

$params = [];
$filterOn = [];
$idmachinefrom_xmpp_or_glpi='machineidmajor'; // id xmppmaster
 if ($_GET['source'] != "xmppmaster" ){
         $idmachinefrom_xmpp_or_glpi='inventoryidmajor'; // id glpi
    }

foreach($statglpiversion['id_machine'] as $key=>$valeur){
$actionspeclistUpds[] = new ActionPopupItem(_T(sprintf("Deploy this update on machine %s", $statglpiversion['machine'][$key]), "updates"), "deployUpdatemajor", "updateone", "", "updates", "updates");
        $parammachineinfo="";
 $params[] = array(
        'entity_id' => $entity,
        'entity_name' => $entityName,
        'complete_name' =>$entityCompleteName,
        'maxperpage' => $maxperpage,
        'source' => $source,
         $idmachinefrom_xmpp_or_glpi => $valeur,
        'cn'=> $statglpiversion['machine'][$key],
        'platform'=> $statglpiversion['platform'][$key],
        'version'=> $statglpiversion['version'][$key],
        'update'=> $statglpiversion['update'][$key],
    );
}

$n = new OptimizedListInfos($statglpiversion["machine"], _T("Machine name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($statglpiversion["platform"], _T("Platform", "updates"));
$n->addExtraInfo($statglpiversion["version"], _T("version", "updates"));
$n->addExtraInfo($statglpiversion["update"], _T("update", "updates"));
//$n->addActionItemArray($actionspeclistUpds);

$n->start = 0;
$n->end = $statglpiversion["nb_machine"];
$n->setItemCount($statglpiversion["nb_machine"]);
$n->setNavBar(new AjaxNavBar($statglpiversion["nb_machine"], $ctx['filter']));
$n->setParamInfo($params);
$n->display();

?>
