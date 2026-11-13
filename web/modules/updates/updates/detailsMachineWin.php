<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/detailsMachineWin.php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");
require_once("modules/base/includes/computers_list.inc.php");

$sidemenu->forceActiveItem("index");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Machine", "updates"), $sidemenu);
    return;
}

$jid = isset($_GET['jid']) ? trim((string) $_GET['jid']) : '';
$machine = ($jid !== '') ? xmlrpc_get_windows_machine($jid) : null;
$readFailed = is_array($machine) && updatesReadFailed($machine);
if ($readFailed || !is_array($machine) || empty($machine)) {
    $machine = null;
}

$hostname = $machine ? trim((string) ($machine['hostname'] ?? '')) : '';
$p = new PageGenerator(htmlspecialchars(($hostname !== '') ? $hostname : _T("Machine", "updates"), ENT_QUOTES, 'UTF-8'));
$p->setSideMenu($sidemenu);
$p->display();
updatesStaleNotice();

$entityId = $machine ? updatesWinNumber($machine['entity_id'] ?? null) : null;
$entity = ($entityId !== null) ? updatesEntityByUuid('UUID' . $entityId) : null;
$linux = $machine && ($machine['os'] ?? '') === 'linux';
$backParams = array();
$listEntity = updatesSelectedEntity();
if ($listEntity) {
    $backParams['location'] = $listEntity['uuid'];
}
if ($linux) {
    $backParams['tab'] = 'tablinux';
}
echo '<a class="updates-back-link" href="' . htmlspecialchars(urlStrRedirect("updates/updates/EntityComplianceos", $backParams)) . '">&larr; '
    . htmlspecialchars($entity ? _T("Back to machines", "updates") : _T("Back", "updates")) . '</a>';

if ($readFailed) {
    updatesReadFailedBox();
    return;
}

if (!$machine) {
    EmptyStateBox::show(_T("Machine not found", "updates"));
    return;
}

if (updatesWinTriState($machine['no_report'] ?? null) === true) {
    EmptyStateBox::show(_T("No report received", "updates"),
        _T("The Medulla agent of this machine has not sent any updates report yet.", "updates"));
    return;
}

$evaluated = updatesWinTriState($machine['evaluated'] ?? null) === true;
$signals = is_array($machine['signals'] ?? null) ? array_map('strval', $machine['signals']) : array();
$rebootPending = in_array('reboot_pending', $signals, true) && updatesWinTriState($machine['running'] ?? null) !== true;
$restartRequested = $rebootPending && updatesWinTriState($machine['restart_requested'] ?? null) === true;
$updates = is_array($machine['updates'] ?? null) ? array_values(array_filter($machine['updates'], 'is_array')) : array();
$searchFailed = in_array('search_failed', $signals, true);
$unsupported = in_array('unsupported', $signals, true);
$noProduct = !$linux && $entityId !== null && updatesWinNumber($machine['tracked_products'] ?? null) === 0;
$untracked = !$linux && !$noProduct && in_array('untracked_version', $signals, true);
$missing = $linux ? $updates : updatesWinSectionRows($updates, 'missing');
$optional = $linux ? array() : updatesWinSectionRows($updates, 'optional');
if (empty($missing) && $unsupported && !$noProduct && !$untracked) {
    $signals = array_values(array_diff($signals, array('unsupported')));
}

$fields = array();
if ($entity) {
    $fields[_T("Entity", "updates")] = htmlspecialchars(updatesEntityName($entity), ENT_QUOTES, 'UTF-8');
}
$machineFields = $linux
    ? array('system' => _T("System", "updates"), 'kernel' => _T("Kernel", "updates"))
    : array('system' => _T("System", "updates"), 'build' => _T("Build", "updates"),
            'language' => _T("Language", "updates"));
foreach ($machineFields as $key => $label) {
    $value = trim((string) ($machine[$key] ?? ''));
    if ($value !== '') {
        $fields[$label] = htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
    }
}
$fields[_T("Last report", "updates")] = updatesWinReportDate($machine['received_at'] ?? '')
    . (!$evaluated ? ' ' . updatesWinBadge(_T("No recent report", "updates"), 'none') : '');
