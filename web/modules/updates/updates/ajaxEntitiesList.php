<?php
/**
 * (c) 2022-2025 Siveo, http://siveo.net/
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

$params = [];
$actiondetailsByMachs = [];
$actiondetailsByUpds = [];
$actiondeployAlls = [];
$actiondeploySpecifics = [];
$actionHistories = [];
$entityNames = [];
$complRates = [];
$conformite = [];
$totalMachine = [];
$nbupdate = [];
$ids_entity = []; // id des ligne de la list
$identity = array();
// definition des actions
$detailsByMach = new ActionItem(_T("Details by machines", "updates"), "detailsByMachines", "auditbymachine", "", "updates", "updates");
$detailsByUpd = new ActionItem(_T("Details by updates", "updates"), "detailsByUpdates", "auditbyupdate", "", "updates", "updates");
$deployAll = new ActionItem(_T("Deploy all updates", "updates"), "deployAllUpdates", "updateall", "", "updates", "updates");
$emptyDeployAll = new EmptyActionItem1(_T("Deploy all updates", "updates"), "deployAllUpdates", "updateallg", "", "updates", "updates");
$deploySpecific = new ActionItem(_T("Deploy specific updates", "updates"), "deploySpecificUpdate", "updateone", "", "updates", "updates");
$emptyDeploySpecific = new EmptyActionItem1(_T("Deploy specific updates", "updates"), "deploySpecificUpdate", "updateoneg", "", "updates", "updates");
$actionHistory = new ActionItem(_T("History by Entity", "updates"), "auditByEntity", "history", "", "updates", "updates");
$texte_help = _T("%s updates for %s machines in the %s entity" , "updates");


$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
// Récupérer les emplacements de l'utilisateur
$_entities = getUserLocations();

// Filtrer les entités en fonction d'un motif de recherche
$filtered_entities = [];
foreach ($_entities as $entity) {
    if (preg_match("#" . $filter . "#i", $entity['name']) || preg_match("#" . $filter . "#i", $entity['completename'])) {
        $filtered_entities[] = $entity;
    }
}

// Compter le nombre d'entités filtrées
$count = count($filtered_entities);

// Paginer les entités filtrées pour afficher uniquement un sous-ensemble
$entities = array_slice($filtered_entities, $start, $maxperpage, false);

// Déterminer la source à partir des paramètres GET ou utiliser une valeur par défaut
$source = isset($_GET['source']) ? $_GET['source'] : "xmppmaster";

// Récupérer les mises à jour de conformité pour les entités paginées
$entitycompliances = xmlrpc_get_conformity_update_by_entity($entities, $source);

// Tableau pour stocker le résultat fusionné
$merged_array = [];

// Cette boucle parcourt chaque entité dans le tableau $filtered_entities.
// Pour chaque entité, elle extrait l'UUID, le transforme, et vérifie s'il existe une correspondance dans le tableau $entitycompliances.
// Si une correspondance est trouvée, les données sont fusionnées. Sinon, des valeurs par défaut sont utilisées pour compléter les informations manquantes.
foreach ($filtered_entities as $entity) {
    // Extraire l'UUID et le transformer
    $uuid = $entity['uuid'];
    $transformed_uuid = intval(substr($uuid, 4));

    // Trouver l'élément correspondant dans $entitycompliances
    if (isset($entitycompliances[$uuid])) {
        $compliance = $entitycompliances[$uuid];
        // Fusionner les données
        $merged_array[] = array_merge($entity, $compliance);
    } else {
        $missing_entity = array(
            "entity" => $transformed_uuid,
            "nbmachines" => 0,
            "nbupdate" => 0,
            "totalmach" => 0,
            "conformite" => 100
        );
        $merged_array[] = array_merge($entity, $missing_entity);
    }
}
// Cette boucle extraitdepuis $merged_array les information pour creer la OptimizedListInfos Conformité des entités
foreach ($merged_array as $index_tab => $entitycompliance) {
    $actiondetailsByMachs[] = $detailsByMach;
    $actiondetailsByUpds[] = $detailsByUpd;

    $nbupdate[] = $entitycompliance['nbupdate'] ;
    $entityNames[] =$entitycompliance['completename'] ;
    // $conformite[] =$entitycompliance['conformite'] ;
    $complRates[] = (string) new medulla_progressbar_static($entitycompliance['conformite'],
                                                        "",
                                                         sprintf($texte_help ,
                                                                 $entitycompliance['nbupdate'] ,
                                                                 $entitycompliance['nbmachines'],
                                                                 $entitycompliance['name']  ));
    $nbMachines[] =$entitycompliance['nbmachines'] ;
    $totalMachine[] =$entitycompliance['totalmach'] ;
    $ids_entity[] = str_replace(" ", "-", "id".$entitycompliance['entity']."-".$entitycompliance['name']);
    // action suivant conformite
    if($entitycompliance['conformite'] == 100) {
            $actiondeployAlls[] = $emptyDeployAll;
            $actiondeploySpecifics[] = $emptyDeploySpecific;

        } else {
            $actiondeployAlls[] = $deployAll;
            $actiondeploySpecifics[] = $deploySpecific;
        }

        $actionHistories[] = $actionHistory;
    // pour chaque action on passe les parametres
    $params[] = array(
        'entity' => $entitycompliance['uuid'],// $transformed_uuid, //
        'completename' => $entitycompliance['completename'],
        'source' => $source
    );
}

$n = new OptimizedListInfos($entityNames, _T("Entity name", "updates"));
$n->setcssIds($ids_entity);
$n->disableFirstColumnActionLink();

$n->addExtraInfo($complRates, _T("Compliance rate", "updates"));
// $n->addExtraInfo($nbupdate, _T("Missing updates", "updates"));
$n->addExtraInfo($nbMachines, _T("Non-compliant machines", "updates"));
$n->addExtraInfo($totalMachine, _T("Total machines", "updates"));

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

$n->addActionItemArray($actionHistories);
$n->addActionItemArray($actiondetailsByMachs);
$n->addActionItemArray($actiondetailsByUpds);
//$n->addActionItemArray($actiondeployAlls);
$n->addActionItemArray($actiondeploySpecifics);
$n->start = 0;
$n->end = $count;
$n->display();
?>
