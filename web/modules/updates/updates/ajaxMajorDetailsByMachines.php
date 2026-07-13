<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorDetailsByMachines.php
// file : modules/updates/updates/ajaxMajorDetailsByMachines.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");


$actiondetailsByMachslog  = array();
$location = (isset($_GET['location'])) ? htmlentities($_GET['location']) : "";
$gid = (isset($_GET['gid'])) ? htmlentities($_GET['gid']) : "";
$groupname = (isset($_GET['groupname'])) ? htmlentities($_GET['groupname']) : "";
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$field = "";
$contains = (isset($_GET['contains'])) ? htmlentities($_GET['contains']) : "";

global $maxperpage;
$start = (isset($_GET['start']) && is_numeric($_GET['start'])) ? (int)$_GET['start'] : 0;
$maxperpage = (isset($_GET['maxperpage']) && is_numeric($_GET['maxperpage'])) ? (int)$_GET['maxperpage'] : (int)$maxperpage;
$end = (isset($_GET['end']) && is_numeric($_GET['end'])) ? (int)$_GET['end'] : $start + $maxperpage;
$entity = !empty($_GET['entity']) ? htmlspecialchars($_GET['entity']) : "";
$entityName = !empty($_GET['name']) ? htmlentities($_GET['name']) : "";
$entityCompleteName = !empty($_GET['completename']) ? htmlentities($_GET['completename']) : "";
$source = !empty($_GET['source']) ? htmlentities($_GET['source']) : "xmppmaster";
$typeaction= !empty($_GET['typeaction']) ? htmlentities($_GET['typeaction']) : "windows";

// Compteur "Mise à jour non conseillée" : on enveloppe la valeur dans le
// tooltip stylisé (pattern .infomach / .ttable, cf. tooltip.css global) qui
// liste les prérequis matériels Windows 11 non satisfaits par ces machines.
$nbMissing = (isset($_GET['nb_missing']) && is_numeric($_GET['nb_missing'])) ? (int)$_GET['nb_missing'] : 0;
if ($nbMissing > 0) {
    $win11Requirements = array(
        'TPM 2.0',
        'UEFI Secure Boot',
        '1GHz 2-core 64-bit CPU',
        '4GB of RAM',
        '64GB in C:\\ partition',
        'GPU supporting DirectX 12 and WDDM 2.0',
        'Display of 1280 x 720 24bits',
    );
    $reqTooltip = '<table class="ttable win11req-tt">';
    $reqTooltip .= '<tr class="ttabletr tt-section win11req-head"><td class="ttabletd" colspan="2">'
        . htmlspecialchars(_T("The machine does not meet the minimum requirements for Windows 11", "updates"))
        . '</td></tr>';
    foreach ($win11Requirements as $req) {
        $reqTooltip .= '<tr class="ttabletr win11req-row"><td class="ttabletd">'
            . htmlspecialchars($req) . '</td></tr>';
    }
    $reqTooltip .= '</table>';
    $nbMissingCell = '<span class="infomach win11req-tooltip" mydata="'
        . htmlentities($reqTooltip) . '">' . $nbMissing . '</span>';
} else {
    $nbMissingCell = (string)$nbMissing;
}

if ($typeaction == "windows") {
    $n = new ListInfos(array($_GET['W10to10']), _T("Upgrade to latest Win 10", "updates"));
    $n->addExtraInfoCentered(array($_GET['W10to11']), _T("Upgrade Win 10 to latest Win 11", "updates"));
    $n->addExtraInfoCentered(array($_GET['W11to11']), _T("Upgrade to latest Win 11", "updates"));
    $n->addExtraInfoCentered(array($_GET['UPDATED']), _T("Up to date", "updates"));
    $n->addExtraInfoCenteredRaw(array($nbMissingCell), _T("Upgrade Not recommended", "updates"));
    $n->addExtraInfoCentered(array($_GET['totalmachineentity']), _T("Total machines", "updates"));
} else {
    $n = new ListInfos(array($_GET['MS12toMS25']), _T("Upgrade Win Server 2012 to 2025", "updates"));
    $n->addExtraInfoCentered(array($_GET['MS16toMS25']), _T("Upgrade Win Server 2016 to 2025", "updates"));
    $n->addExtraInfoCentered(array($_GET['MS19toMS25']), _T("Upgrade Win Server 2019 to 2025", "updates"));
    $n->addExtraInfoCentered(array($_GET['MS25toMS25']), _T("Upgrade to latest Win Server 2025", "updates"));
    $n->addExtraInfoCentered(array($_GET['UPDATED']), _T("Up to date", "updates"));
    $n->addExtraInfoCentered(array($_GET['nb_missing']), _T("Upgrade Not recommended", "updates"));
    $n->addExtraInfoCentered(array($_GET['totalmachineentity']), _T("Total machines", "updates"));
}
$n->setNavBar = "";
$n->start = 0;
$n->end = 1;
$n->disableFirstColumnActionLink();
$n->display($navbar = 0, $header = 0);

    if ($source == "xmppmaster" ){
        // $statglpiversion = xmlrpc_get_os_xmpp_update_major_details($_GET['entity'],$filter);
        $statglpiversion = xmlrpc_get_os_update_major_details($_GET['entity'],
                                                              $typeaction,
                                                              $filter,
                                                              $start,
                                                              $maxperpage);

    }else{
        $statglpiversion=xmlrpc_get_os_update_major_details($_GET['entity'],
                                                            $typeaction,
                                                            $filter,
                                                            $start,
                                                            $maxperpage);

    };

