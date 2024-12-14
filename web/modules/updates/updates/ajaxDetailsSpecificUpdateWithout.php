<?php
/**
 * (c) 2023 Siveo, http://siveo.net/
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
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");

global $conf;
$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$kb = (isset($_GET['kb'])) ? $_GET['kb'] : "";
$updateid = (isset($_GET['updateid'])) ? $_GET['updateid'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";

$without_Upd = xmlrpc_get_machines_needing_update($updateid, $location, $start, $maxperpage, $filter);

$machines = $without_Upd["datas"];
$total = $without_Upd["total"];

echo "<h2>"._T("Machines without update", "updates")."</h2>";
$n = new OptimizedListInfos($machines["name"], _T("Hostname", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($machines["platform"], _T("Platform", "updates"));

$n->start=0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, $filter, "updateSearchParamformWithout"));

$n->display();
