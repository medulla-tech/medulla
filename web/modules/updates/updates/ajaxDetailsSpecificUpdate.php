<?php
/**
 * (c) 2022-2023 Siveo, http://siveo.net/
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
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$filterCTX = "Microsoft";
$field = "platform";

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filterCTX;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = $location;
$ctx['uuid'] = $uuid;

$withUpd = [];
$withoutUpd = [];

$titles_with = [];
$plateform_with = [];

$titles_without = [];
$plateform_without = [];

$result = xmlrpc_get_machine_with_update($kb, $updateid, $location, $start, $maxperpage, $filter);

$machines = $result["datas"];
$count = $result["total"];

echo "<h2>"._T("Machines with update", "updates")."</h2>";
$w = new OptimizedListInfos($machines["name"], _T("Machine Name", "updates"));
$w->disableFirstColumnActionLink();

$w->addExtraInfo($machines["os"], _T("Platform", "updates"));

$w->setItemCount($count);
$w->start = 0;
$w->end = $count;
$w->setNavBar(new AjaxNavBar($count, $filter));

$w->display();
