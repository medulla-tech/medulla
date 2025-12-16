<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

// ICI 
$mobiles_headwind = xmlrpc_get_hmdm_devices();
    
// Retrieving QR code for a specific configuration
$configurationId = 1;
$configurationJson = xmlrpc_get_hmdm_configuration_by_id($configurationId);
$qrCode = $configurationJson;

// Construction du tableau avec OptimizedListInfos
$ids = $col1 = $descript = $enligne = $numeros = $autorisations = $installations = $etatFichiers = $configurations = $actions = [];
$actionQr = [];
$params = [];

if (!is_array($mobiles_headwind)) $mobiles_headwind = [];

foreach ($mobiles_headwind as &$m) {
    $m['source'] = 'headwind';
}

unset($m);

// Filter by device name if filter is provided
if (!empty($filter)) {
    $mobiles_headwind = array_filter($mobiles_headwind, function($mobile) use ($filter) {
        $deviceName = $mobile['number'] ?? '';
        return stripos($deviceName, $filter) !== false;
    });
}

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

    // Standard QR Code action via MMC action API
    $actionQr[] = new ActionItem(_T("QR Code", "mobile"), "qrCode", "qr-code", "", "mobile", "mobile");
    $params[] = [
        'device_number' => $numero,
        'configuration_id' => isset($mobile['configurationId']) ? $mobile['configurationId'] : 1,
    ];
}


$count = is_array($mobiles) ? count($mobiles) : 0;
$count = count($mobiles);
$filter = "";
$n = new OptimizedListInfos($col1, _T("Device's name", "mobile"));
// TODO: adjust AjaxNavBar parameters if needed
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform".($actions?'image':'master')));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

//$n->addExtraInfo($enligne, _T("Status", "mobile"));
$n->addExtraInfo($descript, _T("Description", "mobile"));
$n->addExtraInfo($configurations, _T("Configuration", "mobile"));
$n->addExtraInfo($sources, _T("Model", "mobile"));
$n->addExtraInfo($ip, _T("IP address", "mobile"));
$n->addExtraInfo($installations, _T("Status", "mobile"));
// $n->addExtraInfo($etatFichiers, _T("État des fichiers", "mobile"));

// Attach actions
$n->addActionItemArray($actionQr);
$n->setParamInfo($params);

// $n->setItemCount(count($mobiles));
$n->start = 0;
// $n->end = count($mobiles);

$n->display();
?>
<script type="text/javascript">
jQuery(document).ready(function() {
    jQuery('li.qr-code a').each(function() {
        var $link = jQuery(this);
        var href = $link.attr('href');
        
        $link.on('click', function(e) {
            e.preventDefault();
            window.open(href, '_blank');
        });
    });
});
</script>