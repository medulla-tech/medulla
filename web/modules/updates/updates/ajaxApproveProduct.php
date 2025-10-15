<?php
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

foreach ($f['id'] as $indextableau => $id) {
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
}

$listename=array();
// Début du formulaire HTML
echo '<form method="post" action="" name="montableau">';
foreach($f['name_procedure'] as $name){

    $str = preg_replace('/^up_packages_/', '', $name);
    $str = str_replace("MSOS", _T("Microsoft Server Operating System", "admin"), $str);
    $str = str_replace("Vstudio", _T("Visual studio", "admin"), $str);
    $str = str_replace("Win_Malicious_", _T("Malicious Software Removal Tool_", "admin"), $str);
    $str = str_replace("Office", "Microsoft Office", $str);
    $str = str_replace("Win10", "Windows 10", $str);
    $str = str_replace("Win11", "Windows 11", $str);
    $str = str_replace("_", " ", $str);
    $listename[]=$str;
}
// Construction du tableau avec ListInfos
$n = new ListInfos($listename, _T("Product Microsoft", "updates"));
$n->addExtraInfo($htmlelementcheck, _T("approve update", "updates"));

$n->setParamInfo($params);
$n->setNavBar = "";
$n->start = 0;
$n->end = count($f['name_procedure']);

$converter = new ConvertCouleur();

$n->setCaptionText(sprintf(
    _T("approval update Microsoft", 'updates')
));

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
echo '<input class="btn btn-primary" type="submit" value="' . _T("Apply", "updates") . '">';
echo "\n</form>";
