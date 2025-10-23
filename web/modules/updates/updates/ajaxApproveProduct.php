<?php
require_once("modules/xmppmaster/includes/xmlrpc.php");
require("localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");
?>

<style>
/* separateur de list */
.family-separator td {
    background: linear-gradient(to bottom, #f8f8f8, #232323);
    color: white;
    font-weight: bold;
    text-align: center;
    border-top: 3px solid #7caf94;
    border-bottom: 3px solid #4CAF50;
    font-size: 16px; /* Taille de la police */
  }

  /* Ligne de produit */
  .family-produit td {
    background: linear-gradient(to bottom, #9d9d9d, #dcdcdc); /* contraste plus net */
    color: #1a1a1a;
    font-weight: 600;
    font-size: 14px;
    padding: 12px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.4),
                inset 0 -2px 4px rgba(255,255,255,0.2); /* ombres internes */
  }

.section-icon {
    font-size: 1.8em;
    vertical-align: middle;
    color: #2c3e50;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    margin-right: 8px;
}


/* Ligne de sous-section (plus foncée et élégante) */
.sub-section-row {
    background: linear-gradient(135deg, #f8f8f8, #040404); /* effet de dégradé doux */
    color: #1a1a1a; /* texte plus contrasté */
    font-weight: 600;
    font-size: 1.25em; /* texte plus grand */
    padding: 10px;
}

.sub-section-row td {
    background-color: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(2px); /* effet verre dépoli (si supporté) */
    border-top: 2px solid #388E3C; /* vert plus foncé pour la cohérence */
    border-bottom: 2px solid #388E3C;
/*     background-color: rgba(255, 255, 255, 0.4); */
    padding: 10px 12px;
}

/* Optionnel : effet au survol */
.sub-section-row:hover {
    background: linear-gradient(135deg, #dcdcdc, #cfcfcf);
    transition: background 0.3s ease;
}



.caption-style {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    padding: 10px;
    text-align: center;
    background: linear-gradient(to bottom, #383838, #999999);
    border: 2px solid #9bc1ff;
    border-image: linear-gradient(to bottom, #3b3b3b, #8c8c8c) 1;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border-top-left-radius: 10px;   /* Arrondi coin haut gauche */
    border-top-right-radius: 10px;  /* Arrondi coin haut droit */
}

/* Style pour le tableau */
.table-rounded {
    border-collapse: separate; /* important pour que border-radius fonctionne */
    border-spacing: 0;
    border: 2px solid #eeedff;
    border-radius: 10px; /* Arrondi global du tableau */
    overflow: hidden;    /* pour que les cellules ne dépassent pas les coins arrondis */
}

.table-rounded td {
    padding: 8px;
    border-bottom: 1px solid #ddd; /* exemple de séparateur de lignes */
}


/* titre colonne*/
.listinfos thead {
    background-color: #797979; /* fond bleu */
    color: white;              /* texte blanc */
    text-align: left;        /* centrer le texte */
    font-weight: bold;
    font-size: 16px;
}

/* Style des cellules de l'en-tête */
.listinfos thead th {
    padding: 10px;
    border-bottom: 2px solid #005fa3; /* ligne séparatrice */
}

</style>

<?php
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

// Début du formulaire HTML
echo '<form method="post" action="" name="montableau">';
$currentFamily = null;
foreach ($f['name_procedure'] as $indextableau => $name) {
    $id = $f['id'][$indextableau];

    $str = preg_replace('/^up_packages_/', '', $name);

    if (str_starts_with($str, "MSO")) {
        $productfamily="server";}
    elseif (str_starts_with($str, "WS")) {
        $productfamily="server";}
    elseif (str_starts_with($str, "Vstudio")) {
        $productfamily="vstudio";}
    elseif (str_starts_with($str, "Office")) {
        $productfamily="Office";}
    elseif (str_starts_with($str, "Win10")) {
        $productfamily="Win10";}
    elseif (str_starts_with($str, "Win11")) {
        $productfamily="Win11";}
    elseif (str_starts_with($str, "Win_Malicious_")) {
        $productfamily="Win_Malicious_";}

    if ($currentFamily !== $productfamily || $currentFamily == null) {
        if ($productfamily == "server"){
            $listename[] = '<span class="section-icon">'."&#x1F5A5;".'</span>'._T("SERVER MICROSOFT", "updates");
        }elseif  ($productfamily == "vstudio"){
            $listename[] = _T(" VISUAL STUDIO", "updates");
        }elseif  ($productfamily == "Office"){
            $listename[] =  '<span class="section-icon">'."&#x1F4DD;&#x1F4CB;&#x1F4C8;&#x1F4CA;".'</span>'._T("SUITE OFFICE", "updates");
        }elseif  ($productfamily == "Win10"){
            $listename[] = '<span class="section-icon">'."&#x1F4BB; ".'</span>'._T("MICROSOFT WINDOWS 10", "updates");
        }elseif  ($productfamily == "Win11"){
            $listename[] ='<span class="section-icon">'."&#x1F4BB; ".'</span>'._T("MICROSOFT WINDOWS 11", "updates");
        }elseif  ($productfamily == "Win_Malicious_"){
            $listename[] = '<span class="section-icon">'." &#x1F6E1; &#xFE0F; &#x1F9A0; &#x1F6E1; &#xFE0F;".'</span>'._T(" MALICIOUS SOFTWARE REMOVAL TOOL", "updates"). '<span class="section-icon">';
        }
        $htmlelementcheck[] ='<span class="section-icon">'."&#x26A1&#x2728;".'</span>';
        $cssClasses[] = "family-separator";
        //$cssClasses[] = "sub-section-row";

    }

    $currentFamily=$productfamily;
    $str = str_replace("MSOS", _T("Microsoft Server Operating System", "admin"), $str);
    $str = str_replace("Vstudio", _T("Visual studio", "admin"), $str);
    $str = str_replace("Win_Malicious_", _T("Malicious Software Removal Tool_", "admin"), $str);
    $str = str_replace("Office", "Microsoft Office", $str);
    $str = str_replace("Win10", "Windows 10", $str);
    $str = str_replace("Win11", "Windows 11", $str);
    $str = str_replace("WS", _T("Microsoft Server Operating System", "admin"), $str);

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
        }elseif  ($productfamily == "vstudio"){
            $cssClasses[] ="family-produit";
        }elseif  ($productfamily == "Office"){
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
$n = new ListInfos($listename,  '<span class="section-icon">'."&#x1FA9F;".'</span>'._T("Product Microsoft", "updates"));

$n->addExtraInfo($htmlelementcheck,'<span class="section-icon">'."&#x2705;".'</span>' ._T("approve update", "updates"));
// $n->addExtraClassCssLigne(1, "highlight");
// $n->addExtraClassCssLigne(3, "warning");
// $n->addExtraClassCssColonne(2, "col-status");
$n->setParamInfo($params);
$n->setNavBar = "";
$n->start = 0;
$n->end = count($f['name_procedure']);

$converter = new ConvertCouleur();
$titre= "🪟"._T("Approval Update Microsoft", 'updates');
$n->setCaptionText($titre);
$n->setCssCaptionClass("table-rounded caption-style");


$n->setCssClasses($cssClasses);
// Affichage du tableau
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);
// Bouton de validation
echo '<input type="hidden" name="form_name" value="montableau">';
echo '<input type="hidden" name="entityid" value="'.$_GET['selected_location']['uuid'].'">';
echo '<input type="hidden" name="entityname" value="'.$_GET['selected_location']['name'].'">';
echo '<input class="btn btn-primary" type="submit" value="' . _T("Apply", "updates") . '">';
echo "\n</form>";
