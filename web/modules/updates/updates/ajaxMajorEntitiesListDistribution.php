<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorEntitiesListDistribution.php
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
 * file: ajaxMajorEntitiesListUbuntu.php
 */


/**
 * ------------------------------------------------------------------
 * INCLUDES XML-RPC
 * ------------------------------------------------------------------
 * Chargement des APIs nécessaires pour :
 *  - updates      : gestion des mises à jour
 *  - glpi         : entités / inventaire
 *  - xmppmaster   : remontées machines
 */

// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);
// error_reporting(E_ALL);
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;
$maxperpage   = $conf["global"]["maxperpage"];

?>

<style>
/**
 * ------------------------------------------------------------------
 * EFFET VISUEL : SURVOL DES DONNÉES DE CRÉATION DE GROUPES
 * ------------------------------------------------------------------
 * Effet léger de zoom + déplacement vertical pour indiquer
 * une action cliquable (UX).
 */
.csszoomHover {
    display: inline-block; /* nécessaire pour transform */
    transition: transform 0.15s ease, color 0.15s ease;
}

.csszoomHover:hover {
    transform: translateY(-3px) scale(1.06);
    color: #0a58ca;
}
</style>

<?php
/**
 * ------------------------------------------------------------------
 * PARAMÈTRES GÉNÉRAUX
 * ------------------------------------------------------------------
 */
/*
 * $distribution et $distributionLabel sont definis par le fichier appelant
 * (ajaxMajorEntitiesList<Distro>.php). Ce fichier porte le code commun aux
 * onglets de distributions : ils etaient auparavant dix copies de 578 lignes
 * ne differant que par ces deux valeurs.
 */
if (!isset($distribution) || $distribution === "") {
    echo "<p>" . _T("No distribution specified.", "updates") . "</p>";
    return;
}
$distributionLabel = isset($distributionLabel) && $distributionLabel !== ""
    ? $distributionLabel
    : ucfirst($distribution);

/**
 * Paramètres de pagination et de filtrage
 */
$filter = isset($_GET['filter']) ? $_GET['filter'] : "";
$hostnameFilter = isset($_GET['hostname_filter']) ? trim((string) $_GET['hostname_filter']) : "";
$start  = isset($_GET['start'])  ? (int) $_GET['start'] : 0;
$end    = $start + $maxperpage;
$source = isset($_GET['source']) ? $_GET['source'] : "";

/**
 * ------------------------------------------------------------------
 * RÉCUPÉRATION DES ENTITÉS UTILISATEUR
 * ------------------------------------------------------------------
 */
$_entities = getUserLocations();

$listentity       = []; // Liste des IDs d'entités
$listcompletename = []; // Mapping entity_id => nom complet
$filtered_entities = [];

/**
 * Filtrage des entités par nom ou nom complet
 */
foreach ($_entities as $entity) {

    if (
        preg_match("#" . $filter . "#i", $entity['name']) ||
        preg_match("#" . $filter . "#i", $entity['completename'])
    ) {
        $filtered_entities[] = $entity;
    }

    // Conversion UUID -> ID numérique
    $entityId = (int) preg_replace('/^UUID/', '', $entity['uuid']);

    $listentity[] = $entityId;
    $listcompletename[$entityId] = $entity['completename'];
}

/**
 * Pagination des entités filtrées
 */
$entities = array_slice($filtered_entities, $start, $maxperpage, false);

updates_dev_trace("INFO", "Entities loaded", array(
    "distribution" => $distribution,
    "filtered_count" => count($filtered_entities),
    "page_count" => count($entities),
    "entity_ids" => implode(",", array_slice($listentity, 0, 5))
));

/**
 * ------------------------------------------------------------------
 * RÉCUPÉRATION DES STATISTIQUES DE CONFORMITÉ
 * ------------------------------------------------------------------
 */
$statversion = xmlrpc_get_distribution_version_compliance(
    $distribution,
    $listentity,
    $start,
    (int) $maxperpage,
    $hostnameFilter
);
if (!is_array($statversion)) {
    $statversion = [];
}

