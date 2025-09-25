<?php
/*
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
 *
 */
// modules/admin/admin/manage_entity.php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("Automatic approval rules", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

// Traitement du formulaire
if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'montableau'
) {
    $submittedCheckValues = $_POST['check'] ?? []; // Valeurs cochées ou non

    $result = [];
    foreach ($submittedCheckValues as $key => $value) {
        $result[] = [$key, $value]; // Clé = ID de la règle
    }

    // Mise à jour de la table avec les données reçues
    $success = xmlrpc_update_auto_approve_rules($result, $_POST['entityid']);

    if ($success) {
        new NotifyWidgetSuccess(_T("Rules updated successfully.", "updates"));
        header("Location: " . urlStrRedirect("updates/updates/updatesListWin"));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to update rules.", "updates"));
        header("Location: " . urlStrRedirect("updates/updates/updatesListWin"));
        exit;
    }
}

$_entities = getUserLocations();


$parametresCGI=[];
foreach ($_entities as $value) {
    $completename[] = $value['completename'];
    $uuidNumber = str_replace('UUID', '', $value['uuid']);
    $newElement =  [
        'name' => $value['name'],
        'uuid' => $uuidNumber,
        'completename' => $value['completename'],
        'comments' => $value['comments'],
        'level' => $value['level'],
        'altname' => $value['altname'],
    ];
    // Transformation en paramètres CGI GET
    $parametresCGI[]=http_build_query( $newElement);
}



if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'montableau'
)
{
    $choix = $parametresCGI[$_POST['entityid']];
}else{
    $choix = $parametresCGI[0];
}

$ajax = new AjaxLocation(
     urlStrRedirect("updates/updates/ajaxApproveRules"),
      "mondivlocation",           // div qui affiche la liste des produits
      "selected_location",      // paramètre : $_GET['selected_location']
          $_POST
  );

$ajax->setElements($completename);
$ajax->setElementsVal($parametresCGI);
$ajax->setSelected($choix);
$ajax->display();
$ajax->displayDivToUpdate();


?>

