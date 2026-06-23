<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxEntitiesListlinuxfilter.php
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
 * file:  /updates/updates/ajaxEntitiesListlinuxfilter.php.php
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
// Récupérer les emplacements de l'utilisateur
$_entities = getUserLocations();

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

    function createLinuxGroupPopup(string $question, int $width = 450)
    {
        return new ActionAjaxPopup(
            "CreateGroup",            // Nom de l'action
            "ajaxUpdateCreateGroup",  // Méthode AJAX appelée
            "btnCreateGroup",         // ID bouton
            '',
            _T($question, "updates"), // Question personnalisée
            "updates",                // Module
            "updates",                // Sous-module
            null,                     // Onglet
            $width,                   // Largeur popup
            false,                    // Mode modal
            true                      // Remplacer popup par résultat AJAX
        );
    }

function question_custom_colonne($colonne, $nameentitycomplete){
    switch ($colonne) {

    case "total_machines":
        $question = "Do you want to create a group containing<br> all Linux machines of entity {$nameentitycomplete}?";
        $largeur=500;
        break;

    case "machines_not_up_to_date":
        $question = "Do you want to create a group of Linux machines with pending updates<br> for entity {$nameentitycomplete}?";
        $largeur=500;
        break;

    case "machines_security_not_ok":
        $question = "Do you want to create a group of Linux machines missing security updates<br> for entity {$nameentitycomplete}?";
        $largeur=500;
        break;

    case "machines_kernel_not_ok":
        $question = "Do you want to create a group of Linux machines with outdated kernels<br> for entity {$nameentitycomplete}?";
        $largeur=500;
        break;

    case "machines_other_not_ok":
        $question = "Do you want to create a group of Linux machines with other pending updates<br> for entity {$nameentitycomplete}?";
        $largeur=500;
        break;

    default:
        $question = "Do you want to create this Linux group<br>for entity {$nameentitycomplete}?";
        $largeur=500;
    }
    return array($question, $largeur);
}



// Filtrer les entités en fonction d'un motif de recherche
$filtered_entities = [];

$action_update_kernel_linux=[];
$action_update_other_linux=[];
$action_update_security_linux=[];
$action_update_complet_linux=[];
$vue_compliance_distri_linux_entity=[];
$vue_detail_machine_kernel_linux_entity=[];
$vue_detail_machine_other_linux_entity=[];
$vue_detail_machine_security_linux_entity=[];


// ----------------------------------------------------
// ---------------------- ACTION ----------------------
// ----------------------------------------------------

// ----------------------------------------------------

