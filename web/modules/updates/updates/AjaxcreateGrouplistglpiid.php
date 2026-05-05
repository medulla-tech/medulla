<?php
//ajax direct
require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../dyngroup/includes/dyngroup.php");


if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $entityid = $_POST['entityid'] ?? '';
    $typeaction = $_POST['typeaction'] ?? 'windows';

    if (!function_exists('xmlrpc_get_outdated_major_os_updates_by_entity')) {
        ?>
        <div class="alert alert-danger" style="padding: 10px; background: #f2dfdf; color: #a94442; border: 1px solid #ebccd1; border-radius: 4px;">
            <strong>Erreur !</strong><br>
            La fonction xmlrpc_get_outdated_major_os_updates_by_entity n'existe pas.
        </div>
        <?php
        exit;
    }

    $list_Machine_outdated_major_update  = xmlrpc_get_outdated_major_os_updates_by_entity($entityid, $typeaction);

try {
    $groupname = sprintf (_T("List_Machines_do_not_perform_the_update_%s", "glpi"), date("Y-m-d H:i:s"));
    $group = new Group();
    $group->create($groupname, False);
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
        ?>
        <div class="alert alert-success" style="padding: 10px; background: #dff0d8; color: #3c763d; border: 1px solid #d6e9c6; border-radius: 4px;">
            <strong>Succès !</strong><br>
            Création du groupe <strong>'<?php echo htmlspecialchars($groupname); ?>'</strong> réussie.
        </div>
        <?php
    } else {
        ?>
        <div class="alert alert-danger" style="padding: 10px; background: #f2dfdf; color: #a94442; border: 1px solid #ebccd1; border-radius: 4px;">
            <strong>Erreur !</strong><br>
            Erreur lors de la création du groupe : données incohérentes.
        </div>
        <?php
    }
} catch (Exception $e) {
    ?>
    <div class="alert alert-danger" style="padding: 10px; background: #f2dfdf; color: #a94442; border: 1px solid #ebccd1; border-radius: 4px;">
        <strong>Erreur !</strong><br>
        Erreur lors de la création du groupe <strong>'<?php echo isset($groupname) ? htmlspecialchars($groupname) : ''; ?>'</strong> :
        <br>
        <?php echo htmlspecialchars($e->getMessage()); ?>
    </div>
    <?php
}
}

?>
