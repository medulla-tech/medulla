<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxPendingUpdateByMachine.php

global $maxperpage;

$machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET["machineid"]) : "";
$start = (!empty($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (!empty($_GET['start'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$unselectAction = new ActionPopupItem(_T("Cancel Update", "updates"), "cancelUpdate", "delete", "", "updates", "updates");

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
    $datas[$row]["id_machine"] = $machineid;
    $row++;
}


echo '<div class="pending-updates-table">';
$n = new OptimizedListInfos($titles, _T("Name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($descriptions, _T("Description", "updates"));
$n->addExtraInfo($kbs, _T("Kb", "updates"));
$n->addExtraInfo($update_ids, _T("Update Id", "updates"));
$n->addExtraInfo($start_dates, _T("Started at", "updates"));
$n->addExtraInfo($end_dates, _T("End date", "updates"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->addActionItem($unselectAction);
$n->setEmptyState(_T("No pending updates", "updates"), _T("No updates are currently pending for this machine.", "updates"));
$n->display();
echo '</div>';
