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
 * file: ajaxMajorEntitiesList.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);
// error_reporting(E_ALL);
global $conf;

?>

<style>
/*
 * effet survol des donner de creation de groupes
*/
.csszoomHover {
    display: inline-block; /* important pour transform */
    transition: transform 0.15s ease, color 0.15s ease;
}

.csszoomHover:hover {
    transform: translateY(-3px) scale(1.06);
    color: #0a58ca; /* facultatif */
}
</style>

<?php

$maxperpage = $conf["global"]["maxperpage"];
$filter = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$safeFilter = preg_quote($filter, '#');

$_entities = getUserLocations();

// Filtrer les entités en fonction d'un motif de recherche
$filtered_entities = [];
// Construit la liste des entités à afficher selon le filtre saisi.
foreach ($_entities as $entity) {
    if (preg_match("#" . $safeFilter . "#i", $entity['name']) || preg_match("#" . $safeFilter . "#i", $entity['completename'])) {
        $filtered_entities[] = $entity;
    }
}

// Compter le nombre d'entités filtrées
$count = count($filtered_entities);

// Paginer les entités filtrées pour afficher uniquement un sous-ensemble
$entities = array_slice($filtered_entities, $start, $maxperpage, false);

// Déterminer la source à partir des paramètres GET ou utiliser une valeur par défaut
$source = isset($_GET['source']) ? $_GET['source'] : "xmppmaster";

// Initialisation de sécurité pour éviter les accès sur variable non définie
$statglpiversion = array('entity' => array());

