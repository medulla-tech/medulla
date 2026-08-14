<?php
/*
 * (c) 2026 Medulla, http://medulla-tech.io
 *
 * $Id$
 *
 * This file is part of Pulse.
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

require_once("modules/urbackup/includes/xmlrpc.php");
require_once("modules/urbackup/includes/functions.inc.php");

global $maxperpage;

$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$start = (isset($_GET["start"])) ? htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"])) ? htmlentities($_GET["end"]) : $maxperpage;
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

$logs_global = xmlrpc_get_logs_for_entity($entity, $start, $maxperpage, $filter);

echo '<p .class="color-red">Update and gather the logs can take a while...</p>';
$count = $logs_global["total"];
$logs = $logs_global['data'];

$ids = [];
$loglevels = [];
$messages = [];
$dates = [];
foreach($logs as $log){
    $ids[] = $log["id"];
    $messages[] = $log["msg"];
    $dates[] = date('Y-m-d H:i:s', $log["time"]);
    $loglevels[] = $log["loglevel"];
}

$n = new OptimizedListInfos( $ids, _T("Ids", "urbackup"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($loglevels, _T("LogLevels", 'urbackup'));
$n->addExtraInfo($messages, _T("Messages", 'urbackup'));
$n->addExtraInfo($dates, _T("Dates", 'urbackup'));
// $n->setParamInfo($_params);
// $n->addActionItemArray($displayActions);
// $n->addActionItemArray($deleteActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();
?>

