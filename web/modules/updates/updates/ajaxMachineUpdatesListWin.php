<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMachineUpdatesListWin.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (updatesAjaxDenied("detailsMachineWin")) {
    return;
}

$jid = isset($_GET['jid']) ? trim((string) $_GET['jid']) : '';
list($filter, $start, $maxperpage) = updatesListParams();

$machine = ($jid !== '') ? xmlrpc_get_windows_machine($jid) : null;
if (is_array($machine) && updatesReadFailed($machine)) {
    updatesReadFailedBox();
    return;
}
if (!is_array($machine) || empty($machine)) {
    EmptyStateBox::show(_T("Machine not found", "updates"));
    return;
}

$hostname = trim((string) ($machine['hostname'] ?? ''));
$entityId = updatesWinNumber($machine['entity_id'] ?? null);
$entity = ($entityId !== null) ? updatesEntityByUuid('UUID' . $entityId) : null;
$linux = ($machine['os'] ?? '') === 'linux';
$running = updatesWinTriState($machine['running'] ?? null) === true;
$rebootPending = updatesWinTriState($machine['reboot_pending'] ?? null) === true;
$updates = is_array($machine['updates'] ?? null) ? array_values(array_filter($machine['updates'], 'is_array')) : array();

$section = $_GET['section'] ?? '';
if (!in_array($section, array('missing', 'optional', 'history'), true) || ($linux && $section === 'optional')) {
    $section = 'missing';
}
$jsFunc = "updateSearchParam" . $section;

$kbNeedle = updatesKbNumber($filter);
$matchesTitleOrKb = function ($row) use ($filter, $kbNeedle) {
    if (mb_stripos((string) ($row['title'] ?? ''), $filter) !== false) {
        return true;
    }
    $kb = updatesKbNumber($row['kb'] ?? '');
    return $kbNeedle !== '' && $kb !== '' && strpos($kb, $kbNeedle) !== false;
};

if ($section === 'history') {
    $history = xmlrpc_get_windows_machine_history($jid);
    if (updatesReadFailed($history)) {
        updatesReadFailedBox();
        return;
    }
    $rows = is_array($history['rows'] ?? null) ? array_values(array_filter($history['rows'], 'is_array')) : array();
    if ($filter !== '') {
        $rows = array_values(array_filter($rows, $matchesTitleOrKb));
    }
    $total = count($rows);
    $detailAction = new ActionItem(_T("Detail", "xmppmaster"), "viewlogs", "display", "", "xmppmaster", "xmppmaster");
    $emptyAction = new EmptyActionItem1(_T("Detail", "xmppmaster"), "viewlogs", "displayg", "", "xmppmaster", "xmppmaster");
    $titles = array();
    $dates = array();
    $origins = array();
    $states = array();
    $actions = array();
    $uninstallActions = array();
    $params = array();
    foreach (array_slice($rows, $start, $maxperpage) as $row) {
        $fromMedulla = (($row['source'] ?? '') === 'medulla');
        $titles[] = htmlspecialchars((string) ($row['title'] ?? ''), ENT_QUOTES, 'UTF-8');
        $dates[] = updatesWinReportDate(substr(trim((string) ($row['date'] ?? '')), 0, 16));
        $origins[] = htmlspecialchars($fromMedulla ? "Medulla" : _T("Workstation", "updates"), ENT_QUOTES, 'UTF-8');
        $states[] = $fromMedulla ? updatesDeployStateBadge($row['state'] ?? '', $row['failure'] ?? '')
            : htmlspecialchars(_T("Installed", "updates"), ENT_QUOTES, 'UTF-8');
        $actions[] = $fromMedulla ? $detailAction : $emptyAction;
        $removable = !empty($row['removable']) && ctype_digit((string) ($row['kb'] ?? ''));
        $uninstallActions[] = updatesWinUninstallAction($removable, $running);
        $rowParams = $fromMedulla ? updatesDeployLogParams($row) : array();
        if ($removable) {
            $rowParams = array('kb' => (string) $row['kb'], 'jid' => $jid, 'hostname' => $hostname) + $rowParams;
            unset($rowParams['reinstalled']);
            if (!empty($row['reinstalled'])) {
                $rowParams['reinstalled'] = '1';
            }
        }
        $params[] = $rowParams;
    }
    $n = new OptimizedListInfos($titles, _T("Update", "updates"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfoRaw($dates, _T("Date", "updates"));
    $n->addExtraInfoRaw($origins, _T("Origin", "updates"));
    $n->addExtraInfoRaw($states, _T("Status", "updates"));
    $n->addActionItemArray($actions);
    if (!$linux) {
        $n->addActionItemArray($uninstallActions);
    }
    if ($filter !== '') {
        $n->setEmptyState(_T("No updates found", "updates"), _T("No update matches the search.", "updates"));
    } else {
        $n->setEmptyState(_T("No deployment history", "updates"));
    }
    $n->setParamInfo($params);
    $n->start = 0;
    $n->end = $total;
    $n->setItemCount($total);
    $n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES), $jsFunc));
    $n->display();
    updatesWinTooltips();
    return;
}

