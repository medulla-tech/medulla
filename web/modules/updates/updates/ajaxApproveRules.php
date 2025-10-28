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
 * file: ajaxApproveRules.php
 */
require_once("modules/xmppmaster/includes/xmlrpc.php");
require("localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

global $maxperpage;
$entityuuid = (isset($_GET['entity'])) ? htmlentities($_GET['entity']) : "UUID0";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

// approve_products
// extract($_GET['entities'], EXTR_PREFIX_SAME, "approve");
// Récupération des données à afficher

// Récupération des données à afficher
$f = xmlrpc_get_auto_approve_rules($_GET['selected_location']['uuid']);

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

$listename=array();
// Début du formulaire HTML

echo '<form method="post" action="" name="montableau" class="approval-form approval-rules">';
// Affichage du tableau

$n = new ListInfos($f['msrcseverity'], _T("Update Severity", "updates"));
$n->setTableHeaderPadding(0);
$n->addExtraInfo($f['updateclassification'], _T("Update Classification", "updates"));
$n->addExtraInfo($htmlelementcheck, _T("Automatic approval (White list)", "updates"));;

$n->setParamInfo($params);
$n->setNavBar = "";
$n->start = 0;
$n->end = count($f['msrcseverity']);

$converter = new ConvertCouleur();

$n->setCssCaption(
    $border = 1,
    $bold = 0,
    $bgColor = "lightgray",
    $textColor = "black",
    $padding = "10px 0",
    $size = "20",
    $emboss = 1,
    $rowColor = $converter->convert("lightgray")
);
// Affichage du tableau
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);
// Bouton de validation
echo '<input type="hidden" name="form_name" value="montableau">';
echo '<input type="hidden" name="entityid" value="'.$_GET['selected_location']['uuid'].'">';
echo '<input type="hidden" name="entityname" value="'.$_GET['selected_location']['name'].'">';
echo '<input class="btnPrimary" type="submit" value="' . _T("Apply", "updates") . '">';
echo "\n</form>";

?>
