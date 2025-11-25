<?php
require_once("modules/mobile/includes/xmlrpc.php");

// ICI 
$mobiles_headwind = xmlrpc_get_hmdm_devices();
    
// Retrieving QR code for a specific configuration
$configurationId = 1;
$configurationJson = xmlrpc_get_hmdm_configuration_by_id($configurationId);
$qrCode = $configurationJson;

// Construction du tableau avec OptimizedListInfos
$ids = $col1 = $descript = $enligne = $numeros = $autorisations = $installations = $etatFichiers = $configurations = $actions = [];

if (!is_array($mobiles_headwind)) $mobiles_headwind = [];

foreach ($mobiles_headwind as &$m) {
    $m['source'] = 'headwind';
}

unset($m);

// $mobiles = array_merge($mobiles_headwind, $mobiles_nano);
$mobiles = $mobiles_headwind; // Pour le moment on n'affiche que les headwind

foreach ($mobiles as $index => $mobile) {
    $id = 'mob_' . $index;
    $ids[] = $id;

    // Détection de la source
    $is_headwind = $mobile['source'] === 'headwind';
    $origine = $is_headwind ? 'Android' : 'Inconnu';
    $sources[] = $origine;

    if ($is_headwind) {
        $numero = $mobile['number'];
        $statut = isset($mobile['status_active']) && $mobile['status_active'] == 1 ? 'up' : 'down';
        $descript[] = $mobile['description'] ?? "N/A";
        $ip[] = $mobile['publicIp'] ?? "Inconnue";
        $installations[] = $mobile['custom2'] ?? "Inconnue"; 
        $etatFichiers[] = $mobile['custom3'] ?? "N/A";
        $configurations[] = $mobile['configurationId'] ?? "N/A";
    } 
    else {
        $numero = "Inconnue";
        $statut = "down";
        $descript[] = "N/A";
        $ip[] = "Inconnue";
        $installations[] = "N/A";
        $etatFichiers[] = "N/A";
        $configurations[] = "N/A";
    }


    $col1[] = "<a href='#' class='mobilestatus {$statut}'>{$numero}</a>";

    $actions[] = "
    <ul class='action' style='list-style-type: none; padding: 0; margin: 0; display: flex; gap: 8px; align-items: center;'>
        <li class='configuremobile'><a href='#' title='Éditer'>" . _T("", "mobile") . "</a></li>  
        <li class='mobilepush'><a href='#' title='Push Message'>" . _T("", "mobile") . "</a></li>
        <li class='audit'><a href='#' title='Logs'>" . _T("", "mobile") . "</a></li>
        <li class='delete'><a href='/hmdm/rest/private/devices/$numero' data-method='DELETE' class='delete-link' data-id='{$index}' title='Supprimer'>" . _T("", "mobile") . "</a></li>
        <li class='delete'><a href='/hmdm/rest/public/qr/$qrCode?deviceId=$numero' data-method='GET' class='delete-link' target='_blank' title='QR Code'>" . _T("", "mobile") . "</a></li>
    </ul>
    ";
}


$count = is_array($mobiles) ? count($mobiles) : 0;
$count = count($mobiles);
$filter = "";
$n = new OptimizedListInfos($col1, _T("Nom de l'appareil", "mobile"));
// TODO: adjust AjaxNavBar parameters if needed
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform".($actions?'image':'master')));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

//$n->addExtraInfo($enligne, _T("Status", "mobile"));
$n->addExtraInfo($descript, _T("Description", "mobile"));
$n->addExtraInfo($configurations, _T("Configuration", "mobile"));
$n->addExtraInfo($sources, _T("Modèle", "mobile"));
$n->addExtraInfo($ip, _T("Adresse ip", "mobile"));
$n->addExtraInfo($installations, _T("Statut", "mobile"));
// $n->addExtraInfo($etatFichiers, _T("État des fichiers", "mobile"));
$n->addExtraInfo($actions, _T("Actions", "mobile"));



// $n->setItemCount(count($mobiles));
$n->start = 0;
// $n->end = count($mobiles);

$n->display();
?>