if ($linux) {
    $autoUpdates = updatesLinuxAutoUpdatesState($machine['windows_update'] ?? null);
    if ($autoUpdates !== null) {
        $fields[_T("Automatic updates", "updates")] = $autoUpdates;
    }
} else {
    $windowsUpdate = updatesWinUpdateState($machine['windows_update'] ?? null);
    if ($windowsUpdate !== null) {
        $fields[_T("Windows Update", "updates")] = $windowsUpdate;
    }
}
if (in_array('unsupported', $signals, true)) {
    $fields[_T("Support", "updates")] = '<strong>' . htmlspecialchars(_T("ended (no ESU)", "updates"), ENT_QUOTES, 'UTF-8') . '</strong>';
}
if ($searchFailed) {
    $fields[$linux ? _T("Search for updates", "updates") : _T("Windows search", "updates")] = '<strong>' . htmlspecialchars(_T("failed", "updates"), ENT_QUOTES, 'UTF-8') . '</strong>';
}
if ($restartRequested) {
    $fields[_T("Reboot", "updates")] = updatesWinBadge(_T("Restart requested", "updates"), 'reboot');
} elseif ($rebootPending) {
    $fields[_T("Reboot", "updates")] = '<strong>' . htmlspecialchars(_T("pending", "updates"), ENT_QUOTES, 'UTF-8') . '</strong>';
}
$history = xmlrpc_get_windows_machine_history($jid, 0, 1);
$historyFailed = updatesReadFailed($history);
$hasHistory = !$historyFailed && !empty($history['rows']);
$sections = array();
if (!$untracked && !empty($missing)) {
    $sections[] = 'missing';
}
if (!$untracked && !empty($optional)) {
    $sections[] = 'optional';
}
if ($hasHistory) {
    $sections[] = 'history';
}

echo '<div class="updates-machine-head">';
echo '<dl class="updates-machine-summary">';
foreach ($fields as $label => $html) {
    echo '<dt>' . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</dt><dd>' . $html . '</dd>';
}
echo '</dl>';
if (!empty($sections)) {
    updatesMachineSearch($jid, $sections);
}
echo '</div>';
if ($restartRequested && $entity && updatesWinCanDeploy()) {
    echo '<div class="updates-machine-actions"><button type="button" class="btnPrimary" disabled title="'
        . htmlspecialchars(_T("Restart already requested", "updates"), ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars(_T("Restart", "updates"), ENT_QUOTES, 'UTF-8') . '</button></div>';
} elseif ($rebootPending && $entity && updatesWinCanDeploy() && updatesWinTriState($machine['online'] ?? null) === true) {
    echo updatesDeployPopupButton(urlStrRedirect("updates/updates/restartMachine", array('jid' => $jid, 'from' => 'details') + $backParams),
                                  htmlspecialchars(_T("Restart", "updates"), ENT_QUOTES, 'UTF-8'));
}

if ($untracked) {
    $release = trim(str_replace(array('*', "\r", "\n"), ' ', (string) ($machine['release'] ?? '')));
    if ($release === '') {
        $release = trim(str_replace(array('*', "\r", "\n"), ' ', (string) ($machine['system'] ?? '')));
    }
    $description = ($release !== '')
        ? sprintf(_T("This entity does not track **%s**: check this version in Tracked products to evaluate it.", "updates"), $release)
        : _T("This entity does not track this Windows version: check it in Tracked products to evaluate it.", "updates");
    EmptyStateBox::show(_T("Version not tracked", "updates"), $description);
    if ($entityId !== null && hasCorrectAcl("updates", "updates", "products")) {
        echo '<p>' . updatesWinProductsLink($entityId, _T("Tracked products", "updates")) . '</p>';
    }
} elseif (empty($missing)) {
    if ($noProduct) {
        updatesWinNoProductNotice($entityId);
    } elseif ($unsupported) {
        EmptyStateBox::show(_T("No more updates for this system", "updates"),
            _T("Windows 10 is no longer supported by Microsoft: without an **ESU** license, this machine no longer receives security updates.", "updates"));
    } elseif (!$rebootPending) {
        $section = new SpanElement(htmlspecialchars(_T("Missing updates", "updates"), ENT_QUOTES, 'UTF-8'), "section-title");
        $section->display();
        $noneText = $searchFailed ? _T("Search failed", "updates")
            : ($evaluated ? _T("No update pending", "updates") : _T("No recent report", "updates"));
        echo '<p class="updates-machine-none">' . htmlspecialchars($noneText, ENT_QUOTES, 'UTF-8') . '</p>';
    }
} else {
    updatesMachineSection(_T("Missing updates", "updates"), 'missing');
    if ($linux && $entity) {
        $approvedCount = 0;
        foreach ($updates as $update) {
            if (updatesWinTriState($update['approved'] ?? null) === true) {
                $approvedCount++;
            }
        }
        echo updatesLinuxDeployButton($jid, $hostname, $approvedCount, updatesWinTriState($machine['running'] ?? null) === true);
    }
}

if (in_array('optional', $sections, true)) {
    updatesMachineSection(_T("Other available updates", "updates"), 'optional');
}

if ($hasHistory) {
    updatesMachineSection(_T("Updates history", "updates"), 'history');
} else {
    $section = new SpanElement(htmlspecialchars(_T("Updates history", "updates"), ENT_QUOTES, 'UTF-8'), "section-title");
    $section->display();
    if ($historyFailed) {
        updatesReadFailedBox();
    } else {
        EmptyStateBox::show(_T("No deployment history", "updates"));
    }
}
?>
