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
 * file: ajaxApproveProduct.php
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

$f = xmlrpc_get_approve_products($_GET['selected_location']['uuid']);

// Initialisation
$htmlelementcheck = [];
$params = [];
$submittedCheckValues = $_POST['check'] ?? [];
$cssClasses= [];
$listename=[];
$counttitleproduit=0;
// Début du formulaire HTML
echo '<form method="post" action="" name="montableau" class="approval-form">';
$currentFamily = null;
foreach ($f['name_procedure'] as $indextableau => $name) {
    $id = $f['id'][$indextableau];

    $str = preg_replace('/^up_packages_/', '', $name);

    if (str_starts_with($str, "MSO")) {
        $productfamily="server";}
    elseif (str_starts_with($str, "WS")) {
        $productfamily="server";}
    elseif (str_starts_with($str, "Vstudio")) {
        $productfamily="Vstudio";}
    elseif (str_starts_with($str, "office")) {
        $productfamily="office";}
    elseif (str_starts_with($str, "Win10")) {
        $productfamily="Win10";}
    elseif (str_starts_with($str, "Win11")) {
        $productfamily="Win11";}
    elseif (str_starts_with($str, "Win_Malicious_")) {
        $productfamily="Win_Malicious_";}

    if ($currentFamily !== $productfamily || $currentFamily == null) {
        if ($productfamily == "server"){
            $listename[] = _T("MICROSOFT SERVER", "updates");
        }elseif  ($productfamily == "Vstudio"){
            $listename[] = _T("MICROSOFT VISUAL STUDIO", "updates");
        }elseif  ($productfamily == "office"){
            $listename[] = _T("MICROSOFT OFFICE", "updates");
        }elseif  ($productfamily == "Win10"){
            $listename[] = _T("MICROSOFT WINDOWS 10", "updates");
        }elseif  ($productfamily == "Win11"){
            $listename[] = _T("MICROSOFT WINDOWS 11", "updates");
        }elseif  ($productfamily == "Win_Malicious_"){
            $listename[] = _T("MALICIOUS SOFTWARE REMOVAL TOOL", "updates");
        }
        $htmlelementcheck[] = '&nbsp;';
        $cssClasses[] = "family-separator";
        $counttitleproduit++;
        //$cssClasses[] = "sub-section-row";
    }

    $currentFamily=$productfamily;
    $str = str_replace("MSOS", _T("Microsoft Server Operating System", "updates"), $str);
    $str = str_replace("Vstudio", _T("Visual studio", "updates"), $str);
    $str = str_replace("Win_Malicious_", _T("Malicious Software Removal Tool_", "updates"), $str);
    $str = str_replace("office", "Microsoft Office", $str);
    $str = str_replace("Win10", "Windows 10", $str);
    $str = str_replace("Win11", "Windows 11", $str);
    $str = str_replace("WS", _T("Microsoft Server Operating System", "updates"), $str);

    $str = str_replace("_", " ", $str);
    // Récupération du commentaire correspondant (s'il existe)
    $comment = isset($f['comment'][$indextableau]) ? htmlspecialchars($f['comment'][$indextableau]) : '';
    // Construction du span avec info-bulle
    $listename[] = "<span title=\"$comment\">$str</span>";
     // Construction des paramètres pour le tableau
    $params[] = array(
        'id' => $id,
        'enable' => $f['enable'][$indextableau],
        'name_procedure' => $f['name_procedure'][$indextableau]
    );

    // Détermination si la case doit être cochée
    $isChecked = isset($submittedCheckValues[$id]) ? $submittedCheckValues[$id] : $f['enable'][$indextableau];
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
    # on definie les css appliquue au produit
    if ($productfamily == "server"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "Vstudio"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "office"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "Win10"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "Win11"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "Win_Malicious_"){
           $cssClasses[] ="family-produit";
        }
}

// Construction du tableau avec ListInfos
$n = new ListInfos($listename, _T("Product Microsoft", "updates"));
$n->setTableHeaderPadding(16);

$n->addExtraInfo($htmlelementcheck, _T("approve update", "updates"));
// $n->addExtraClassCssLigne(1, "highlight");
// $n->addExtraClassCssLigne(3, "warning");
// $n->addExtraClassCssColonne(2, "col-status");
$n->setParamInfo($params);
$n->setNavBar = "";
$n->start = 0;
$n->end = count($f['name_procedure'])+$counttitleproduit;

$n->setCssCaptionClass("table-rounded caption-style");


$n->setCssClasses($cssClasses);
// Affichage du tableau
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);
// Bouton de validation
echo '<input type="hidden" name="form_name" value="montableau">';
echo '<input type="hidden" name="entityid" value="'.$_GET['selected_location']['uuid'].'">';
echo '<input type="hidden" name="entityname" value="'.$_GET['selected_location']['name'].'">';
echo '<input class="btnPrimary" type="submit" value="' . _T("Apply", "updates") . '">';
echo "\n</form>";
