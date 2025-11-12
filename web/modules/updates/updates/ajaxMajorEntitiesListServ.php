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
 *
 * file modules/updates/updates/ajaxMajorEntitiesList.php
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
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$source  = (isset($_GET['$source']) ? $_GET['$source']: "");

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

if ($_GET['source'] == "xmppmaster" || $_GET['source'] == "glpi" ){

    if ($_GET['source'] == "xmppmaster" ){
        $p = new PageGenerator(_T("OS SERVER Upgrades", 'updates'));
        $p->display();
        // $statglpiversion = xmlrpc_get_os_xmpp_update_major_stats();
        $statglpiversion=xmlrpc_get_os_update_major_stats_win_serv();
    }else{
        $p = new PageGenerator(_T("OS SERVER Upgrades", 'updates'));
        $p->display();
        $statglpiversion=xmlrpc_get_os_update_major_stats_win_serv();
    };

// Valeurs par défaut
$defaultValues = [
    'count' => 0,
    'name' => '',
    "MS12toMS25" => 0,
    "MS16toMS25" => 0,
    "MS19toMS25" => 0,
    "MS25toMS25" => 0,
    'non_conforme' => 0,
    'autre_cas' => 0,
    'conformite' => 100,
    'UPDATED' => 0,
    'entity_id' => 0,
    'non_inventorie'=> 0
];

$mergedArray = [];

foreach ($entities as $entity) {
    $name = $entity['name'];
    $uuid = intval(substr($entity['uuid'], 4));

    if (isset($statglpiversion['entity'][$name])) {
        $additionalInfo = $statglpiversion['entity'][$name];
    } else {
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

$params =  array();
$actiondetailsByMachs  = array();
$actionupdateByentity  = array();
$actionHardwareConstraintsForMajorUpdatesByEntity  = array();
$complete_name_major  = array();
$comformite_name_major  = array();
$MS12toMS25_major = array();
$MS16toMS25_major = array();
$MS19toMS25_major = array();
$MS25toMS25_major = array();
$total_win=array();
$complRates=array();
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
                                    320,"machine");

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
        _T("Do you want to create the group ?", "updates"),
        "updates",    // module
        "updates" ,    // submod
        null, // tab
        450, // largeur
        false, // mod
        true // remplace le popup avec le result de ajax
    );

    // Générer la chaîne de date et heure
    $datestring = date("Ymd_His");
    $title = _T("OS Upgrades", "updates");
    $texte_help = _T("%s machines in the entity \"%s\" can benefit from a major update.", "updates");


foreach ($mergedArray as  $index=>$datacolonne) {
    // Remplacer les espaces par des underscores

    $nbupdate = $datacolonne['MS12toMS25'] +
                $datacolonne['MS16toMS25'] +
                $datacolonne['MS19toMS25'] +
                $datacolonne['MS25toMS25'];
    if ($datacolonne['count'] > 0){
        $actiondetailsByMachs[] = $detailsByMach;
    }else{
        $actiondetailsByMachs[] =$emptydetailsByMach;
    }

    if ($nbupdate > 0){
        // echo "k";
        $actionupdateByentity [] = $deployAll;
    }else{
        // echo "j";
        $actionupdateByentity[] = $emptydeployAll;
    }

    // on initialise le tableau
    $complete_name_major[]=$datacolonne['name'];
    // $win10towin10_major[]=$datacolonne['MS12toMS25'];
    // $win10towin11_major[]=$datacolonne['MS16toMS25'];
    // $updated_major[]=$datacolonne['UPDATED'];

    $nb_machine_manque_info=$datacolonne['count'] - ( $datacolonne['MS12toMS25'] +
                                                      $datacolonne['MS16toMS25'] +
                                                      $datacolonne['MS19toMS25'] +
                                                      $datacolonne['MS25toMS25'] +
                                                      $datacolonne['UPDATED']);

    if (intval($nb_machine_manque_info) > 0) {
        echo "hardware_requirements";
        $msgtitle =_T("These machines do not meet the hardware requirements for upgrading to a newer Windows release.", "updates");
        // Construire $namegrp
        $tabcgi= array_merge($datacolonne, ['grp'=> 'hardware_requirements',
                                            "namegrp" => "Server hardware requirements for MSO 25".$datestring,
                                            "colonne" => "hardware_requirements",
                                            "typeaction" => "serverwin"]);
        $missing_information_major[] = $grp->render($nb_machine_manque_info, $tabcgi, $msgtitle, "csszoomHover");
    }else{
        $missing_information_major[]=$nb_machine_manque_info;
    }

    if (intval($datacolonne['MS19toMS25']) > 0) {
        echo "kkkkkkkkkkkkkkkkkkkkkk";
        $msgtitle = _T("These machines need a Windows SERVER 25 update", "updates");
        // Construire $namegrp
        $tabcgi= array_merge($datacolonne, ['grp'=> 'MS19toMS25',
                                            "namegrp" => "Server MSO 19 to release MSO 25".$datestring,
                                            "colonne" => "MS19toMS25",
                                            "typeaction" => "serverwin"]);
        $MS19toMS25_major[] = $grp->render($datacolonne['MS19toMS25'], $tabcgi, $msgtitle, "csszoomHover");
    }else{
         $MS19toMS25_major[]=$datacolonne['MS19toMS25'];
    }

    if (intval($datacolonne['MS12toMS25']) > 0) {
        $msgtitle = _T("These machines need a Windows SERVER 25 update", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne, ['grp' => 'MS12toMS25',
                                             "namegrp" => "Server MSO 12 to release MSO 25".$datestring,
                                             "colonne" => "MS12toMS25",
                                             "typeaction" => "serverwin"]);
        $MS12toMS25_major[] = $grp->render($datacolonne['MS12toMS25'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $MS12toMS25_major[] = $datacolonne['MS12toMS25'];
    }

    if (intval($datacolonne['MS16toMS25']) > 0) {
        $msgtitle = _T("These machines need a Windows SERVER 25 update", "updates");
        $tabcgi = array_merge($datacolonne, ['grp' => 'MS16toMS25',
                                             "namegrp" => "Server MSO 16 to release MSO 25".$datestring,
                                             "colonne" => "MS16toMS25",
                                             "typeaction" => "serverwin"]);
        $MS16toMS25_major[] = $grp->render($datacolonne['MS16toMS25'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $MS16toMS25_major[] = $datacolonne['MS16toMS25'];
    }


    if (intval($datacolonne['MS25toMS25']) > 0) {
        $msgtitle = _T("These machines need a Windows SERVER 25 24H2 update", "updates");
            $tabcgi = array_merge($datacolonne, ['grp' => 'MS25toMS25',
                                                 "namegrp" => "Server MSO 15 to last release MSO 25".$datestring,
                                                 "colonne" => "MS25toMS25",
                                                 "typeaction" => "serverwin"]);
        $MS25toMS25_major[] = $grp->render($datacolonne['MS25toMS25'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $MS25toMS25_major[] = $datacolonne['MS25toMS25'];
    }

    if (intval($datacolonne['UPDATED']) > 0) {
        $msgtitle = _T("These machines are up to date", "updates");
        // Construire $namegrp
        $tabcgi = array_merge($datacolonne, ['grp' => 'UPDATED',
                                             "namegrp" => "Server MSO 25 updated to last release MSO 25".$datestring,
                                             "colonne" => "UPDATED",
                                             "typeaction" => "serverwin"]);
        $updated_major[] = $grp->render($datacolonne['UPDATED'], $tabcgi, $msgtitle, "csszoomHover");
    } else {
        $updated_major[] = $datacolonne['UPDATED'];
    }

    $total_win[]=$datacolonne['count'];

    // Add hardware constraint details only if some machines are missing information
    $actionHardwareConstraintsForMajorUpdatesByEntity[] = ($nb_machine_manque_info > 0)
    ? $details_hardware_constraints_for_major_updates  // Some machines are missing info
    : $empty_hardware_constraints_for_major_updates;   // All machines are compliant

    $formattedText_help = sprintf($texte_help, $nbupdate, $datacolonne['name']);
    $comformite_name_major[]=(string) new medulla_progressbar_static($datacolonne['conformite'],
                                                                     "",
                                                                     $formattedText_help);
    // pour chaque action on passe les parametres
    $params[] = array(
        'entity' => $datacolonne['entity_id'],
        'name' => $datacolonne['name'],
        'completename' => $datacolonne['completename'],
        'source' => $source,
        'MS12toMS25' => $datacolonne['MS12toMS25'],
        'MS16toMS25'=> $datacolonne['MS16toMS25'],
        'MS19toMS25' => $datacolonne['MS19toMS25'],
        'MS25toMS25' => $datacolonne['MS25toMS25'],
        'UPDATED' => $datacolonne['UPDATED'],
        "nb_missing" => $nb_machine_manque_info,
        "totalmachineentity" => $datacolonne['count'],
        "typeaction" => "serverwin"
    );
}
$count = count($complete_name_major);
$n = new OptimizedListInfos($complete_name_major, _T("Entity name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($comformite_name_major, _T("Compliance rate", "updates"));
$n->addExtraInfoRaw($MS12toMS25_major, _T("Upg WS2012→2025", "updates"));
$n->addExtraInfoRaw($MS16toMS25_major, _T("Upg WS2016→2025", "updates"));
$n->addExtraInfoRaw($MS19toMS25_major, _T("Upg WS2019→2025", "updates"));
$n->addExtraInfoRaw($MS25toMS25_major, _T("Upg WS2025→24H2", "updates"));

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
$n->start = $start;
$n->end = $count;

echo '<div class="major-entities-metrics">';
$n->display();
echo '</div>';

}else{
    echo "object inexistant";
}
?>
