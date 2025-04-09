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
$machineidglpi =  (!empty($_GET['uuid_inventorymachine'])) ? htmlentities($_GET['uuid_inventorymachine']) : 0;
$machineidmajor =  (!empty($_GET['machineidmajor'])) ? htmlentities($_GET['machineidmajor']) : 0;
$hostname = (!empty($_GET['cn'])) ? htmlentities($_GET['cn']) : "";
$machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET['machineid']) : 0;
$start = (!empty($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (!empty($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

// Get status log
$result = xmlrpc_get_audit_summary_updates_by_machine($machineid, $start, $end, $filter);
$datas = $result["datas"];
$count = $result["count"];

$detailAction = new ActionItem(_T("Detail", "xmppmaster"), "viewlogs", "display", "", "xmppmaster", "xmppmaster");
$titles = [];
$states = [];
$startcmds = [];
$detailActions = [];
foreach($datas as $key=>$deploy) {
    $titles[] = $deploy["title"];
    $states[] = $deploy["state"];
    $startcmds[] = $deploy["startcmd"];
    $detailActions[] = $detailAction;
    $datas[$key]['hostname'] = $hostname;
}

$n = new OptimizedListInfos($titles, _T("Title", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($startcmds, _T("Started at", "updates"));

$n->addExtraInfo($states, _T("Status", "xmppmaster"));
$n->addActionItemArray($detailActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->display();
