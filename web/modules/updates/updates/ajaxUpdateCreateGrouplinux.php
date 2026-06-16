<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * file /modules/updates/updates/ajaxUpdateCreateGroup.php
 */

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
