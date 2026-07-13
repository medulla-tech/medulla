<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxView_compliance_distri_linux_entity.php


require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");


global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);

$entity_id = isset($_GET['entity_id']) ? intval($_GET['entity_id'], 10) : -1;


// echo $filter;
// Initialisation des variables avec des valeurs par défaut
$completename = ""; // La valeur par défaut est une chaîne vide

// Utiliser filter_var pour convertir la valeur en chaîne de caractères (filtre FILTER_SANITIZE_STRING)
if (isset($_GET['completename'])) {
$completename = filter_var($_GET['completename'], FILTER_SANITIZE_STRING);
}

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

$action_update_kernel_distribution=[];
$action_update_other_distribution=[];
$action_update_security_distribution=[];
$action_update_complet_distribution=[];


$action_update_kernel_linux=[];
$action_update_other_linux=[];
$action_update_security_linux=[];
$action_update_complet_linux=[];


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
    "updateoneg", "", "updates", "updates"
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
    "updateoneg", "", "updates", "updates"
);


// ----------------------------------------------------

$action_Update_complete_all_Linux_on_entity = new ActionPopupItem( _T("Update complete all Linux on entity", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_complete_all_linux_entity");

$action_no_Update_complete_all_Linux_on_entity = new EmptyActionItem1(
    _T("Update complete all Linux on entity", "updates"),
    "deployUpdateLinuxType",
    "updateoneg", "", "updates", "updates"
);
// ----------------------------------------------------
// update security all linux on entity
// $action_update_security_all_linux_entity = new ActionItem(
//     _T("Update all Linux security on entity", "updates"),
//     "action_update_security_all_linux_entity",
//     "updateone", "", "updates", "updates"
// );

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
    "updateoneg", "", "updates", "updates"
);
// ----------------------------------------------------
// update other all linux on entity (other applications & libs)
// $action_update_other_all_linux_entity = new ActionItem(
//     _T("Update all other Linux packages on entity", "updates"),
//     "action_update_other_all_linux_entity",
//     "updateone", "", "updates", "updates"
// );

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
    "updateoneg", "", "updates", "updates"
);




// ----------------------------------------------------



// ----------------------------------------------------

// ----------------------------------------------------

// ----------------------------------------------------


