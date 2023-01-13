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
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;
$entityId = htmlentities($_GET['entity']);
$entityCompleteName = htmlentities($_GET['completename']);
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

// $updates_list = xmlrpc_get_white_list($start, $end, $filter);
$updates_list = xmlrpc_get_updates_by_entity($entityId, $start, $end, $filter);

$deployThisUpdate = new ActionItem(_T(sprintf("Deploy this update on entity %s", $entityCompleteName), "updates"),"deployUpdate","quick","", "updates", "updates");


$params = [];
$names_updates = [];
$actionspeclistUpds = [];

$count = $updates_list['total'];
$updates_list = $updates_list['datas'];

$row = 0;

foreach ($updates_list['title'] as $update) {
    $actionspeclistUpds[] = $deployThisUpdate;
    $names_updates[] = $update;
    $params[] = [
        "pid" => $updates_list["updateid"][$row],
        "kb" => $updates_list["kb"][$row],
        "entity"=> $entityId,
    ];
    $row++;
}

$n = new OptimizedListInfos($names_updates, _T("Update name", "updates"));
$n->disableFirstColumnActionLink();
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($params);

echo '<h2>';
echo _T(sprintf("Updates on Entity %s", $entityCompleteName), "updates");
echo '</h2>';

$n->addActionItemArray($actionspeclistUpds);

$n->display();
?>
