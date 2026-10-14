<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxUpdateCreateGrouplinux.php

require_once("modules/dyngroup/includes/dyngroup.php"); # for Group Class
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/updates/includes/xmlrpc.php");


try {
    // Vérification des paramètres obligatoires
    $requiredParams = ['entity_id', 'typeaction', 'grp', 'namegrp'];
    foreach ($requiredParams as $param) {
        if (!array_key_exists($param, $_GET)) {
            throw new Exception("Paramètre '$param' manquant.");
        }
    }

    // Récupération des machines
    $namemachine = xmlrpc_get_machines_update_grp(
        $_GET['entity_id'],
        $_GET['typeaction'],
        $_GET['grp']
    );

    if ($namemachine === false || empty($namemachine)) {
        throw new Exception("Aucune machine trouvée pour les critères spécifiés.");
    }

    // Création du groupe
    $group = new Group();
    $groupCreated = $group->create($_GET['namegrp'], false);

    if (!$groupCreated) {
        throw new Exception("Échec de la création du groupe.");
    }

    // Ajout des membres
    $membersAdded = $group->addMembers($namemachine);

    if ($membersAdded === false) {
        throw new Exception("Échec de l'ajout des membres au groupe.");
    }

    // HTML pour le succès
    ?>
    <div class="alert alert-success" style="padding: 10px; background: #dff0d8; color: #3c763d; border: 1px solid #d6e9c6; border-radius: 4px;">
        <strong>Succès !</strong><br>
        Création du groupe <strong>'<?php echo htmlspecialchars($_GET['namegrp']); ?>'</strong> réussie.
    </div>
    <?php

} catch (Exception $e) {
    // HTML pour l'erreur
    ?>
    <div class="alert alert-danger" style="padding: 10px; background: #f2dfdf; color: #a94442; border: 1px solid #ebccd1; border-radius: 4px;">
        <strong>Erreur !</strong><br>
        Erreur lors de la création du groupe <strong>'<?php echo htmlspecialchars($_GET['namegrp']); ?>'</strong> :
        <br>
        <?php echo htmlspecialchars($e->getMessage()); ?>
    </div>
    <?php
}

?>