if ($source == "xmppmaster" || $source == "glpi") {

    $statglpiversion = xmlrpc_get_os_update_major_stats_win();

// Valeurs par défaut
$defaultValues = [
    'count' => 0,
    'name' => '',
    'W10to10' => 0,
    'W10to11' => 0,
    'W11to11' => 0,
    'non_conforme' => 0,
    'autre_cas' => 0,
    'conformite' => 100,
    'UPDATED' => 0,
    'entity_id' => 0,
    'non_inventorie' => 0
];

$mergedArray = [];

// Cette boucle prépare les données par entité pour l'affichage:
// - récupère le nom et l'ID de l'entité locale
// - récupère les statistiques XML-RPC si elles existent
// - applique des valeurs par défaut sinon
// - fusionne le tout dans un format unique consommé plus bas
foreach ($entities as $entity) {
    $name = $entity['name'];
    $completeName = isset($entity['completename']) ? $entity['completename'] : $name;
    $uuid = intval(substr($entity['uuid'], 4));

    // Les stats XML-RPC peuvent être indexées soit par completename (ex: "Medulla > dede"),
    // soit par name simple selon la source.
    if (is_array($statglpiversion) && isset($statglpiversion['entity']) && isset($statglpiversion['entity'][$completeName])) {
        $additionalInfo = $statglpiversion['entity'][$completeName];
    } elseif (is_array($statglpiversion) && isset($statglpiversion['entity']) && isset($statglpiversion['entity'][$name])) {
        $additionalInfo = $statglpiversion['entity'][$name];
    } else {
        // Si aucune stat n'est retournée, on garde une ligne cohérente avec des zéros.
        $defaultValues['name'] = $name;
        $defaultValues['entity_id'] = $uuid;
        $additionalInfo = $defaultValues;
    }

    // Fusion
    $merged = array_merge($entity, $additionalInfo);

    // Sécuriser entity_id dans tous les cas
    if (!isset($merged['entity_id'])) {
        $merged['entity_id'] = $uuid;
    }

    $mergedArray[] = $merged;
}

$params = array();
$actiondetailsByMachs = array();
$actionupdateByentity = array();
$actionHardwareConstraintsForMajorUpdatesByEntity = array();
$complete_name_major = array();
$comformite_name_major = array();
$win10towin10_major = array();
$win10towin11_major = array();
$win11towin11_major = array();
$total_win = array();
$updated_major = array();
$missing_information_major = array();
// definition des actions
$detailsByMach = new ActionItem(_T("Details by machines", "updates"),
                                "majorDetailsByMachines",
                                "auditbymachine",
                                "",
                                "updates",
                                "updates");

$emptydetailsByMach = new EmptyActionItem1(_T("no major updates for this entity", "updates"),
                                            "majorDetailsByMachines",
                                            "auditbymachine",
                                            "",
                                            "updates",
                                            "updates");

// Please do not perform the update for now, as long as certain essential hardware constraints are not met.
// Veuillez ne pas effectuer la mise à jour pour le moment, tant que certaines contraintes matérielles essentielles ne sont pas respectées.



$details_hardware_constraints_for_major_updates = new ActionItem(_T("Please do not perform the update for now, as long as certain essential hardware constraints are not met.", "updates"),
                                "hardwareConstraintsForMajorUpdates",
                                "donotupdate",
                                "",
                                "updates",
                                "updates");

// No machines are affected by hardware constraints for major updates.
// Aucune machine n’est concernée par des contraintes matérielles pour les mises à jour majeures.
$empty_hardware_constraints_for_major_updates = new EmptyActionItem1(_T("No machines are affected by hardware constraints for major updates.", "updates"),
                                            "hardwareConstraintsForMajorUpdates",
                                            "donotupdate",
                                            "",
                                            "updates",
                                            "updates");

$deployAll = new ActionPopupItem(_T("Deploy all major updates on entity", "updates"),
                                    "grpDeployUpdatemajor",
                                    "updateall",
                                    "",
                                    "updates",
                                    "updates",
                                    null,
                                    640,"machine");

$emptydeployAll = new EmptyActionItem1(_T("There are no major updates to deploy for the entity.", "updates"),
                                            "grpDeployUpdatemajor",
                                            "updateall",
                                            "",
                                            "updates",
                                            "updates");

    $grp = new ActionAjaxPopup(
        "CreateGroup",
        "ajaxUpdateCreateGroup", // action
        "btnCreateGroup",
        '',
        _T("Voulez-vous créer le groupe ?", "updates"),
        "updates",    // module
        "updates" ,    // submod
        null, // tab
        700, // largeur
        false, // mod
        true // remplace le popup avec le result de ajax
    );

    // Générer la chaîne de date et heure
    $datestring = date("Ymd_His");
    $texte_help = _T("%s machines in the entity \"%s\" can benefit from a major update.", "updates");

// Machine with Windows 10 22H2 installed at 2025-11-04 09:07:17
// Construit toutes les colonnes de la table et les actions associées pour chaque entité.
foreach ($mergedArray as $datacolonne) {
    // Remplacer les espaces par des underscores

    // Nb de machines candidates à une mise à niveau majeure (hors machines déjà à jour)
    $nbupdate = $datacolonne['W10to10'] + $datacolonne['W10to11'] + $datacolonne['W11to11'];
    if ($datacolonne['count'] > 0) {
        $actiondetailsByMachs[] = $detailsByMach;
    } else {
        $actiondetailsByMachs[] = $emptydetailsByMach;
    }

    if ($nbupdate > 0) {
        $actionupdateByentity[] = $deployAll;
    } else {
        $actionupdateByentity[] = $emptydeployAll;
    }

    // on initialise le tableau
    $complete_name_major[] = $datacolonne['name'];
    // $win10towin10_major[]=$datacolonne['W10to10'];
    // $win10towin11_major[]=$datacolonne['W10to11'];
    // $updated_major[]=$datacolonne['UPDATED'];

    // Nb de machines non conformes matériellement pour la montée de version
    $nb_machine_manque_info = intval($datacolonne['non_conforme']);

    if (intval($nb_machine_manque_info) > 0) {
        $msgtitle = _T("These machines do not meet the hardware requirements for upgrading to a newer Windows release.", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne, ['grp' => 'hardware_requirements',
                                            "namegrp" => "Machine with Win10 hardware requirements for win11_".$datestring,
                                            "colonne" => "norequired",
                                            "typeaction" => "windows"
                                           ]);
        // $namegrp = $Entitynamegrp."_hardware_requirements";
        $missing_information_major[] = $grp->render($nb_machine_manque_info, $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $missing_information_major[] = $nb_machine_manque_info;
    }

    if (intval($datacolonne['W11to11']) > 0) {
        $msgtitle = _T("These machines need a Windows 11 update", "updates");
        // Construire $namegrp
           $tabcgi = array_merge($datacolonne, ['grp' => 'W11to11',
                                            "namegrp" => "Machine with Win11 to Win11 last version".$datestring ,
                                            "colonne" => "W11to11",
                                            "typeaction" => "windows"]);
        $win11towin11_major[] = $grp->render($datacolonne['W11to11'], $tabcgi, $msgtitle, "csszoomHover");
        } else {
            $win11towin11_major[] = $datacolonne['W11to11'];
    }

    if (intval($datacolonne['W10to10']) > 0) {
        $msgtitle = _T("These machines need a Windows 10 update", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne,['grp' => 'W10to10',
                                            "namegrp" => "Machine for install Win10 22H2".$datestring ,
                                            "colonne" => "W10to10",
                                            "typeaction" => "windows"]);
        $win10towin10_major[] = $grp->render($datacolonne['W10to10'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $win10towin10_major[] = $datacolonne['W10to10'];
    }

    if (intval($datacolonne['W10to11']) > 0) {
        $msgtitle = _T("These machines need a Windows 10 to Windows 11 update", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne, ['grp' => 'W10to11',
                                             "namegrp" => "Machine for install Win11".$datestring ,
                                             "colonne" => "W10to11",
                                             "typeaction" => "windows"]);
        $win10towin11_major[] = $grp->render($datacolonne['W10to11'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $win10towin11_major[] = $datacolonne['W10to11'];
    }

    if (intval($datacolonne['UPDATED']) > 0) {
        $msgtitle = _T("These machines are up to date", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne, ['grp' => 'UPDATED',
                                             "namegrp" => "Machine updated".$datestring,
                                             "colonne" => "UPDATED",
                                             "typeaction" => "windows"]);
        $updated_major[] = $grp->render($datacolonne['UPDATED'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $updated_major[] = $datacolonne['UPDATED'];
    }

    // Total machines par entité: valeur officielle renvoyée par l'API
    $total_win[] = intval($datacolonne['count']);

    // Add hardware constraint details only if some machines are missing information
    $actionHardwareConstraintsForMajorUpdatesByEntity[] = ($nb_machine_manque_info > 0)
    ? $details_hardware_constraints_for_major_updates  // Some machines are missing info
    : $empty_hardware_constraints_for_major_updates;   // All machines are compliant

    $formattedText_help = sprintf($texte_help, $nbupdate, $datacolonne['name']);
    $comformite_name_major[] = (string) new medulla_progressbar_static($datacolonne['conformite'],
                                                                        "",
                                                                        $formattedText_help);
    // Paramètres réutilisés par les popups/actions déclenchés depuis la ligne
    $params[] = array(
        'entity' => $datacolonne['entity_id'],
        'name' => $datacolonne['name'],
        'completename' => $datacolonne['completename'],
        'source' => $source,
        'W10to10' => $datacolonne['W10to10'],
        'W10to11' => $datacolonne['W10to11'],
        'W11to11' => $datacolonne['W11to11'],
        'UPDATED' => $datacolonne['UPDATED'],
        "nb_missing" => $nb_machine_manque_info,
        "totalmachineentity" => $datacolonne['count'],
        "typeaction" => "windows"
    );
}

// $count garde sa valeur initiale (total des entités filtrées, calculé ligne 69),
// pour que la navbar puisse calculer correctement les pages.
$n = new OptimizedListInfos($complete_name_major, _T("Entity name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($comformite_name_major, _T("Compliance rate", "updates"));
$n->addExtraInfoRaw($win10towin10_major, _T("Upgrade to latest Win 10", "updates"));
$n->addExtraInfoRaw($win10towin11_major, _T("Upgrade Win 10 to latest Win 11", "updates"));
$n->addExtraInfoRaw($win11towin11_major, _T("Upgrade to latest Win 11", "updates"));

$n->addExtraInfoRaw($updated_major, _T("Up to date", "updates"));
// $n->addExtraInfo($missing_information_major, _T("Upgrade Not recommended", "updates"));
$n->addExtraInfoRaw($missing_information_major, _T("Upgrade Not recommended", "updates"));
$n->addExtraInfoRaw($total_win, _T("Total machines", "updates"));

$n->addActionItemArray($actionupdateByentity);
$n->addActionItemArray($actiondetailsByMachs);
$n->addActionItemArray($actionHardwareConstraintsForMajorUpdatesByEntity);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
// arrInfo contient déjà le slice paginé : on itère depuis l'index 0,
// $count reste le total global utilisé par la navbar.
$n->start = 0;
$n->end = $count;

$n->setEmptyState(_T("No entities found", "updates"), _T("No entities match the current filter.", "updates"));
echo '<div class="major-entities-metrics">';
$n->display();
echo '</div>';
}else{
    echo "object inexistant";
}

?>
