<?php
/*
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
 * file: View_detail_machine_other_linux_entity.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");
/*
echo "<pre>";
print_r($_GET);
echo "</pre>";*/
$updatetype="all";
$entity_id = isset($_GET['entity_id']) ? intval($_GET['entity_id'], 10) : -1;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);


echo "View_detail_machine_other_linux_entity";
echo "<pre>";
echo $entity_id;
echo "<br>";
echo $updatetype;
echo "</pre>";

$machines  = xmlrpc_get_machines_by_update_type($entity_id,
                                                $updatetype,
                                                $filter_str,
                                                $start,
                                                $end);
echo "<pre>";
print_r($machines);
echo "</pre>";


?>
