<?php
//ajax direct
require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../dyngroup/includes/dyngroup.php");


if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['entityid'] ?? '';
    if (!function_exists('xmlrpc_get_outdated_major_os_updates_by_entity')) {
    echo "fonction existe pas";
    }

$list_Machine_outdated_major_update  = xmlrpc_get_outdated_major_os_updates_by_entity($action);

$groupname = sprintf (_T("List_Machines_do_not_perform_the_update_%s", "glpi"), date("Y-m-d H:i:s"));
$group = new Group();
$group->create($groupname, False);
print_r($list_Machine_outdated_major_update['glpi_id']);
$result = array();
// Vérifiez que les deux tableaux ont la même longueur
if (count($list_Machine_outdated_major_update['glpi_id']) === count($list_Machine_outdated_major_update['hostname'])) {
    // Parcourez les tableaux et créez le tableau de dictionnaires
    for ($i = 0; $i < count($list_Machine_outdated_major_update['glpi_id']); $i++) {
        $result[] = array(
            'uuid' => 'uuid' . $list_Machine_outdated_major_update['glpi_id'][$i],
            'hostname' =>  $list_Machine_outdated_major_update['hostname'][$i]
        );
    }
    $group->miniAddMembers($result);
    // Affichez le résultat
    echo "Creation Group ".$groupname;
} else {
    echo "Erreur creation group ".$groupname;
}
}

?>
