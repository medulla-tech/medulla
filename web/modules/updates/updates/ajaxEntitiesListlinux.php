<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: ajaxEntitiesList.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

global $conf;
// $params = [];
// $actiondetailsByMachs = [];
// $actiondetailsByUpds = [];
// $actiondeployAlls = [];
// $actiondeploySpecifics = [];
// $actionHistories = [];
// $entityNames = [];
// $complRates = [];
// $conformite = [];
// $totalMachine = [];
// $nbupdate = [];
// $ids_entity = []; // id des ligne de la list
// $identity = array();
/*
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

// Tableau pour stocker le résultat fusionné
$merged_array = [];

// Cette boucle parcourt chaque entité dans le tableau $filtered_entities.
// Pour chaque entité, elle extrait l'UUID, le transforme, et vérifie s'il existe une correspondance dans le tableau $entitycompliances.
// Si une correspondance est trouvée, les données sont fusionnées. Sinon, des valeurs par défaut sont utilisées pour compléter les informations manquantes.
foreach ($filtered_entities as $entity) {
    // Extraire l'UUID et le transformer
    $uuid = $entity['uuid'];
    $transformed_uuid = intval(substr($uuid, 4));
        $missing_entity = array(
            "name"=>$entity['name'],
            "completename"=>$entity['completename'],
            "entity" => $transformed_uuid
        );
        $merged_array[] = array_merge($entity, $missing_entity);
}
// print_r($merged_array);
$merged_array['tab'] = $_GET['tab'];*/

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxEntitiesListlinuxfilter"), "container", [], 'formRunning');

$ajax->display();
$ajax->displayDivToUpdate();
?>
