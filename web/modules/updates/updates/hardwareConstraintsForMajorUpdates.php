<?php
/* **
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
 * file updates/hardwareConstraintsForMajorUpdates.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

// Récupération de la configuration globale
global $conf;

// Définir le nombre maximum de lignes à afficher par page, depuis la configuration
$maxperpage = $conf["global"]["maxperpage"] ?? 20;

// Récupération sécurisée avec contrôle de type
$start = filter_input(INPUT_GET, 'start', FILTER_VALIDATE_INT) ?? 0;
$end = isset($_GET['end']) ? $start + $maxperpage : $maxperpage;
$filter = filter_input(INPUT_GET, 'filter', FILTER_SANITIZE_STRING) ?? "";
$entityname = filter_input(INPUT_GET, 'completename', FILTER_SANITIZE_STRING) ?? "";
$entityid = filter_input(INPUT_GET, 'entity', FILTER_VALIDATE_INT) ?? 0;
echo '
<form id="myForm">
    <input type="hidden" name="entityid" value="'.htmlspecialchars($entityid).'">
    <button class="btn btn-primary" type="submit">Creation Group</button>
</form>';

$titlepage = sprintf(_T("List Machines do not perform the update for now [ Entity %s ]"), htmlspecialchars($entityname));
$p = new PageGenerator($titlepage);
$p->setSideMenu($sidemenu);
$p->display();
$list_Machine_outdated_major_update = xmlrpc_get_outdated_major_os_updates_by_entity($entityid, $start, $end, $filter);
$n = new ListInfos($list_Machine_outdated_major_update['hostname'], _T("Computer", "updates"));
$n->addExtraInfo($list_Machine_outdated_major_update['platform'], _T("Platform", "updates"));
$n->addExtraInfo($list_Machine_outdated_major_update['oldcode'], _T("Code Version", "updates"));
$n->addExtraInfo($list_Machine_outdated_major_update['lang_code'], _T("Langue Code", "updates"));
$n->setNavBar(new AjaxNavBar($list_Machine_outdated_major_update['nb_element'], $filter, 'search_computer'));
$n->start = $start;
$n->end = isset($_GET['end']) ? $_GET['end'] : $maxperpage;
$n->display();
?>

<script>
jQuery(document).ready(function () {
    jQuery('#myForm').on('submit', function (e) {
        e.preventDefault(); // Empêche l'envoi classique
        jQuery.ajax({
            url: 'modules/updates/updates/AjaxcreateGrouplistglpiid.php',
            type: 'POST',
            data: jQuery(this).serialize(), // Sérialise les données du formulaire
            success: function (response) {
                alert("Réponse du serveur : " + response);
            },
            error: function (xhr, status, error) {
                alert("Erreur AJAX : " + error);
            }
        });
    });
});
</script>

