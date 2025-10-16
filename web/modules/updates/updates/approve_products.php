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
 */
// modules/admin/admin/manage_entity.php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");
require_once("modules/updates/includes/updates.inc.php");
// Traitement du formulaire
if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'montableau'&& isset($_POST['entityid'])
) {
    $submittedCheckValues = $_POST['check'] ?? []; // Valeurs cochées ou non
    $result = [];
    foreach ($submittedCheckValues as $key => $value) {
        $result[] = [$key, $value]; // Clé = ID de la règle
    }
    // Mise à jour de la table avec les données reçues
    xmlrpc_update_approve_products($result, $_POST['entityid']);
}
generateEntityPage(_T("Approve rule gray_list to white_list", 'updates'),
                            "ajaxApproveProduct",
                            $sidemenu);
<<<<<<< HEAD
=======

>>>>>>> 60d93c2420bf81300a22db153b8e3e0d47695a99
?>
