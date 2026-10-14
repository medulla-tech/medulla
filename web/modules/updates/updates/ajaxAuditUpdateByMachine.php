<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxAuditUpdateByMachine.php

global $maxperpage;

$machineidglpi =  (!empty($_GET['uuid_inventorymachine'])) ? htmlentities($_GET['uuid_inventorymachine']) : 0;
$machineidmajor =  (!empty($_GET['machineidmajor'])) ? htmlentities($_GET['machineidmajor']) : 0;
$hostname = (!empty($_GET['cn'])) ? htmlentities($_GET['cn']) : "";
$machineid = (!empty($_GET['machineid'])) ? htmlentities($_GET['machineid']) : $machineidmajor;
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
    $rawStatus = $deploy["state"];
    if (preg_match('#success#i', $rawStatus)) {
        $badgeClass = 'status-badge-success';
    } elseif (preg_match('#^abort#i', $rawStatus)) {
        $badgeClass = 'status-badge-abort';
    } elseif (preg_match('#^error#i', $rawStatus)) {
        $badgeClass = 'status-badge-error';
    } elseif (preg_match('#pending#i', $rawStatus)) {
        $badgeClass = 'status-badge-pending';
    } elseif (preg_match('#start#i', $rawStatus)) {
        $badgeClass = 'status-badge-start';
    } else {
        $badgeClass = 'status-badge-other';
    }
    $states[] = '<span class="status-badge ' . $badgeClass . '">' . htmlspecialchars($rawStatus) . '</span>';
    $startcmds[] = $deploy["startcmd"];
    $detailActions[] = $detailAction;
    $datas[$key]['hostname'] = $hostname;
}

$n = new OptimizedListInfos($titles, _T("Name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($startcmds, _T("Started at", "updates"));

$n->addExtraInfoRaw($states, _T("Status", "xmppmaster"));
$n->addActionItemArray($detailActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->setEmptyState(_T("No deployment history", "updates"), _T("No update deployments have been recorded yet.", "updates"));
echo '<div class="audit-updates-table">';
$n->display();
echo '</div>';