// Garantit l'affichage de toutes les entités de la page, même si la base
// ne retourne aucune ligne de conformité pour certaines d'entre elles.
$statsByEntityId = [];
foreach (($statversion['by_entity'] ?? []) as $statRow) {
    $rowEntityId = isset($statRow['entity_id']) ? (int) $statRow['entity_id'] : 0;
    if ($rowEntityId >= 0) {
        $statsByEntityId[$rowEntityId] = $statRow;
    }
}

$normalizedByEntity = [];
foreach ($entities as $entity) {
    $entityId = (int) preg_replace('/^UUID/', '', ($entity['uuid'] ?? '0'));
    if ($entityId < 0) {
        continue;
    }

    if (isset($statsByEntityId[$entityId])) {
        $row = $statsByEntityId[$entityId];
        $row['entity_id'] = $entityId;
        $normalizedByEntity[] = $row;
        continue;
    }

    $normalizedByEntity[] = [
        'entity_id' => $entityId,
        'total_machines' => 0,
        'outdated_machines' => 0,
        'up_to_date_machines' => 0,
        'pending_support_update' => 0,
        'compliance_rate' => 0,
    ];
}

$statversion['by_entity'] = $normalizedByEntity;

updates_dev_trace("INFO", "Stats returned from RPC", array(
    "total_outdated" => $statversion['total_outdated'] ?? 'MISSING',
    "by_entity_count" => count($statversion['by_entity'] ?? []),
    "has_by_entity" => isset($statversion['by_entity']) ? 'YES' : 'NO',
    "statversion_keys" => implode(",", array_keys($statversion ?? []))
));

/**
 * Informations de version
 */
$name_version = $statversion['name_version'] ?? "";
$max_version  = $statversion['max_version'] ?? "";

/**
 * Version lisible pour affichage
 */
$versionup = ucwords(strtolower(sprintf(
    "%s %s %s",
    $distribution,
    $max_version,
    $name_version
)));

/*
 * Pas de titre ici : la version cible est deja portee par l'en-tete de colonne
 * "Montee vers <version>", et l'onglet actif indique la distribution. Les
 * onglets Windows et Windows Server n'en affichent pas non plus.
 *
 * Ce bloc instanciait par ailleurs un PageGenerator (generateur de page
 * complete) a l'interieur d'un fragment AJAX, ce qui n'a pas lieu d'etre : la
 * page hote est deja rendue par MajorEntitiesList.php.
 */

/**
 * ------------------------------------------------------------------
 * INITIALISATION DES STRUCTURES DE DONNÉES
 * ------------------------------------------------------------------
 */
$datestring = date("Ymd_Hi");

$title = _T("OS Upgrades", "updates");

/**
 * Texte d’aide affiché au survol (progress bar)
 */
$texte_help = _T(
    "%s machines in the entity \"%s\" can benefit from a major update.",
    "updates"
);

// definition des actions
  // $updateAll= new ActionPopupItem(
  //      "llllllllllllllllllllllllllllllllllllllll",
  //       "deployUpdateLinuxMajor",
  //       "updateone",
  //       '',
  //       "updates",
  //       "updates",
  //       null,
  //       320,
  //       "machine"
  //   );
$updateAll = new ActionPopupItem(_T("Deploy all major updates on entity", "updates"),
                                "grpDeployUpdateLinuxMajor",
                                "updateallg",
                                "",
                                "updates",
                                "updates",
                                null,
                                320,"machine");

$emptyupdateAll = new EmptyActionItem1(_T("There are no major updates to deploy for the entity.", "updates"),
                                        "grpDeployUpdateLinuxMajor",
                                        "updateallg",
                                        "",
                                        "updates",
                                        "updates");

$detailsByMach = new ActionItem(_T("List of machines to be upgraded", "updates"),
                                "majorDetailsByMachinesLinux",
                                "auditbymachine",
                                "",
                                "updates",
                                "updates");

$emptydetailsByMach = new EmptyActionItem1(_T("No major updates for this entity", "updates"),
                                            "majorDetailsByMachinesLinux",
                                            "auditbymachine",
                                            "",
                                            "updates",
                                            "updates");



