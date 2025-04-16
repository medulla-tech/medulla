<?php
/**
 * (c) 2022-2024 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * file modules/updates/updates/ajaxMajorEntitiesList.php
 */
require_once("modules/updates/includes/html.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

global $conf;
// echo "modules/updates/updates/ajaxMajorEntitiesList.php";

// $r = getUserLocations1();

$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$source  = (isset($_GET['$source']) ? $_GET['$source']: "");

echo "<pre>";
print_r($_GET );
echo "</pre>";

// Récupere les id des machine
$machinesListGlpi = getRestrictedComputersListuuid(0, -1, ['gid' => $_GET['gid']], false, true);

// Extraire les numéros des UUIDs
$numbers = array_map(function($uuid) {
    // Utiliser une expression régulière pour extraire les chiffres à la fin de la chaîne
    preg_match('/\d+$/', $uuid, $matches);
    return (int)$matches[0]; // Convertir en entier
}, $machinesListGlpi);

echo "<pre>";
print_r($numbers );
echo "</pre>";
//JFKJFK
$mach = xmlrpc_get_os_update_major_stats_list_grp( $_GET['groupname'], $numbers, $presence=False);
echo "<br><pre>";
print_r($mach );
echo "</pre>";
?>
