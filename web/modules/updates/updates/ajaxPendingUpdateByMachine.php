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

$machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET["machineid"]) : "";
$start = (!empty($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (!empty($_GET['start'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$unselectAction = new ActionPopupItem(_T("Cancel Update", "updates"), "cancelUpdate", "delete", "", "updates", "updates");
$unselectActionEmpty = new EmptyActionItem(_T("Cancel Update", "updates"), "cancelUpdate", "delete", "", "updates", "updates");
$unselectActions = [];

// Get selected updates
$result = xmlrpc_get_tagged_updates_by_machine($machineid, $start, $end, $filter);

$count = $result["count"];
$datas = $result["datas"];

$titles = [];
$kbs = [];
$start_dates = [];
$end_dates = [];
$update_ids = [];
$descriptions = [];
$idmachines = [];
$row = 0;

foreach($datas as $update) {
    $titles[] = $update["title"];
    $kbs[] = $update["kb"];
    $update_ids[] = $update["update_id"];
    $start_dates[] = $update["start_date"];
    $end_dates[] = $update["end_date"];
    $descriptions[] = $update["description"];
    if($update['required_deploy'] == 1) {
        $unselectActions[] = $unselectAction;
    } else {
        $unselectActions[] = $unselectActionEmpty;
    }
    $datas[$row]["id_machine"] = $machineid;
    $row++;
}


$n = new OptimizedListInfos($titles, _T("Pending Updates", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($descriptions, _T("Description", "updates"));
$n->addExtraInfo($kbs, _T("Kb", "updates"));
$n->addExtraInfo($update_ids, _T("Update", "updates"));
$n->addExtraInfo($start_dates, _T("Start Date", "updates"));
$n->addExtraInfo($end_dates, _T("End Date", "updates"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->addActionItemArray($unselectActions);
$n->display();
