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
 * file modules/medulla_server/medulla_server/computers_list.php
 */

require("modules/medulla_server/includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

/**
 * Construction d’un tableau $param à partir de variables de session et de paramètres GET.
 * On filtre et encode les données pour éviter toute injection.
 */

// Initialisation
$param = [];

/**
 * 1. Gestion des paramètres liés à la présence des ordinateurs
 */
if (isset($_SESSION['computerpresence']) && $_SESSION['computerpresence'] !== "all_computer") {
    $param['computerpresence'] = $_SESSION['computerpresence'];
}

/**
 * 2. Paramètres GET classiques
 */
$directParams = ['gid', 'groupname', 'equ_bool', 'imaging_server'];

foreach ($directParams as $key) {
    if (isset($_GET[$key])) {
        $param[$key] = urlencode($_GET[$key]);
    }
}

/**
 * 3. Paramètres spécifiques si le module "xmppmaster" est activé
 */
if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    // Liste des paramètres autorisés pour xmppmaster
    $allowedParams = ['cmd_id', 'login', 'id', 'ses', 'hos', 'sta'];

    foreach ($allowedParams as $key) {
        if (isset($_GET[$key])) {
            $param[$key] = urlencode($_GET[$key]);
        }
    }

    // Cas particulier : "action" est mappé sur "logview"
    if (isset($_GET['action'])) {
        $param['logview'] = urlencode($_GET['action']);
    }
}

/**
 * 4. Nouveaux paramètres optionnels à prendre depuis $_GET
 */
$extraParams = ['type', 'owner', 'idowner', 'exist', 'is_owner','entity_name','entity_id', 'entity_completename','profile','is_recursive', 'is_dynamic'];

foreach ($extraParams as $key) {
    if (isset($_GET[$key])) {
        $param[$key] = urlencode($_GET[$key]);
    }
}

/**
 * 5. $param est maintenant construit avec toutes les conditions possibles
 */


if (displayLocalisationBar() && (isset($_GET['imaging_server']) && $_GET['imaging_server'] == '' || !isset($_GET['imaging_server']))) {
    $restreint = isset($_GET["restreint"]) ? 1 : 0;
    $ajax = new AjaxFilterLocation(urlStrRedirect("base/computers/ajaxComputersList"), "container", 'location', $param);
    if (! $restreint){
        list($list, $values) = getEntitiesSelectableElements(True);
    }else
    {
        $list = ["UUID".$_GET['entity_id'] =>$_GET['entity_completename']];
        $values = ["UUID".$_GET['entity_id'] =>"UUID".$_GET['entity_id']];
    }

    $ajax->setElements($list);
    $ajax->setElementsVal($values);
    if (!empty($param['gid'])) {
        if (!empty($_SESSION["computers.selected_location." . $param['gid']])) {
            $ajax->setSelected($_SESSION["computers.selected_location." . $param['gid']]);
        }
    } else if (!empty($_SESSION["computers.selected_location"])) {
        $ajax->setSelected($_SESSION["computers.selected_location"]);
    }
} else {
    $ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxComputersList"), "container", $param);
}

$ajax->display();
echo "<br /><br /><br /><br />";
$ajax->displayDivToUpdate();
?>