// Nom machine	Système d'exploitation	Mises à jour Major

$params = [];
$filterOn = [];
$idmachinefrom_xmpp_or_glpi='machineidmajor'; // id xmppmaster
 if ($_GET['source'] != "xmppmaster" ){
         $idmachinefrom_xmpp_or_glpi='inventoryidmajor'; // id glpi
    }
$actionspeclistUpds = [];
$actiondetailsByMachslog = [];
$params = [];


// Sécuriser aussi les tableaux de stat
$statglpiversion = $statglpiversion ?? ['id_machine' => []];

$idmachinefrom_xmpp_or_glpi = ($_GET['source'] != "xmppmaster") ? 'inventoryidmajor' : 'machineidmajor';

foreach ($statglpiversion['id_machine'] as $key => $valeur) {

    $actiondetailsByMachslog[] = new ActionItem(
        _T("Updates History", "updates"),
        "auditUpdateByMachine",
        "history",
        "",
        "updates",
        "updates"
    );

    $actionspeclistUpds[] = new ActionPopupItem(
        sprintf(_T("Deploy this update on machine %s", "updates"), $statglpiversion['machine'][$key]),
        "deployUpdatemajor",
        "updateone",
        '',
        "updates",
        "updates",
        null,
        640,
        "machine"
    );

    $params[] = [
        'entity_id' => $entity,
        'entity_name' => $entityName,
        'complete_name' => $entityCompleteName,
        'maxperpage' => $maxperpage,
        'source' => $source,
        $idmachinefrom_xmpp_or_glpi => $valeur,
        'cn' => $statglpiversion['machine'][$key] ?? '',
        'platform' => $statglpiversion['platform'][$key] ?? '',
        'version' => $statglpiversion['version'][$key] ?? '',
        'update' => $statglpiversion['update'][$key] ?? '',
        'uuid_inventorymachine' => $statglpiversion['uuid_inventorymachine'][$key] ?? '',
        'package_id' => $statglpiversion['package_id'][$key] ?? '',
        'installeur' => $statglpiversion['installeur'][$key] ?? ''
    ];
}

$n = new OptimizedListInfos($statglpiversion["machine"], _T("Machine name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($statglpiversion["platform"], _T("Platform", "updates"));
$n->addExtraInfoCentered($statglpiversion["version"], _T("Version", "updates"));
$n->addExtraInfo($statglpiversion["update"], _T("Upgrade", "updates"));
$n->addActionItemArray($actionspeclistUpds);
$n->addActionItemArray($actiondetailsByMachslog);
// arrInfo contient déjà le slice paginé (LIMIT côté SQL via xmlrpc),
// $count reste le total global utilisé par la navbar.
$count = $statglpiversion["nb_machine"] ?? 0;
$n->start = 0;
$n->end = $count;
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);
$n->setEmptyState(_T("No machines found", "updates"), _T("No machines match the current filter.", "updates"));
$n->display();

// Active le tooltip stylisé sur le compteur "Upgrade Not recommended" du
// tableau récapitulatif (jQuery UI + tooltip.css, même pattern que
// ajaxXmppMachinesList.php). items:"[mydata]" lit l'attribut mydata.
echo '<script>
jQuery(function() {
    if (!(jQuery.ui && jQuery.ui.tooltip)) { return; }
    jQuery(".win11req-tooltip").tooltip({
        position: { my: "left+15 center", at: "right center" },
        items: "[mydata]",
        content: function() { return jQuery(this).attr("mydata"); }
    });
});
</script>';

?>