if (!$linux) {
    $updates = updatesWinSectionRows($updates, $section);
}
if ($filter !== '') {
    $updates = array_values(array_filter($updates, function ($update) use ($linux, $filter, $matchesTitleOrKb) {
        if ($linux) {
            return mb_stripos((string) ($update['package_name'] ?? ''), $filter) !== false;
        }
        return $matchesTitleOrKb($update);
    }));
}
$total = count($updates);
$updates = array_slice($updates, $start, $maxperpage);

$classifications = array();
foreach ($updates as $update) {
    $classification = trim((string) ($update['classification'] ?? ''));
    $classifications[] = ($classification !== '') ? updatesCatalogLabel($classification) : '<span class="cell-empty">-</span>';
}

if ($linux) {
    $packages = array();
    $installedVersions = array();
    $availableVersions = array();
    $severities = array();
    $actions = array();
    $params = array();
    foreach ($updates as $update) {
        $approved = updatesWinTriState($update['approved'] ?? null) === true;
        $packageName = trim((string) ($update['package_name'] ?? ''));
        if (!$entity) {
            $blocker = _T("Unknown entity", "updates");
        } elseif ($running) {
            $blocker = _T("Deployment in progress", "updates");
        } elseif (!$approved) {
            $blocker = _T("Not approved for this entity", "updates");
        } elseif ($packageName === '') {
            $blocker = _T("Deploy", "updates");
        } else {
            $blocker = '';
        }
        $actions[] = updatesWinDeployAction($blocker);
        $params[] = array('jid' => $jid, 'hostname' => $hostname, 'os' => 'linux', 'package' => $packageName);
        $packages[] = updatesLinuxTextCell($update['package_name'] ?? '');
        $installedVersions[] = updatesLinuxTextCell($update['installed_version'] ?? '');
        $availableVersions[] = updatesLinuxTextCell($update['available_version'] ?? '');
        $severities[] = updatesWinSeverityCell($update['severity'] ?? '');
    }
    $n = new OptimizedListInfos($packages, _T("Package", "updates"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfoRaw($installedVersions, _T("Installed version", "updates"));
    $n->addExtraInfoRaw($availableVersions, _T("Available version", "updates"));
    $n->addExtraInfoRaw($classifications, _T("Classification", "updates"));
    $n->addExtraInfoRaw($severities, _T("Severity", "updates"));
    if ($filter !== '') {
        $n->setEmptyState(_T("No package found", "updates"), _T("No package matches the search.", "updates"));
    }
} else {
    $kbs = array();
    $titles = array();
    $sizes = array();
    $risks = array();
    $actions = array();
    $params = array();
    foreach ($updates as $update) {
        $kb = (string) ($update['kb'] ?? '');
        $kbs[] = updatesKbCell($kb, ($section === 'optional') ? '' : updatesWinOfferIcon($update));
        $titles[] = updatesTitleCell($update['title'] ?? '', $kb);
        $sizes[] = updatesSizeCell($update['size'] ?? null);
        $risks[] = updatesWinRiskCell($update['severity'] ?? '', $update['exploited'] ?? null);

        $updateId = updatesApprovalId($update['update_id'] ?? null);
        $package = is_array($update['package'] ?? null) ? $update['package'] : array();
        if (!$entity) {
            $blocker = _T("Unknown entity", "updates");
        } elseif ($running) {
            $blocker = _T("Deployment in progress", "updates");
        } elseif ($rebootPending) {
            $blocker = _T("Reboot pending", "updates");
        } elseif ($updateId === null) {
            $blocker = _T("Not in the updates catalog", "updates");
        } elseif (updatesWinTriState($update['approved'] ?? null) === false) {
            $blocker = _T("Not approved for this entity", "updates");
        } else {
            $blocker = updatesWinPackageBlocker($package['state'] ?? '', $package['error'] ?? '');
            if ($blocker === '' && updatesWinTriState($update['deployed_pending_report'] ?? null) === true) {
                $blocker = _T("Installed, waiting for the machine report", "updates");
            }
        }
        $actions[] = (updatesWinOffer($update) === 'esu') ? updatesWinEsuAction() : updatesWinDeployAction($blocker);
        $params[] = array(
            'updateid' => (string) $updateId,
            'kb'       => $kb,
            'title'    => (string) ($update['title'] ?? ''),
            'location' => $entity ? $entity['uuid'] : '',
            'jid'      => $jid,
            'hostname' => $hostname,
        );
    }
    $n = new OptimizedListInfos($kbs, _T("KB", "updates"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfoRaw($titles, _T("Title", "updates"));
    $n->addExtraInfoRaw($classifications, _T("Classification", "updates"));
    $n->addExtraInfoRaw($sizes, _T("Size", "updates"));
    $n->addExtraInfoRaw($risks, _T("Update Severity", "updates"));
    if ($filter !== '') {
        $n->setEmptyState(_T("No updates found", "updates"), _T("No update matches the search.", "updates"));
    }
}
if ($filter === '') {
    $signals = is_array($machine['signals'] ?? null) ? array_map('strval', $machine['signals']) : array();
    $n->setEmptyState(in_array('search_failed', $signals, true) ? _T("Search failed", "updates") : _T("No update pending", "updates"));
}
$n->addActionItemArray($actions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES), $jsFunc));
$n->setTableCssClass("updates-machine-updates");
$n->display();
updatesWinTooltips();
