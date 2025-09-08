<?php
require_once("modules/mobile/includes/xmlrpc.php");

// ICI 
$mobiles_headwind = xmlrpc_getDevice();
$mobiles_nano = xmlrpc_nano_devices();

// Construction du tableau avec OptimizedListInfos
$ids = $col1 = $descript = $enligne = $numeros = $autorisations = $installations = $etatFichiers = $configurations = $actions = [];

if (!is_array($mobiles_headwind)) $mobiles_headwind = [];
if (!is_array($mobiles_nano)) $mobiles_nano = [];

foreach ($mobiles_headwind as &$m) {
    $m['source'] = 'headwind';
}
foreach ($mobiles_nano as &$m) {
    $m['source'] = 'nano';
}
unset($m);

$mobiles = array_merge($mobiles_headwind, $mobiles_nano);


foreach ($mobiles as $index => $mobile) {
    $id = 'mob_' . $index;
    $ids[] = $id;

    // Détection de la source
    $is_headwind = $mobile['source'] === 'headwind';
    $is_nano = $mobile['source'] === 'nano';
    $origine = $is_headwind ? 'Android' : 'IOs';
    $sources[] = $origine;

    if ($is_headwind) {
        $numero = $mobile['number'];
        $statut = isset($mobile['status_active']) && $mobile['status_active'] == 1 ? 'up' : 'down';
        $descript[] = $mobile['description'] ?? "N/A";
        $ip[] = $mobile['publicIp'] ?? "Inconnue";
        $installations[] = $mobile['custom2'] ?? "Inconnue";  // Décommenté
        $etatFichiers[] = $mobile['custom3'] ?? "N/A";
        $configurations[] = $mobile['configurationId'] ?? "N/A";
    } elseif ($is_nano) {
    $numero = $mobile['serial_number'] ?? $mobile['id'] ?? "Inconnu";
    $statut = (!empty($mobile['token_update_at']) && (strtotime($mobile['token_update_at']) > time() - 600)) ? 'up' : 'down';

    $created = !empty($mobile['created_at']) ? date('d/m/Y H:i', strtotime($mobile['created_at'])) : "—";
    $updated = !empty($mobile['updated_at']) ? date('d/m/Y H:i', strtotime($mobile['updated_at'])) : "—";
    $descript[] = "$created";

    $ip[] = "-";
    $installations[] = !empty($mobile['bootstrap_token_at']) ? date('d/m/Y', strtotime($mobile['bootstrap_token_at'])) : "—";
    $etatFichiers[] = !empty($mobile['unlock_token_at']) ? 'Unlock prêt' : (!empty($mobile['authenticate_at']) ? 'Authentifié' : 'Incomplet');
    $configurations[] = !empty($mobile['authenticate_at']) ? date('d/m/Y', strtotime($mobile['authenticate_at'])) : "Profil inconnu";
    } else {
        $numero = "Inconnu";
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
        <li class='delete'><a href='#' class='delete-link' data-id='{$index}' title='Supprimer'>" . _T("", "mobile") . "</a></li>
    </ul>
    ";
}


// $count = is_array($mobiles) ? count($mobiles) : 0;
// $count = count($mobiles);
// $filter = "";
$n = new OptimizedListInfos($col1, _T("Nom de l'appareil", "mobile"));
// CA FAUDRA CHANGER les parametres de AjaxNavBar
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform".($actions?'image':'master')));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

//$n->addExtraInfo($enligne, _T("Status", "mobile"));
$n->addExtraInfo($descript, _T("Description", "mobile"));
$n->addExtraInfo($configurations, _T("Configuration", "mobile"));
$n->addExtraInfo($sources, _T("Origine", "mobile"));
$n->addExtraInfo($ip, _T("Ip server", "mobile"));
// $n->addExtraInfo($installations, _T("État de l'installation", "mobile"));
$n->addExtraInfo($etatFichiers, _T("État des fichiers", "mobile"));
$n->addExtraInfo($actions, _T("Actions", "mobile"));



// $n->setItemCount(count($mobiles));
$n->start = 0;
// $n->end = count($mobiles);

$n->display();
?>