/**
 * Tableaux de résultats par catégorie
 */
$outdated_machines          = [];
$up_to_date_machines        = [];
$pending_support_update     = [];
$total_machines             = [];

$list_compliance_rate       = [];
$list_name_entity           = [];
$comformite_name_major      = [];
$display_entities           = [];
$actionupdateByentity       = [];
$actiondetailsByMachs       = [];
$actionDeploymentHistory    = [];

$deploymentHistory = new ActionItem(_T("Deployment history", "updates"),
                                    "majorDeploymentHistoryLinux",
                                    "history",
                                    "",
                                    "updates",
                                    "updates");

$emptyDeploymentHistory = new EmptyActionItem1(_T("No Linux major deployment history for this entity", "updates"),
                                                "majorDeploymentHistoryLinux",
                                                "historyg",
                                                "",
                                                "updates",
                                                "updates");

// parametre des action
$params =  array();
foreach ($statversion['by_entity'] as $entityId => $ent) {
    if ( $ent['outdated_machines'] > 0){
        $actionupdateByentity[] = $updateAll;
        $actiondetailsByMachs[] = $detailsByMach;
    }else{
        $actionupdateByentity[] = $emptyupdateAll;
        $actiondetailsByMachs[] = $emptydetailsByMach;
    }


    $currentEntityId = isset($ent['entity_id']) ? (int) $ent['entity_id'] : -1;
    if ($currentEntityId < 0) {
        $currentEntityId = (int) $entityId;
    }

    if (intval($ent['total_machines']) > 0) {
        $actionDeploymentHistory[] = $deploymentHistory;
    } else {
        $actionDeploymentHistory[] = $emptyDeploymentHistory;
    }

    $entityName = $listcompletename[$currentEntityId] ?? (string) $currentEntityId;
    $display_entities[] = $entityName;

    // Texte d’aide pour la barre de conformité
    $formattedText_help = sprintf(
        $texte_help,
        $ent['outdated_machines'],
        $entityName
    );

    $comformite_name_major[] = (string) new medulla_progressbar_static(
        $ent['compliance_rate'],
        "",
        $formattedText_help
    );

    // Popup générique de création de groupe
    $grp = new ActionAjaxPopup(
        "CreateGroup",
        "ajaxUpdateCreateGroup",
        "btnCreateGroup",
        '',
        _T("Do you want to create the group?", "updates"),
        "updates",
        "updates",
        null,
        450,
        false,
        true
    );

    /*
     * ------------------------------------------------------------------
     * MACHINES OUTDATED
     * ------------------------------------------------------------------
     */
    if (intval($ent['outdated_machines']) > 0) {

        $namegrp = sprintf(
            "%s - %s - [%s] (%s) - %s",
            ucfirst($distribution),
            _T("Outdated machines", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s\n\n%s\n%s",
            $formattedText_help,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "outdated_machines",
            "typeaction" => $distribution
        ]);

        $outdated_machines[] = $grp->render(
            $ent['outdated_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $outdated_machines[] = $ent['outdated_machines'];
    }

    /*
     * ------------------------------------------------------------------
     * MACHINES UP TO DATE
     * ------------------------------------------------------------------
     */
    if (intval($ent['up_to_date_machines'])  > 0) {

        $namegrp = sprintf(
            "%s - %s %s - [%s] (%s)- %s",
            ucfirst($distribution),
            _T("Up to date machines", "updates"),
            $versionup,
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s %s\n\n%s\n%s",
            _T("All machines are up to date with version", "updates"),
            $versionup,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "up_to_date_machines",
            "typeaction" => $distribution
        ]);

        $up_to_date_machines[] = $grp->render(
            $ent['up_to_date_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $up_to_date_machines[] = $ent['up_to_date_machines'];
    }


    /*
     * ------------------------------------------------------------------
     * MACHINES PENDING SUPPORT UPDATE
     * ------------------------------------------------------------------
     */
    if (intval($ent['pending_support_update']) > 0) {

        $namegrp = sprintf(
            "%s - %s - [%s] (%s) - %s",
            ucfirst($distribution),
            _T("Pending Support Update", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s\n\n%s\n%s",
            sprintf(_T("Machines with %s version pending support update", "updates"), $distributionLabel),
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "pending_support_update",
            "typeaction" => $distribution
        ]);

        $pending_support_update[] = $grp->render(
            $ent['pending_support_update'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $pending_support_update[] = $ent['pending_support_update'];
    }

    /*
     * ------------------------------------------------------------------
     * TOTAL MACHINES
     * ------------------------------------------------------------------
     */
    if (intval($ent['total_machines']) > 0) {

        $namegrp = sprintf(
            "%s - %s - [%s] - ()%s)%s",
            ucfirst($distribution),
            _T("All machines", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s %s\n\n%s\n%s",
            sprintf(_T("Total %s machines in entity", "updates"), $distributionLabel),
            $entityName,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "total_machines",
            "typeaction" => $distribution
        ]);

        $total_machines[] = $grp->render(
            $ent['total_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $total_machines[] = $ent['total_machines'];
    }
    // Paramètres transmis aux actions: entity_id=0 est valide pour l'entité racine.
    $ent['entity_id'] = $currentEntityId;
    $ent['entityName'] = $entityName;
    $ent['name'] = $entityName;
    $ent['completename'] = $entityName;
    $ent['distribution'] = $statversion['distribution'];
    $ent['name_version'] = $statversion['name_version'];
    $ent['max_version']  = $statversion['max_version'];
    $params[] = $ent;
}
// Générer la chaîne de date et heure
$display_entities = array_values($display_entities);
$comformite_name_major = array_values($comformite_name_major);
$outdated_machines = array_values($outdated_machines);
$up_to_date_machines = array_values($up_to_date_machines);
$pending_support_update = array_values($pending_support_update);
$total_machines = array_values($total_machines);
$actionupdateByentity = array_values($actionupdateByentity);
$actiondetailsByMachs = array_values($actiondetailsByMachs);
$actionDeploymentHistory = array_values($actionDeploymentHistory);
$params = array_values($params);

$count = count($display_entities);
$n = new OptimizedListInfos($display_entities, _T("Entity name", "updates"));
// Colonnes redimensionnables, comme les autres listes du module.
$n->setResizable();
$n->disableFirstColumnActionLink();
/*
 * Compteurs centres en-tete comprise (addExtraInfoCenteredRaw pose text-center
 * sur le <th> et le <td>), et libelles construits par sprintf : concatener la
 * version ou la distribution au msgid les rendait intraduisibles.
 */
$n->addExtraInfo(
    $comformite_name_major,
    _T("Compliance rate", "updates"),
    "",
    sprintf(_T("Share of %s machines already running the target version.", "updates"), $distributionLabel)
);
$n->addExtraInfoCenteredRaw(
    $outdated_machines,
    sprintf(_T("Upgrade to %s", "updates"), $versionup),
    "",
    sprintf(_T("Machines running a version older than %s.", "updates"), $versionup)
);
$n->addExtraInfoCenteredRaw(
    $up_to_date_machines,
    _T("Up to date", "updates"),
    "",
    sprintf(_T("Machines already running %s.", "updates"), $versionup)
);
$n->addExtraInfoCenteredRaw(
    $pending_support_update,
    _T("Pending Support Update", "updates"),
    "",
    sprintf(_T("Machines running a version newer than %s, not managed yet.", "updates"), $versionup)
);
$n->addExtraInfoCenteredRaw(
    $total_machines,
    _T("Total machines", "updates"),
    "",
    sprintf(_T("Total number of %s machines attached to this entity.", "updates"), $distributionLabel)
);

$n->addActionItemArray($actionupdateByentity);
$n->addActionItemArray($actiondetailsByMachs);
$n->addActionItemArray($actionDeploymentHistory);
// $n->addActionItemArray($actionHardwareConstraintsForMajorUpdatesByEntity);
$n->setTableHeaderPadding(12);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
$n->start = $start;
$n->end = $count;

echo '<div class="major-entities-metrics">';
$n->display();
echo '</div>';

?>
