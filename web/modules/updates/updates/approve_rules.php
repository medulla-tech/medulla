<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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
 *
 */
// modules/admin/admin/manage_entity.php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("Approve rule gray_list to white_list", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

$f = xmlrpc_get_auto_approve_rules();

$htmlelementcheck = [];
$params = [];
$submittedCheckValues = $_POST['check'] ?? []; // Récupérer les valeurs cochées si formulaire soumis

foreach ($f['id'] as $key => $valeur) {
    $params[] = array(
        'id' => $f['id'][$key],
        'active_rule' => $f['active_rule'][$valeur],
        'msrcseverity' => $f['msrcseverity'][$valeur],
        'updateclassification' => $f['updateclassification'][$valeur]
    );

    // Prendre les valeurs du formulaire si soumises, sinon garder les valeurs initiales
    $isChecked = isset($submittedCheckValues[$valeur]) ? $submittedCheckValues[$valeur] : $f['active_rule'][$valeur];
    $checked = ($isChecked == 1) ? 'checked' : '';

    $hiddenInput = sprintf('<input type="hidden" name="check[%s]" value="0">', $valeur);
    $checkboxInput = sprintf(
        '<input type="checkbox" id="check%s" name="check[%s]" value="1" %s>',
        $f['id'][$key],
        $f['id'][$key],
        $checked
    );
    $htmlelementcheck[] = $hiddenInput . $checkboxInput;
}



echo "\n";
echo '<form method="post" action="" name="montableau">';
echo "\n";
$n = new ListInfos( $f['msrcseverity'], _T("Update Severity", "updates"));
$n->addExtraInfo($f['updateclassification'], _T("Update Classification", "updates"));
$n->addExtraInfo($htmlelementcheck, _T("validate rule", "updates"));


$n->setParamInfo($params);
$n->setNavBar ="";
$n->start = 0;
$n->end =count($f['msrcseverity']);

$converter = new ConvertCouleur();

$n->setCaptionText(sprintf(_T("Auto-approval rules: automatic whitelisting based on update severity and classification.", 'updates'),
                            ));

$n->setCssCaption(  $border = 1,
                    $bold = 0,
                    $bgColor = "lightgray",
                    $textColor = "black",
                    $padding = "10px 0",
                    $size = "20",
                    $emboss = 1,
                    $rowColor = $converter->convert("lightgray"));

        $n->disableFirstColumnActionLink();
        //$n->setParamInfo($params);
        //$n->addActionItemArray($actionEdit);
        $n->display($navbar = 0, $header = 0);
        echo'<input type="hidden" name="form_name" value="montableau">';
echo '<input type="submit" value="Submit">';
echo "\n</form>";
if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'montableau'
) {
    $result = [];
    foreach ($submittedCheckValues as $key => $value) {
        $result[] = [$key, $value];
    }
    // mise a jour de la table
    xmlrpc_update_auto_approve_rules($result);
}
?>

