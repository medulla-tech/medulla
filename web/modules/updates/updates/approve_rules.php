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

$p = new PageGenerator(_T("Automatic approval rules", 'admin'));
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
    $success = xmlrpc_update_auto_approve_rules($result);

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

// Récupération des données à afficher
$f = xmlrpc_get_auto_approve_rules();

// Initialisation
$htmlelementcheck = [];
$params = [];
$submittedCheckValues = $_POST['check'] ?? [];

foreach ($f['id'] as $indextableau => $id) {
    // Construction des paramètres pour le tableau
    $params[] = array(
        'id' => $id,
        'active_rule' => $f['active_rule'][$indextableau],
        'msrcseverity' => $f['msrcseverity'][$indextableau],
        'updateclassification' => $f['updateclassification'][$indextableau]
    );

    // Détermination si la case doit être cochée
    $isChecked = isset($submittedCheckValues[$id]) ? $submittedCheckValues[$id] : $f['active_rule'][$indextableau];
    $checked = ($isChecked == 1) ? 'checked' : '';

    // Génération des champs input (hidden + checkbox)
    $hiddenInput = sprintf('<input type="hidden" name="check[%s]" value="0">', $id);
    $checkboxInput = sprintf(
        '<input type="checkbox" id="check%s" name="check[%s]" value="1" %s>',
        $id,
        $id,
        $checked
    );

    $htmlelementcheck[] = $hiddenInput . $checkboxInput;
}


// Début du formulaire HTML
echo '<form method="post" action="" name="montableau">';
echo "\n";

// Construction du tableau avec ListInfos
$n = new ListInfos($f['msrcseverity'], _T("Update Severity", "updates"));
$n->addExtraInfo($f['updateclassification'], _T("Update Classification", "updates"));
$n->addExtraInfo($htmlelementcheck, _T("Automatic approval (White list)", "updates"));

$n->setParamInfo($params);
$n->setNavBar = "";
$n->start = 0;
$n->end = count($f['msrcseverity']);

// Affichage du tableau
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);

// Bouton de validation
echo '<input type="hidden" name="form_name" value="montableau">';
echo '<input class="btn btn-primary" type="submit" value="' . _T("Apply", "updates") . '">';
echo "\n</form>";

?>

