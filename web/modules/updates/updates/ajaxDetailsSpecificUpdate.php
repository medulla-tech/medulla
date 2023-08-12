<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
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
$end   = (isset($_GET['end']) ? $_GET['start']+$maxperpage : $maxperpage);
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

$uuid = htmlspecialchars($_GET['uuid']);
$ctx['uuid'] = $uuid;

//$uuidCut = substr($uuid, -1);

$entityMachineList = xmlrpc_xmppmaster_get_machines_list($start, $end, $ctx);

$withUpd = [];
$withoutUpd = [];

$titles_with = [];
$plateform_with = [];

$titles_without = [];
$plateform_without = [];

$with_Upd = xmlrpc_get_machine_with_update($kb);
$without_Upd = xmlrpc_get_machines_needing_update($updateid);
$count_with_upd = sizeof($with_Upd[1]);
$count_without_upd = sizeof($without_Upd);

$count = $entityMachineList['count'];
for($i=0; $i < $count; $i++) {
    if (in_array($entityMachineList['data']['hostname'][$i], $with_Upd[1])) {
        $titles_with[] = $entityMachineList['data']['hostname'][$i];
        $plateform_with[] = $entityMachineList['data']['platform'][$i];
    }
}

for($i=0; $i < $count; $i++) {
    if (in_array($entityMachineList['data']['hostname'][$i], $without_Upd)) {
        $titles_without[] = $entityMachineList['data']['hostname'][$i];
        $plateform_without[] = $entityMachineList['data']['platform'][$i];
    }
}


echo "<h2>Machines without update</h2>";
$n = new OptimizedListInfos($titles_without, _T("Hostname", "updates"));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($plateform_without, _T("Platform", "updates"));

$n->setItemCount($count_with_upd);
$n->setNavBar(new AjaxNavBar($count_with_upd, $filter));

$n->display();

echo "<h2>Machines with update</h2>";
$w = new OptimizedListInfos($titles_with, _T("Hostname", "updates"));
$w->disableFirstColumnActionLink();

$w->addExtraInfo($plateform_with, _T("Platform", "updates"));

$w->setItemCount($count_without_upd);
$w->setNavBar(new AjaxNavBar($count_without_upd, $filter));

$w->display();
