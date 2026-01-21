<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$mobiles = xmlrpc_get_hmdm_devices();
$configurations_data = xmlrpc_get_hmdm_configurations();

// map id name
$config_map = [];
if (is_array($configurations_data)) {
    foreach ($configurations_data as $config) {
        if (isset($config['id']) && isset($config['name'])) {
            $config_map[$config['id']] = $config['name'];
        }
    }
}
    
$configurationId = 1;
$configurationJson = xmlrpc_get_hmdm_configuration_by_id($configurationId);
$qrCode = $configurationJson;

$ids = $col1 = $descript = $enligne = $numeros = $autorisations = $installations = $etatFichiers = $configurations = $actions = [];
$actionQr = [];
$actionEdit = [];
$params = [];

if (!is_array($mobiles)) $mobiles = [];

foreach ($mobiles as &$m) {
    $m['source'] = 'headwind';
}

unset($m);

if (!empty($filter)) {
    $mobiles = array_filter($mobiles, function($mobile) use ($filter) {
        $deviceName = $mobile['number'] ?? '';
        return stripos($deviceName, $filter) !== false;
    });
}

foreach ($mobiles as $index => $mobile) {
    $id = 'mob_' . $index;
    $ids[] = $id;

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
        $configId = $mobile['configurationId'] ?? null;
        $configurations[] = isset($configId) && isset($config_map[$configId]) ? $config_map[$configId] : "N/A";
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

    $actionEdit[] = new ActionItem(_T("Edit", "mobile"), "editDevice", "edit", "id", "mobile", "mobile");
    $actionQr[] = new ActionPopupItem(_T("QR Code", "mobile"), "qrCode", "qr-code", "", "mobile", "mobile");
    $params[] = [
        'id' => isset($mobile['id']) ? $mobile['id'] : $index,
        'device_number' => $numero,
        'configuration_id' => isset($mobile['configurationId']) ? $mobile['configurationId'] : 1,
    ];
}


$count = is_array($mobiles) ? count($mobiles) : 0;
$count = count($mobiles);
$filter = "";
$n = new OptimizedListInfos($col1, _T("Device's name", "mobile"));

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
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionQr);
$n->setParamInfo($params);

// $n->setItemCount(count($mobiles));
$n->start = 0;
// $n->end = count($mobiles);

$n->display();
?>
