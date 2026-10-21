<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxDeployWinGroup.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$group = hasCorrectAcl("updates", "updates", "deployWinGroup") ? updatesWinRequestGroup() : null;
if (!$group) {
    EmptyStateBox::show(_T("Unknown group.", "updates"));
    return;
}

list($filter, $start, $maxperpage) = updatesListParams();

if (($_GET['os'] ?? '') === 'linux') {
    $result = xmlrpc_get_linux_group_packages($group['id'], $start, $maxperpage, $filter);
    if (updatesReadFailed($result)) {
        updatesReadFailedBox();
        return;
    }
    $total = intval($result['total'] ?? 0);
    $packages = array();
    $severities = array();
    $machines = array();
    $hasSeverity = false;
    foreach ((is_array($result['rows'] ?? null) ? array_filter($result['rows'], 'is_array') : array()) as $row) {
        $packages[] = updatesLinuxTextCell($row['package'] ?? '');
        $severities[] = updatesWinRiskCell($row['severity'] ?? '', null);
        $machines[] = updatesWinCount($row['machines'] ?? null);
        $hasSeverity = $hasSeverity || trim((string) ($row['severity'] ?? '')) !== '';
    }
    $n = new OptimizedListInfos($packages, _T("Package", "updates"));
    $n->setTableCssClass("updates-approval");
    $n->disableFirstColumnActionLink();
    if ($hasSeverity) {
        $n->addExtraInfoRaw($severities, _T("Severity", "updates"));
    }
    $n->addExtraInfoCenteredRaw($machines, _T("Machines", "updates"), "",
        _T("Machines of the group missing this update.", "updates"));
    $n->start = 0;
    $n->end = $total;
    $n->setItemCount($total);
    $n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES), "updateSearchParamLinuxPackages"));
    if ($filter !== '') {
        $n->setEmptyState(_T("No package found", "updates"), _T("No package matches the search.", "updates"));
    } else {
        $n->setEmptyState(_T("No approved package", "updates"));
    }
    $n->display();
    return;
}

$result = xmlrpc_get_windows_group_updates($group['id']);
if (updatesReadFailed($result)) {
    updatesReadFailedBox();
    return;
}
$groupMachines = updatesWinNumber($result['machines'] ?? null);

$rows = array();
foreach ((is_array($result['rows'] ?? null) ? $result['rows'] : array()) as $row) {
    if (!is_array($row) || updatesApprovalId($row['update_id'] ?? null) === null) {
        continue;
    }
    if ($filter !== '' && stripos((string) ($row['kb'] ?? '') . ' ' . (string) ($row['title'] ?? ''), $filter) === false) {
        continue;
    }
    $rows[] = $row;
}
$total = count($rows);
if ($start >= $total) {
    $start = 0;
}

$kbs = array();
$titles = array();
$risks = array();
$machines = array();
$eligibles = array();
$actions = array();
$params = array();
foreach (array_slice($rows, $start, $maxperpage) as $row) {
    $kb = (string) ($row['kb'] ?? '');
    $title = (string) ($row['title'] ?? '');
    $eligible = updatesWinNumber($row['eligible'] ?? null);

    $kbs[] = updatesKbCell($kb, updatesWinOfferIcon($row));
    $titles[] = updatesTitleCell($title, $kb);
    $risks[] = updatesWinRiskCell($row['severity'] ?? '', $row['exploited'] ?? null);
    $machines[] = updatesWinCount($row['machines'] ?? null);
    $eligibles[] = updatesWinCount($row['eligible'] ?? null);
    $actions[] = (updatesWinOffer($row) === 'esu') ? updatesWinEsuAction() : updatesWinGroupDeployAction($eligible);
    $params[] = array(
        'updateid' => updatesApprovalId($row['update_id']),
        'kb'       => $kb,
        'title'    => $title,
        'gid'      => $group['id'],
        'eligible' => $eligible ?? '',
    );
}

$n = new OptimizedListInfos($kbs, _T("KB", "updates"));
$n->setTableCssClass("updates-approval");
$n->disableFirstColumnActionLink();
$n->addExtraInfoRaw($titles, _T("Title", "updates"));
$n->addExtraInfoRaw($risks, _T("Update Severity", "updates"));
$n->addExtraInfoCenteredRaw($machines, _T("Machines", "updates"), "",
    _T("Machines of the group missing this update.", "updates"));
$n->addExtraInfoCenteredRaw($eligibles, _T("Eligible", "updates"), "",
    _T("Machines that can receive it now.", "updates"));
$n->addActionItemArray($actions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES)));
if ($filter !== '') {
    $n->setEmptyState(_T("No updates found", "updates"), _T("No update matches the search.", "updates"));
} elseif ($groupMachines === 0) {
    $n->setEmptyState(_T("No Windows machine in this group", "updates"));
} else {
    $n->setEmptyState(_T("No update missing", "updates"),
                      _T("The Windows machines of this group have every update of their tracked products.", "updates"));
}
$n->display();
updatesWinTooltips();
?>