$action_Update_complete_all_Linux_on_entity = new ActionPopupItem( _T("Update complete all Linux on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_all_linux_entity");

$action_no_Update_complete_all_Linux_on_entity = new EmptyActionItem1(
    _T("Update complete all Linux on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg"
);
// ----------------------------------------------------
$action_update_kernel_all_linux_entity = new ActionPopupItem( _T("Update all Linux kernel on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_kernel_all_linux_entity");

// // Affiche le lien dans un <li> avec la popup titre "Mettre à jour tous les kernels Linux de l'entité" // titre affiché
// $action_update_kernel_all_linux_entity->displayWithRight("", array());

$action_no_update_kernel_all_linux_entity = new EmptyActionItem1(
    _T("Update all Linux kernel on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg"
);


// ----------------------------------------------------

$action_Update_complete_all_Linux_on_entity = new ActionPopupItem( _T("Update complete all Linux on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_kernel_all_linux_entity");

$action_no_Update_complete_all_Linux_on_entity = new EmptyActionItem1(
    _T("Update complete all Linux on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg"
);
// ----------------------------------------------------

$action_update_security_all_linux_entity = new ActionPopupItem(_T("Update all Linux security on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_security_all_linux_entity");


$action_no_update_security_all_linux_entity = new EmptyActionItem1(
    _T("Update all Linux security on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg"
);
// ----------------------------------------------------

$action_update_other_all_linux_entity = new ActionPopupItem(_T("Update all other Linux packages on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_other_all_linux_entity");


$action_no_update_other_all_linux_entity = new EmptyActionItem1(
    _T("Update all other Linux packages on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg"
);
// ----------------------------------------------------
// ----------------------- VIEW -----------------------
// ----------------------------------------------------

$View_compliance_distri_linux_entity = new ActionItem(_T("Distibution Linux on entity",
                                                         "updates"),
                                                        "View_compliance_distri_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");

$NoView_compliance_distri_linux_entity = new EmptyActionItem1(_T("Distibution Linux on entity",
                                                                "updates"),
                                                        "View_compliance_distri_linux_entity",
                            "auditbymachine");
// --------------------

$View_detail_machine_kernel_linux_entity = new ActionItem(_T("Details Machine kernel update",
                                                             "updates"),
                                                        "View_detail_machine_kernel_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");

$NoView_detail_machine_kernel_linux_entity = new EmptyActionItem1(_T("Details Machine kernel update",
                                                                     "updates"),
                                                            "View_detail_machine_kernel_linux_entity",
                                                            "auditbymachine");
//------------------------
$View_detail_machine_other_linux_entity = new ActionItem(_T("Details machines all other Update Linux packages on entity",
                                                            "updates"),
                                                        "View_detail_machine_other_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");

$NoView_detail_machine_other_linux_entity = new EmptyActionItem1(_T("Details machines all other Update Linux packages on entity",
                                                                    "updates"),
                                                        "View_detail_machine_other_linux_entity",
                                                        "auditbymachine");
//--------------------------
$View_detail_machine_security_linux_entity = new ActionItem(_T("Details Machine security update on entity",
                                                               "updates"),
                                                        "View_detail_machine_security_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");
$NoView_detail_machine_security_linux_entity = new EmptyActionItem1(_T("Details Machine security update on entity",
                                                                       "updates"),
                                                        "View_detail_machine_security_linux_entity",
                                                        "auditbymachine");
//--------------------------


foreach ($_entities as $entity) {
    if (preg_match("#" . $filter . "#i", $entity['name']) || preg_match("#" . $filter . "#i", $entity['completename'])) {
        $filtered_entities[] = $entity;
    }
}

// Compter le nombre d'entités filtrées
$count = count($filtered_entities);
if ($count != 0){
// Paginer les entités filtrées pour afficher uniquement un sous-ensemble
$entities = array_slice($filtered_entities, $start, $maxperpage, false);

// Déterminer la source à partir des paramètres GET ou utiliser une valeur par défaut
$source = isset($_GET['source']) ? $_GET['source'] : "xmppmaster";

// Tableau pour stocker le résultat fusionné
$merged_array = [];

// Cette bouc
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

$params = [];

$entityid = array_column($merged_array, 'entity');
$nameentity = array_column($merged_array, 'completename');
$entitycompliances = xmlrpc_analyze_machine_compliance_linux($entityid);

$datestring = date("Ymd_His");

// Vérifier que $entitycompliances est un tableau valide
if (!is_array($entitycompliances) || empty($entitycompliances)) {
    $entitycompliances = [];
}

// Initialize output arrays before the loop to ensure variables are defined
$complRatestotal = [];
$complSecurity = [];
$complkernel = [];
$complother = [];
$total_machines = [];
$machines_not_up_to_date = [];
$machines_up_to_date = [];
$machines_security_not_ok = [];
$machines_kernel_not_ok = [];
$machines_other_not_ok = [];

// Utiliser un compteur séquentiel pour itérer de manière cohérente sur les tableaux parallèles
$entity_count = count($entityid);
for ($counter = 0; $counter < $entity_count; $counter++) {
    $ind = $counter;
    $val = $entityid[$counter];

    // Nom complet de l'entité courante
    $nameentitycomplete = $nameentity[$counter];

    /*
     * Tableau de données transmis lors de la création des groupes dynamiques.
     * Ces informations sont nécessaires pour permettre :
     *  - le filtrage
     *  - la navigation
     *  - la reconstruction du contexte (entité + type Linux)
     */
    $datagrp = [
        "entity_id"                   => $entityid[$ind],
        "completename"                => $nameentitycomplete,
        "compliance_total_percent"    => ($entitycompliances['compliance_total_percent'][$ind] ?? 0),
        "compliance_security_percent" => ($entitycompliances['compliance_security_percent'][$ind] ?? 0),
        "compliance_kernel_percent"   => ($entitycompliances['compliance_kernel_percent'][$ind] ?? 0),
        "compliance_other_percent"    => ($entitycompliances['compliance_other_percent'][$ind] ?? 0),
        "machines_not_up_to_date"     => ($entitycompliances['machines_not_up_to_date'][$ind] ?? 0),
        "machines_up_to_date"         => ($entitycompliances['machines_up_to_date'][$ind] ?? 0),
        "machines_security_not_ok"    => ($entitycompliances['machines_security_not_ok'][$ind] ?? 0),
        "machines_kernel_not_ok"      => ($entitycompliances['machines_kernel_not_ok'][$ind] ?? 0),
        "machines_other_not_ok"       => ($entitycompliances['machines_other_not_ok'][$ind] ?? 0),
        "total_machines"              => ($entitycompliances['total_machines'][$ind] ?? 0)
    ];
    $params[]=$datagrp;
    /*
     |--------------------------------------------------------------------------
     | PROGRESS BARS - Messages explicatifs Linux
     |--------------------------------------------------------------------------
     */

    $complRatestotal[] = (string) new medulla_progressbar_static(
        ($entitycompliances['compliance_total_percent'][$ind] ?? 0),
        "",
        "Overall Linux compliance rate for entity {$nameentitycomplete}.\nPercentage of machines fully up to date."
    );

    $complSecurity[] = (string) new medulla_progressbar_static(
        ($entitycompliances['compliance_security_percent'][$ind] ?? 0),
        "",
        "Linux security update compliance for entity {$nameentitycomplete}.\nMachines without pending security patches."
    );

    $complkernel[] = (string) new medulla_progressbar_static(
        ($entitycompliances['compliance_kernel_percent'][$ind] ?? 0),
        "",
        "Linux kernel compliance for entity {$nameentitycomplete}.\nMachines running an up-to-date kernel version."
    );

    $complother[] = (string) new medulla_progressbar_static(
        ($entitycompliances['compliance_other_percent'][$ind] ?? 0),
        "",
        "Other Linux updates compliance for entity {$nameentitycomplete}.\nCovers non-security and non-kernel packages."
    );

    /*
     |--------------------------------------------------------------------------
     | TOTAL MACHINES LINUX
     |--------------------------------------------------------------------------
     | Représente le nombre total de machines Linux rattachées à l'entité.
     */

    if (intval(($entitycompliances['total_machines'][$ind] ?? 0)) > 0) {

        $msgtitle = _T(
            "Total number of Linux machines registered under entity {$nameentitycomplete}.\n"
            . "Click to view detailed list of machines.",
            "updates"
        );
        // les Params ['entity_id', 'typeaction', 'grp', 'namegrp'] sont required  pour la creation d'un groupe
        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "Total_linux_entity",        // Identifiant technique du groupe
                "namegrp"    => "Linux_machines_{$datestring}", // Nom fonctionnel du groupe
                "colonne"    => "total_machines",            // Colonne concernée
                "typeaction" => "print_r"                      // Contexte Linux
            ]
        );
        $question_largeur = question_custom_colonne("total_machines", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $total_machines[] = $grp->render(
            ($entitycompliances['total_machines'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {

        $total_machines[] = ($entitycompliances['total_machines'][$ind] ?? 0);
    }
    /*
     |--------------------------------------------------------------------------
     | MACHINES NOT UP TO DATE (toutes mises à jour)
     |--------------------------------------------------------------------------
     */

    if (intval(($entitycompliances['machines_not_up_to_date'][$ind] ?? 0)) > 0) {
        $vue_compliance_distri_linux_entity[]= new ActionItem(_T("Distibution Linux on entity $nameentitycomplete",
                                                         "updates"),
                                                        "View_compliance_distri_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");
        $action_update_complet_linux[]=new ActionPopupItem( _T("Update complete all Linux on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_all_linux_entity");

        $msgtitle = _T(
            "Linux machines in entity {$nameentitycomplete} that have pending updates.\n"
            . "These systems are not fully compliant.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_not_up_to_date_linux",
                "namegrp"    => "linux_not_up_to_date_{$datestring}",
                "colonne"    => "machines_not_up_to_date",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_not_up_to_date", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $machines_not_up_to_date[] = $grp->render(
            ($entitycompliances['machines_not_up_to_date'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $vue_compliance_distri_linux_entity[]= new EmptyActionItem1(_T("Distibution Linux on entity $nameentitycomplete",
                                                                "updates"),
                                                                    "View_compliance_distri_linux_entity",
                                                                    "auditbymachine");
        $machines_not_up_to_date[] = ($entitycompliances['machines_not_up_to_date'][$ind] ?? 0);
        $action_update_complet_linux[]=new EmptyActionItem1(
                                                            _T("Update complete all Linux on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg"
                                                        );
    }
    /*
     |--------------------------------------------------------------------------
     | MACHINES UP TO DATE
     |--------------------------------------------------------------------------
     */

    if (intval(($entitycompliances['machines_up_to_date'][$ind] ?? 0)) > 0) {

        $msgtitle = _T(
            "Linux machines in entity {$nameentitycomplete} that are fully up to date.\n"
            . "No pending updates detected.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_up_to_date_linux",
                "namegrp"    => "linux_up_to_date_{$datestring}",
                "colonne"    => "machines_up_to_date",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_up_to_date", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_up_to_date[] = $grp->render(
            ($entitycompliances['machines_up_to_date'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $machines_up_to_date[] = ($entitycompliances['machines_up_to_date'][$ind] ?? 0);
    }
    /*
     |--------------------------------------------------------------------------
     | SECURITY NOT OK
     |--------------------------------------------------------------------------
     */

    if (intval(($entitycompliances['machines_security_not_ok'][$ind] ?? 0)) > 0) {
        $action_update_security_linux[]= new ActionPopupItem(_T("Update all Linux security on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_security_all_linux_entity");
        $vue_detail_machine_security_linux_entity[]=new ActionItem(_T("Details Machine security update on entity $nameentitycomplete",
                                                               "updates"),
                                                        "View_detail_machine_security_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");;
        $msgtitle = _T(
            "Linux machines in entity {$nameentitycomplete} missing security updates.\n"
            . "These systems may be exposed to vulnerabilities.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_security_not_ok_linux",
                "namegrp"    => "linux_security_issues_{$datestring}",
                "colonne"    => "machines_security_not_ok",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_security_not_ok", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_security_not_ok[] = $grp->render(
            ($entitycompliances['machines_security_not_ok'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {

        $action_update_security_linux[]= new EmptyActionItem1( _T("Update all Linux security on entity $nameentitycomplete", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateoneg"
                                                            );
        $machines_security_not_ok[] = ($entitycompliances['machines_security_not_ok'][$ind] ?? 0);
        $vue_detail_machine_security_linux_entity[]=new EmptyActionItem1(_T("Details Machine security update on entity $nameentitycomplete",
                                                                       "updates"),
                                                        "View_detail_machine_security_linux_entity",
                                                        "auditbymachine");
    }


    /*
     |--------------------------------------------------------------------------
     | KERNEL NOT OK
     |--------------------------------------------------------------------------
     */

    if (intval(($entitycompliances['machines_kernel_not_ok'][$ind] ?? 0)) > 0) {
        $vue_detail_machine_kernel_linux_entity[]=new ActionItem(_T("Details Machine update on entity $nameentitycomplete",
                                                             "updates"),
                                                        "View_detail_machine_kernel_linux_entity",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");
        $action_update_kernel_linux[]= new ActionPopupItem( _T("Update all Linux kernel on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_kernel_all_linux_entity");
        $msgtitle = _T(
            "Linux machines in entity {$nameentitycomplete} running an outdated kernel version.\n"
            . "Kernel update recommended.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_kernel_not_ok_linux",
                "namegrp"    => "linux_kernel_issues_{$datestring}",
                "colonne"    => "machines_kernel_not_ok",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_kernel_not_ok", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_kernel_not_ok[] = $grp->render(
            ($entitycompliances['machines_kernel_not_ok'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $action_update_kernel_linux[]=new EmptyActionItem1(
                                                            _T("Update all Linux kernel on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg"
                                                        );
        $vue_detail_machine_kernel_linux_entity[]=new EmptyActionItem1(_T("Details Machine kernel update $nameentitycomplete",
                                                                     "updates"),
                                                            "View_detail_machine_kernel_linux_entity",
                                                            "auditbymachine");
        $machines_kernel_not_ok[] = ($entitycompliances['machines_kernel_not_ok'][$ind] ?? 0);
    }


    /*
     |--------------------------------------------------------------------------
     | OTHER PACKAGES NOT OK
     |--------------------------------------------------------------------------
     */


    if (intval(($entitycompliances['machines_other_not_ok'][$ind] ?? 0)) > 0) {

        $vue_detail_machine_other_linux_entity[]=new ActionItem(_T("Details machines all other Update Linux packages on entity",
                                                            "updates"),
                                                        "View_detail_machine_other_linux_entity $nameentitycomplete",
                                                        "auditbymachine",
                                                        "",
                                                        "updates",
                                                        "updates");
        $action_update_other_linux[]= new ActionPopupItem(_T("Update all other Linux packages on entity $nameentitycomplete", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_other_all_linux_entity");

        $msgtitle = _T(
            "Linux machines in entity {$nameentitycomplete} with other pending package updates.\n"
            . "Includes non-security and non-kernel packages.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_other_not_ok_linux",
                "namegrp"    => "linux_other_updates_{$datestring}",
                "colonne"    => "machines_other_not_ok",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_other_not_ok", $nameentitycomplete);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_other_not_ok[] = $grp->render(
            ($entitycompliances['machines_other_not_ok'][$ind] ?? 0),
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $action_update_other_linux[]= new EmptyActionItem1(
                                        _T("Update all other Linux packages on entity $nameentitycomplete", "updates"),
                                        "deployUpdateLinuxType",
                                        "updateoneg"
                                    );
        $vue_detail_machine_other_linux_entity[]= new EmptyActionItem1(_T("Details machines all other Update Linux packages on entity $nameentitycomplete",
                                                                    "updates"),
                                                        "View_detail_machine_other_linux_entity",
                                                        "auditbymachine");
        $machines_other_not_ok[] = ($entitycompliances['machines_other_not_ok'][$ind] ?? 0);
    }
}//end for

// params is $datagrp
$n = new OptimizedListInfos($nameentity, _T("Entity name", "updates"));
$n->setcssIds($nameentity); // id name pour selection permet des selection css
$n->disableFirstColumnActionLink();
$n->addExtraInfoRaw($total_machines,_T("Total update machines", "updates"));
$n->addExtraInfo($complRatestotal, _T("compliance total", "updates"));
$n->addExtraInfo($complSecurity,_T("compliance security", "updates"));
$n->addExtraInfo($complkernel,_T("compliance kernel", "updates"));
$n->addExtraInfo($complother,_T("compliance other", "updates"));
$n->addExtraInfoRaw($machines_not_up_to_date, _T("not_up_to_date", "updates"));
$n->addExtraInfoRaw($machines_up_to_date, _T("up_to_date", "updates"));
$n->addExtraInfoRaw($machines_security_not_ok, _T("security_not_ok", "updates"));
$n->addExtraInfoRaw($machines_kernel_not_ok, _T("kernel_not_ok", "updates"));
$n->addExtraInfoRaw($machines_other_not_ok, _T("other_not_ok", "updates"));

$n->addActionItemArray($action_update_kernel_linux);
$n->addActionItemArray($action_update_security_linux);
$n->addActionItemArray($action_update_other_linux);
$n->addActionItemArray($action_update_complet_linux);

$n->addActionItemArray($vue_compliance_distri_linux_entity);
$n->addActionItemArray($vue_detail_machine_kernel_linux_entity);
// $n->addActionItemArray($vue_detail_machine_other_linux_entity);
// $n->addActionItemArray($vue_detail_machine_security_linux_entity);

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));

$n->setParamInfo($params);
$n->start = 0;
$n->end = $count;
echo '<div class="entity-compliance-table">';
$n->display();
echo '</div>';
/*
echo "<pre>";
print_r($entitycompliances);
echo "</pre>";*/
}else
{
echo '
<div style="padding:12px; margin:15px 0; border:1px solid #ffeeba;
background-color:#fff3cd; color:#856404; border-radius:5px;
font-weight:bold;">
⚠️ '. _T("No entity name matches your search.", "updates").'
</div>';
};
?>