// $action_Update_complete_all_Linux_on_entity = new ActionPopupItem( _T("Update complete all Linux on entity", "updates"),
//                                                             "deployUpdateLinuxType",
//                                                             "updateone", "",
//                                                             "updates",
//                                                             "updates",
//                                                             null,
//                                                             320,
//                                                             "action_update_all_linux_entity");
// $action_Update_complete_all_Linux_on_entity->display($_GET);

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
    function question_custom_colonne($colonne, $nameentitycomplete, $distribution){
        switch ($colonne) {

        case "total_machines":
            $question = "Do you want to create a group containing<br> {$distribution} machines of entity {$nameentitycomplete}?";
            $largeur=500;
            break;

        case "machines_not_up_to_date":
            $question = "Do you want to create a group of {$distribution} machines with pending updates<br> for entity {$nameentitycomplete}?";
            $largeur=500;
            break;

        case "machines_security_not_ok":
            $question = "Do you want to create a group of {$distribution} machines missing security updates<br> for entity {$nameentitycomplete}?";
            $largeur=500;
            break;

        case "machines_kernel_not_ok":
            $question = "Do you want to create a group of {$distribution} machines with outdated kernels<br> for entity {$nameentitycomplete}?";
            $largeur=500;
            break;

        case "machines_other_not_ok":
            $question = "Do you want to create a group of {$distribution} machines with other pending updates<br> for entity {$nameentitycomplete}?";
            $largeur=500;
            break;

        default:
            $question = "Do you want to create this {$distribution} group<br>for entity {$nameentitycomplete}?";
            $largeur=500;
        }
        return array($question, $largeur);
    }


    $compliance_total_percent = 0; // La valeur par défaut est un flottant
    $compliance_security_percent = 0;
    $compliance_kernel_percent = 0;
    $compliance_other_percent = 0;
    // Initialisation des variables avec des valeurs par défaut (zéro)
    $machines_not_up_to_date = 0;
    $machines_up_to_date = 0;
    $machines_security_not_ok = 0;
    $machines_kernel_not_ok = 0;
    $machines_other_not_ok = 0;
    $total_machines = 0;
    $complRatestotal = array();
    $complSecurity = array();
    $complkernel = array();
    $complother = array();

    $vue_detail_machine_security_linux_entity = array();
    // Utiliser filter_var pour convertir la valeur en flottant (filtre FILTER_SANITIZE_NUMBER_FLOAT avec FLAGS FLOAT_FILTER)
    if (isset($_GET['compliance_total_percent'])) {
        $compliance_total_percent = filter_var($_GET['compliance_total_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_security_percent'])) {
        $compliance_security_percent = filter_var($_GET['compliance_security_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_kernel_percent'])) {
        $compliance_kernel_percent = filter_var($_GET['compliance_kernel_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_other_percent'])) {
        $compliance_other_percent = filter_var($_GET['compliance_other_percent'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_not_up_to_date'])) {
        $machines_not_up_to_date = filter_var($_GET['machines_not_up_to_date'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_up_to_date'])) {
        $machines_up_to_date = filter_var($_GET['machines_up_to_date'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_security_not_ok'])) {
        $machines_security_not_ok = filter_var($_GET['machines_security_not_ok'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_kernel_not_ok'])) {
        $machines_kernel_not_ok = filter_var($_GET['machines_kernel_not_ok'], FILTER_SANITIZE_NUMBER_INT);
    }

    if (isset($_GET['machines_other_not_ok'])) {
        $machines_other_not_ok = filter_var($_GET['machines_other_not_ok'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['total_machines'])) {
        $total_machines = filter_var($_GET['total_machines'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

            $dataget = [
                "entity_id"                   => $entity_id,
                "completename"                => $completename,
                "distribution"                => "alllinux",
                "compliance_total_percent"    => $compliance_total_percent,
                "compliance_security_percent" => $compliance_security_percent,
                "compliance_kernel_percent"   => $compliance_kernel_percent,
                "compliance_other_percent"    => $compliance_other_percent,
                "machines_not_up_to_date"     => $machines_not_up_to_date,
                "machines_up_to_date"         => $machines_up_to_date,
                "machines_security_not_ok"    => $machines_security_not_ok,
                "machines_kernel_not_ok"      => $machines_kernel_not_ok,
                "machines_other_not_ok"       => $machines_other_not_ok,
                "total_machines"              => $total_machines
            ];




    $entitycompliances = xmlrpc_analyze_machine_compliance_distribution_linux($entity_id, $filter, $start, $end);

    $datestring = date("Ymd_His");
/*

    echo "<pre>";
        print_r($entitycompliances);
        echo "</pre>";*/

    foreach ($entitycompliances["distributor_id"] as $index => $value)
    {

        $complRatestotal[] = (string) new medulla_progressbar_static(
            $entitycompliances['compliance_total_percent'][$index],
            "",
            "Overall Linux compliance rate for entity {$completename}.\nPercentage of machines fully up to date."
        );

        $complSecurity[] = (string) new medulla_progressbar_static(
            $entitycompliances['compliance_security_percent'][$index],
            "",
            "Linux security update compliance for entity {$completename}.\nMachines without pending security patches."
        );

        $complkernel[] = (string) new medulla_progressbar_static(
            $entitycompliances['compliance_kernel_percent'][$index],
            "",
            "Linux kernel compliance for entity {$completename}.\nMachines running an up-to-date kernel version."
        );

        $complother[] = (string) new medulla_progressbar_static(
            $entitycompliances['compliance_other_percent'][$index],
            "",
            "Other Linux updates compliance for entity {$completename}.\nCovers non-security and non-kernel packages."
        );

            $distribution=$entitycompliances['distributor_id'][$index];
            $datagrp = [
                "entity_id"                   => $entity_id,
                "completename"                => $completename,
                "distribution"                => $distribution,
                "compliance_total_percent"    => $entitycompliances['compliance_total_percent'][$index],
                "compliance_security_percent" => $entitycompliances['compliance_security_percent'][$index],
                "compliance_kernel_percent"   => $entitycompliances['compliance_kernel_percent'][$index],
                "compliance_other_percent"    => $entitycompliances['compliance_other_percent'][$index],
                "machines_not_up_to_date"     => $entitycompliances['machines_not_up_to_date'][$index],
                "machines_up_to_date"         => $entitycompliances['machines_up_to_date'][$index],
                "machines_security_not_ok"    => $entitycompliances['machines_security_not_ok'][$index],
                "machines_kernel_not_ok"      => $entitycompliances['machines_kernel_not_ok'][$index],
                "machines_other_not_ok"       => $entitycompliances['machines_other_not_ok'][$index],
                "total_machines"              => $entitycompliances['total_machines'][$index]
            ];
            $params[]=$datagrp;
    /*
     |--------------------------------------------------------------------------
     | TOTAL MACHINES DISTRIBUTION
     |--------------------------------------------------------------------------
     | Représente le nombre total de machines Linux rattachées à l'entité.
     */

    if (intval($entitycompliances['total_machines'][$index]) > 0) {

        $msgtitle = _T(
            "Total number of {$distribution} registered under entity {$completename}.\n"
            . "Click to view detailed list of machines.",
            "updates"
        );
        // les Params ['entity_id', 'typeaction', 'grp', 'namegrp'] sont required  pour la creation d'un groupe
        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "Total_{$distribution}_entity", // Identifiant technique du groupe
                "namegrp"    => "Total_{$distribution}_entity_{$completename}_{$datestring}", // Nom fonctionnel du groupe
                "colonne"    => "total_machines",  // Colonne concernée
                "typeaction" => "Compliancelinux" // Contexte Linux
            ]
        );
        $question_largeur = question_custom_colonne("total_machines", $completename, $distribution);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $total_machines_tab[] = $grp->render(
            $entitycompliances['total_machines'][$index],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
        //-----------------------------------------------------
        //-------------- Action distribution ------------------
        //-----------------------------------------------------


    } else {
        $total_machines_tab[] = $entitycompliances['total_machines'][$index];

    }
    /*
     |--------------------------------------------------------------------------
     | MACHINES NOT UP TO DATE DISTRIBUTION (toutes mises à jour)
     |--------------------------------------------------------------------------
     */

    $txtaction= _T("Update complete $distribution \non entity [$completename]", "updates");
    if (intval($entitycompliances['machines_not_up_to_date'][$index]) > 0) {
        // $vue_compliance_distri_linux_entity[]=$View_compliance_distri_linux_entity;
        $msgtitle = _T(
            "{$distribution} in entity {$completename} that have pending updates.\n"
            . "These systems are not fully compliant.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_not_up_to_date_{$distribution}",
                "namegrp"    => "not_up_to_date_{$distribution}_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_not_up_to_date",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_not_up_to_date", $completename, $distribution);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $machines_not_up_to_date_tab[] = $grp->render(
            $entitycompliances['machines_not_up_to_date'][$index],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
        $action_update_complet_distribution[]=new ActionPopupItem($txtaction,
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_Update_distribution_not_up_to_date_on_entity");

    } else {
        // $vue_compliance_distri_linux_entity[]=$NoView_compliance_distri_linux_entity;
        $machines_not_up_to_date_tab[] = $entitycompliances['machines_not_up_to_date'][$index];
        $action_update_complet_distribution[]= new EmptyActionItem1($txtaction,
                                                                    "deployUpdateLinuxType",
                                                                    "updateoneg", "", "updates", "updates"
                                                                );


    }
    /*
     |--------------------------------------------------------------------------
     | MACHINES UP TO DATE DISTRIBUTION
     |--------------------------------------------------------------------------
     */




    if (intval($entitycompliances['machines_up_to_date'][$index]) > 0) {

        $msgtitle = _T(
            "{$distribution} in entity {$completename} that are fully up to date.\n"
            . "No pending updates detected.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_up_to_date_{$distribution}",
                "namegrp"    => "{$distribution}_up_to_date_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_up_to_date",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_up_to_date", $completename, $distribution);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_up_to_date_tab[] = $grp->render(
            $entitycompliances['machines_up_to_date'][$index],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );


    } else {
        $machines_up_to_date_tab[] = $entitycompliances['machines_up_to_date'][$index];

    }
    /*
     |--------------------------------------------------------------------------
     | SECURITY NOT OK DISTRIBUTION
     |--------------------------------------------------------------------------
     */
      $txtaction=_T("Update $distribution security on entity [$completename]", "updates");


    if (intval($entitycompliances['machines_security_not_ok'][$index]) > 0) {
        // $action_update_security_linux[]=$action_update_security_all_linux_entity;
        // $vue_detail_machine_security_linux_entity[]=$View_detail_machine_security_linux_entity;
        $msgtitle = _T(
            "{$distribution} in entity {$completename} missing security updates.\n"
            . "These systems may be exposed to vulnerabilities.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_security_not_ok_{$distribution}",
                "namegrp"    => "{$distribution}_security_issues_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_security_not_ok",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_security_not_ok", $completename, $distribution);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_security_not_ok_tab[] = $grp->render(
            $entitycompliances['machines_security_not_ok'][$index],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    $action_update_security_distribution[] = new ActionPopupItem($txtaction,
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_security_distribution_linux_entity");


    } else {

        // $action_update_security_linux[]=$action_no_update_security_all_linux_entity;
        $machines_security_not_ok_tab[] = $entitycompliances['machines_security_not_ok'][$index];
        // $vue_detail_machine_security_linux_entity[]=$NoView_detail_machine_security_linux_entity;

        $action_update_security_distribution[] = new EmptyActionItem1(
            $txtaction,
            "deployUpdateLinuxType",
            "updateoneg", "", "updates", "updates"
        );

    }


    /*
     |--------------------------------------------------------------------------
     | KERNEL NOT OK DISTRIBUTION
     |--------------------------------------------------------------------------
     */
      $txtaction=_T("Update $distribution kernel on entity [$completename]", "updates");
    if (intval($entitycompliances['machines_kernel_not_ok'][$index]) > 0) {
        // $vue_detail_machine_kernel_linux_entity[]=$View_detail_machine_kernel_linux_entity;
        // $action_update_kernel_linux[]=$action_update_kernel_all_linux_entity;
        $msgtitle = _T(
            "{$distribution} in entity {$completename} running an outdated kernel version.\n"
            . "Kernel update recommended.",
            "updates"
        );

        $tabcgi = array_merge(
            $datagrp,
            [
                "grp"        => "machines_kernel_not_ok_{$distribution}",
                "namegrp"    => "{$distribution}_kernel_not_ok__entity_{$completename}_{$datestring}",
                "colonne"    => "machines_kernel_not_ok",
                "typeaction" => "Compliancelinux"
            ]
        );
        $question_largeur = question_custom_colonne("machines_kernel_not_ok", $completename, $distribution);
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $machines_kernel_not_ok_tab[] = $grp->render(
            $entitycompliances['machines_kernel_not_ok'][$index],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
         $action_update_kernel_distribution[] = new ActionPopupItem($txtaction,
                                                            "deployUpdateLinuxType",
                                                            "updateone", "",
                                                            "updates",
                                                            "updates",
                                                            null,
                                                            320,
                                                            "action_update_kernel_distribution_linux_entity");



    } else {
        // $action_update_kernel_linux[]=$action_no_update_kernel_all_linux_entity;
        // $vue_detail_machine_kernel_linux_entity[]=$NoView_detail_machine_kernel_linux_entity;
        $machines_kernel_not_ok_tab[] = $entitycompliances['machines_kernel_not_ok'][$index];
        $action_update_kernel_distribution[] = new EmptyActionItem1(
            $txtaction,
            "deployUpdateLinuxType",
            "updateoneg", "", "updates", "updates"
        );
    }

    /*
     |--------------------------------------------------------------------------
     | OTHER PACKAGES NOT OK DISTRIBUTION
     |--------------------------------------------------------------------------
     */
     $txtaction=_T("Update $distribution other packages on entity [$completename]", "updates");
     if (intval($entitycompliances['machines_other_not_ok'][$index]) > 0) {

            // $vue_detail_machine_other_linux_entity[]=$View_detail_machine_other_linux_entity;
            // $action_update_other_linux[]=$action_update_other_all_linux_entity;

            $msgtitle = _T(
                "{$distribution} in entity {$completename} with other pending package updates.\n"
                . "Includes non-security and non-kernel packages.",
                "updates"
            );

            $tabcgi = array_merge(
                $datagrp,
                [
                    "grp"        => "machines_other_not_ok_{$distribution}",
                    "namegrp"    => "{$distribution}_other_updates_entity_{$completename}_{$datestring}",
                    "colonne"    => "machines_other_not_ok",
                    "typeaction" => "Compliancelinux"
                ]
            );
            $question_largeur = question_custom_colonne("machines_other_not_ok", $completename, $distribution);
            $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

            $machines_other_not_ok_tab[] = $grp->render(
                $entitycompliances['machines_other_not_ok'][$index],
                $tabcgi,
                $msgtitle,
                "csszoomHover"
            );

        $action_update_other_distribution[] = new ActionPopupItem($txtaction,
                                                                "deployUpdateLinuxType",
                                                                "updateone", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                320,
                                                                "action_update_other_distribution_linux_entity");
        } else {
        // $action_update_other_linux[]=$action_no_update_other_all_linux_entity;        $vue_detail_machine_other_linux_entity[]=$NoView_detail_machine_other_linux_entity;
        $machines_other_not_ok_tab[] = $entitycompliances['machines_other_not_ok'][$index];

        $action_update_other_distribution[]= new EmptyActionItem1($txtaction,
                                                                  "deployUpdateLinuxType",
                                                                  "updateoneg", "", "updates", "updates"
                                                                );
        }
    }// end foreach distribution



    //------------------------------------------------------
    //----------------all distribution ---------------------
    //------------------------------------------------------








    /*
    |--------------------------------------------------------------------------
    | TOTAL MACHINES LINUX
    |--------------------------------------------------------------------------
    | Représente le nombre total de machines Linux rattachées à l'entité.
    */


    if (intval($total_machines) > 0) {

        $msgtitle = _T(
            "Total number of linux registered under entity {$completename}.\n"
            . "Click to view detailed list of machines.",
            "updates"
        );
        // les Params ['entity_id', 'typeaction', 'grp', 'namegrp'] sont required  pour la creation d'un groupe
        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "Total_linux_entity", // Identifiant technique du groupe
                "namegrp"    => "Total_linux_entity_{$completename}_{$datestring}", // Nom fonctionnel du groupe
                "colonne"    => "total_machines",  // Colonne concernée
                "typeaction" => "Compliancedistribution" // Contexte Linux
            ]
        );
        $question_largeur = question_custom_colonne("total_machines", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $alllinux_total_machines[] = $grp->render(
            $total_machines,
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {
        $alllinux_total_machines[] = $total_machines;
    }

    /*
     |--------------------------------------------------------------------------
     | MACHINES NOT UP TO DATE (toutes mises à jour)
     |--------------------------------------------------------------------------
     */
    if (intval($machines_not_up_to_date) > 0) {
        $action_update_complet_linux[]=$action_Update_complete_all_Linux_on_entity;
        $msgtitle = _T(
            "All distribution Linux in entity {$completename} that have pending updates.\n"
            . "These systems are not fully compliant.",
            "updates"
        );

        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "machines_not_up_to_date_linux",
                "namegrp"    => "linux_not_up_to_date_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_not_up_to_date",
                "typeaction" => "Compliancedistribution"
            ]
        );
        $question_largeur = question_custom_colonne("machines_not_up_to_date", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);
        $alllinux_machines_not_up_to_date[] = $grp->render(
            $machines_not_up_to_date,
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {

        $action_update_complet_linux[]=$action_no_Update_complete_all_Linux_on_entity;
        $alllinux_machines_not_up_to_date[] = $machines_not_up_to_date;
    }
    /*
     |--------------------------------------------------------------------------
     | MACHINES UP TO DATE
     |--------------------------------------------------------------------------
     */

    if (intval($machines_up_to_date) > 0) {

        $msgtitle = _T(
            "All distribution Linux in entity {$completename} that are fully up to date.\n"
            . "No pending updates detected.",
            "updates"
        );

        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "machines_up_to_date_linux",
                "namegrp"    => "linux_up_to_date_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_up_to_date",
                "typeaction" => "Compliancedistribution"
            ]
        );
        $question_largeur = question_custom_colonne("machines_up_to_date", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $alllinux_machines_up_to_date[] = $grp->render(
            $machines_up_to_date,
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $alllinux_machines_up_to_date[] = $machines_up_to_date;
    }
    /*
     |--------------------------------------------------------------------------
     | SECURITY NOT OK
     |--------------------------------------------------------------------------
     */

    if (intval($machines_security_not_ok) > 0) {
        $action_update_security_linux[]=$action_update_security_all_linux_entity;
        $msgtitle = _T(
            "All distribution Linux in entity {$completename} missing security updates.\n"
            . "These systems may be exposed to vulnerabilities.",
            "updates"
        );

        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "machines_security_not_ok_linux",
                "namegrp"    => "linux_security_issues_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_security_not_ok",
                "typeaction" => "Compliancedistribution"
            ]
        );
        $question_largeur = question_custom_colonne("machines_security_not_ok", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $alllinux_machines_security_not_ok[] = $grp->render(
            $machines_security_not_ok,
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $alllinux_machines_security_not_ok[] = $machines_security_not_ok;
        $action_update_security_linux[]=$action_no_update_security_all_linux_entity;
    }


    /*
     |--------------------------------------------------------------------------
     | KERNEL NOT OK
     |--------------------------------------------------------------------------
     */
    if (intval($machines_kernel_not_ok) > 0) {
        $action_update_kernel_linux[]=$action_update_kernel_all_linux_entity;
        $msgtitle = _T(
            "All distribution Linux in entity {$completename} running an outdated kernel version.\n"
            . "Kernel update recommended.",
            "updates"
        );

        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "machines_kernel_not_ok_Linux",
                "namegrp"    => "Linux_kernel_not_ok__entity_{$completename}_{$datestring}",
                "colonne"    => "machines_kernel_not_ok",
                "typeaction" => "Compliancedistribution"
            ]
        );
        $question_largeur = question_custom_colonne("machines_kernel_not_ok", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $alllinux_machines_kernel_not_ok[] = $grp->render(
                                                            $machines_kernel_not_ok,
                                                            $tabcgi,
                                                            $msgtitle,
                                                            "csszoomHover"
                                                        );

    } else {
        $alllinux_machines_kernel_not_ok[] = $machines_kernel_not_ok;
        $action_update_kernel_linux[]=$action_no_update_kernel_all_linux_entity;
    }

    /*
     |--------------------------------------------------------------------------
     | OTHER PACKAGES NOT OK
     |--------------------------------------------------------------------------
     */

    if (intval($machines_other_not_ok) > 0) {
        $action_update_other_linux[]=$action_update_other_all_linux_entity;
        $msgtitle = _T(
            "All distribution Linux in entity {$completename} with other pending package updates.\n"
            . "Includes non-security and non-kernel packages.",
            "updates"
        );

        $tabcgi = array_merge(
            $dataget,
            [
                "grp"        => "machines_other_not_ok_Linux",
                "namegrp"    => "Linux_other_updates_entity_{$completename}_{$datestring}",
                "colonne"    => "machines_other_not_ok",
                "typeaction" => "Compliancedistribution"
            ]
        );
        $question_largeur = question_custom_colonne("machines_other_not_ok", $completename, "linux");
        $grp = createLinuxGroupPopup($question_largeur[0],  $question_largeur[1]);

        $alllinux_machines_other_not_ok[] = $grp->render(
            $machines_other_not_ok,
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );

    } else {
        $alllinux_machines_other_not_ok[] = $machines_other_not_ok;
        $action_update_other_linux[]=$action_no_update_other_all_linux_entity;
    }



    $n = new ListInfos(array( "All"),
                       _T("Distribution", "updates"));

    $compliance_total_percent_bar = (string) new medulla_progressbar_static(
        $compliance_total_percent,
        "",
        "Overall Linux compliance rate for entity {$completename}.\nPercentage of machines fully up to date."
    );
    $n->addExtraInfo(array( $compliance_total_percent_bar),
                       _T("compliance<br>total", "updates"));


    $compliance_security_percent_bar = (string) new medulla_progressbar_static(
        $compliance_security_percent,
        "",
        "Linux security update compliance for entity {$completename}.\nMachines without pending security patches."
    );

    $n->addExtraInfo(array($compliance_security_percent_bar),
                     _T("compliance<br>secutity", "updates"));


    $compliance_kernel_percent_bar = (string) new medulla_progressbar_static(
        $compliance_kernel_percent,
        "",
        "Linux kernel compliance for entity {$completename}.\nMachines running an up-to-date kernel version."
    );

    $n->addExtraInfo(array( $compliance_kernel_percent_bar),
                     _T("compliance<br>kernel", "updates"));

    $compliance_other_percent_bar = (string) new medulla_progressbar_static(
        $compliance_other_percent,
        "",
        "Other Linux updates compliance for entity {$completename}.\nCovers non-security and non-kernel packages."
    );
    $n->addExtraInfo(array( $compliance_other_percent_bar),
                     _T("compliance<br>other", "updates"));

    $n->addExtraInfoRaw( $alllinux_machines_not_up_to_date,
                     _T("not<br>up to date", "updates"));
    $n->addExtraInfoRaw( $alllinux_machines_up_to_date,
                     _T("up to_date", "updates"));
    $n->addExtraInfoRaw( $alllinux_machines_security_not_ok,
                     _T("security<br>not ok", "updates"));
    $n->addExtraInfoRaw($alllinux_machines_kernel_not_ok,
                     _T("kernel<br>not ok", "updates"));
    $n->addExtraInfoRaw( $alllinux_machines_other_not_ok,
                     _T("other<br>not ok", "updates"));
    $n->addExtraInfoRaw( $alllinux_total_machines,
                     _T("Total<br>machines", "updates"));



    $n->addActionItemArray($action_update_kernel_linux);
    $n->addActionItemArray($action_update_security_linux);
    $n->addActionItemArray($action_update_other_linux);
    $n->addActionItemArray($action_update_complet_linux);

    $n->setNavBar ="";
    $n->start = 0;
    $n->end =1;
    $converter = new ConvertCouleur();

    $n->setCaptionText(sprintf("%s %s",
                            _T("Compliance All Linux Upgrades on Entity ", 'updates'),
                                $completename));

    $n->setCssCaption(  $border = 1,
                        $bold = 0,
                        $bgColor = "lightgray",
                        $textColor = "black",
                        $padding = "10px 0",
                        $size = "20",
                        $emboss = 1,
                        $rowColor = $converter->convert("lightgray"));

    $n->disableFirstColumnActionLink();
    $n->setParamInfo($params);
    //$n->addActionItemArray($actionEdit);
    $n->display($navbar = 0, $header = 0);
    // -------------------------------------------------
    // ---------------- by Distribution Linux ----------
    // -------------------------------------------------
    $count = $entitycompliances["total_rows"];
    $w = new OptimizedListInfos($entitycompliances["distributor_id"],
                                _T("Distribution", "updates"));
    $w->disableFirstColumnActionLink();
    $w->setcssIds($entitycompliances["distributor_id"]);
    $w->addExtraInfo($complRatestotal, _T("compliance<br>total", "updates"));
    $w->addExtraInfo($complSecurity,_T("compliance<br>security", "updates"));
    $w->addExtraInfo($complkernel,_T("compliance<br>kernel", "updates"));
    $w->addExtraInfo($complother,_T("compliance<br>other", "updates"));

    $w->addExtraInfoRaw($machines_not_up_to_date_tab,
                    _T("not<br>up to date", "updates"));


    $w->addExtraInfoRaw($machines_up_to_date_tab,
                    _T("up to date", "updates"));


    $w->addExtraInfoRaw($machines_security_not_ok_tab,
                    _T("security<br>not ok", "updates"));


    $w->addExtraInfoRaw($machines_kernel_not_ok_tab,
                    _T("kernel<br>not ok", "updates"));


    $w->addExtraInfoRaw($machines_other_not_ok_tab,
                    _T("other<br>not ok", "updates"));


    $w->addExtraInfoRaw($total_machines_tab,
                    _T("Total<br>machine", "updates"));


    $w->addActionItemArray($action_update_complet_distribution);
    $w->addActionItemArray($action_update_security_distribution);
    $w->addActionItemArray($action_update_kernel_distribution);
    $w->addActionItemArray($action_update_other_distribution);

    $w->setParamInfo($params);


   // $converter = new ConvertCouleur();

    $w->setCaptionText(_T("Distribution linux", 'updates'));

    $w->setCssCaption(  $border = 1,
                        $bold = 0,
                        $bgColor = "lightgray",
                        $textColor = "black",
                        $padding = "10px 0",
                        $size = "20",
                        $emboss = 1,
                        $rowColor = $converter->convert("lightgray"));



    $w->setItemCount($count);
    $w->start = 0;
    $w->end = $count;
    $w->setNavBar(new AjaxNavBar($count, $filter,  'updateSearchParamform'));
    $w->display();
?>
