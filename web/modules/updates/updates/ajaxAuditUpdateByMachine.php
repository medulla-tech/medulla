<?php
/*
 * (c) 2023 Siveo, http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

global $maxperpage;

$machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET['machineid']) : 0;
$start = (!empty($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (!empty($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

// Get status log
$result = xmlrpc_get_audit_summary_updates_by_machine($machineid, $start, $end, $filter);
$datas = $result["datas"];
$count = $result["count"];

$titles = [];
$states = [];
$startcmds = [];
foreach($datas as $deploy){
    $titles[] = $deploy["title"];
    $states[] = $deploy["state"];
    $startcmds[] = $deploy["startcmd"];
}

$n = new OptimizedListInfos($titles, _T("Title", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($startcmds, _T("Started at", "updates"));

$n->addExtraInfo($states, _T("Status", "xmppmaster"));
// $n->addExtraInfo($missingUpdatesMachine, _T("Missing updates", "updates"));
// $n->addActionItemArray($detailsByMachs);
// $n->addActionItemArray($actionPendingByMachines);
// $n->addActionItemArray($actionDoneByMachines);

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->display();
?>