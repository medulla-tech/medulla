<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMachinesListWin.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$entity = updatesSelectedEntity();
$system = updatesStatusSystem($_GET['system'] ?? '');
$linux = ($system === 'linux');
if (updatesAjaxDenied("EntityComplianceos", $linux ? "tablinux" : "tabwin")) {
    return;
}
$distribution = $linux ? updatesStatusDistribution($_GET['distribution'] ?? '') : '';
list($filter, $start, $maxperpage) = updatesListParams();

$total = 0;
$rows = array();
$result = xmlrpc_get_windows_machines($entity ? array(updatesEntityId($entity)) : array(),
                                      $start, $maxperpage, $filter, $system, $distribution);
if (updatesReadFailed($result)) {
    updatesReadFailedBox();
    return;
}
if (is_array($result['rows'] ?? null)) {
    $total = intval($result['total'] ?? 0);
    $rows = array_values(array_filter($result['rows'], 'is_array'));
}

$details = new ActionItem(_T("Details", "updates"), "detailsMachineWin", "display", "", "updates", "updates");
$listParams = array('from' => 'list');
if ($entity) {
    $details->staticParams = array('location' => $entity['uuid']);
    $listParams['location'] = $entity['uuid'];
}
if ($distribution !== '') {
    $listParams['distribution'] = $distribution;
}
$restartParams = $listParams + ($linux ? array('tab' => 'tablinux') : array());

$hostnames = array();
$entities = array();
$systems = array();
$missing = array();
$critical = array();
$statuses = array();
$reports = array();
$actions = array();
$deployActions = array();
$restartActions = array();
$params = array();
$presences = array();
foreach ($rows as $row) {
    $jid = (string) ($row['jid'] ?? '');
    if ($jid === '') {
        continue;
    }
    $hostname = (string) ($row['hostname'] ?? '');
    $evaluated = updatesWinTriState($row['evaluated'] ?? null) === true;
    $reported = trim((string) ($row['received_at'] ?? '')) !== '';
    $hostnames[] = htmlspecialchars(($hostname !== '') ? $hostname : $jid, ENT_QUOTES, 'UTF-8');
    $entityName = htmlspecialchars((string) ($row['entity_name'] ?? ''), ENT_QUOTES, 'UTF-8');
    $entities[] = '<span class="cell-text" title="' . $entityName . '">' . $entityName . '</span>';
    $system = trim((string) ($row['system'] ?? ''));
    $systems[] = ($system !== '') ? htmlspecialchars($system, ENT_QUOTES, 'UTF-8') : '<span class="cell-empty">-</span>';
    $untracked = updatesWinTriState($row['untracked_version'] ?? null) === true;
    $searchFailed = updatesWinTriState($row['search_failed'] ?? null) === true;
    // Nothing to count on a machine that never reported or runs an untracked version;
    // zero after a failed search proves nothing.
    $counted = ($evaluated || $reported) && !$untracked
        && !($searchFailed && (int) updatesWinNumber($row['missing'] ?? null) === 0);
    $missing[] = $counted ? updatesWinCount($row['missing'] ?? null) : '<span class="cell-empty">-</span>';
    $critical[] = $counted ? updatesWinCount($row['critical'] ?? null, 'critical') : '<span class="cell-empty">-</span>';
    if (updatesWinTriState($row['no_report'] ?? null) === true) {
        $statuses[] = updatesWinBadge(_T("No report received", "updates"), 'none');
    } else {
        $statuses[] = updatesWinMachineStatus($row['unsupported'] ?? null, $row['evaluated'] ?? null,
                                              $row['untracked_version'] ?? null, $row['reboot_pending'] ?? null,
                                              $linux ? 'linux' : 'windows', $row['missing'] ?? null, $row['search_failed'] ?? null,
                                              $row['updating'] ?? null, $row['restart_requested'] ?? null);
    }
    $reports[] = updatesWinReportDate($row['received_at'] ?? '');
    $actions[] = $details;
    $params[] = array('jid' => $jid);
    $online = updatesWinTriState($row['online'] ?? null) === true;
    $presences[] = $online ? "machineNamepresente" : "machineName";
    // Memes conditions que le badge Reboot pending de updatesWinMachineStatus.
    $rebootShown = updatesWinTriState($row['no_report'] ?? null) !== true && !$searchFailed && $evaluated
        && updatesWinTriState($row['updating'] ?? null) !== true
        && updatesWinTriState($row['reboot_pending'] ?? null) === true;
    $restartActions[] = updatesRestartAction($restartParams, $rebootShown, $online,
                                             updatesWinTriState($row['restart_requested'] ?? null) === true);
    if ($linux) {
        $approved = (int) updatesWinNumber($row['approved'] ?? null);
        if (!updatesEntityByUuid('UUID' . (int) updatesWinNumber($row['entity_id'] ?? null))) {
            $blocker = _T("Unknown entity", "updates");
        } elseif (updatesWinTriState($row['running'] ?? null) === true) {
            $blocker = _T("Deployment in progress", "updates");
        } elseif ($approved === 0) {
            $blocker = _T("No approved package", "updates");
        } elseif (!$online) {
            $blocker = _T("Machine offline", "updates");
        } else {
            $blocker = '';
        }
        $deployAction = updatesWinDeployAction($blocker);
        // Sur l'action seule : le lien vers la fiche garde son URL.
        $deployAction->staticParams = updatesLinuxDeployParams($jid, $hostname, $approved) + $listParams;
        $deployActions[] = $deployAction;
    }
}

$n = new OptimizedListInfos($hostnames, _T("Machine", "updates"));
$n->addExtraInfoRaw($entities, _T("Entity", "updates"));
$n->addExtraInfoRaw($systems, _T("System", "updates"));
$n->addExtraInfoCenteredRaw($missing, _T("Missing", "updates"), "",
    _T("Updates not installed on the machine.", "updates"));
$n->addExtraInfoCenteredRaw($critical, _T("Critical updates", "updates"), "",
    $linux ? _T("Updates rated Critical by the distribution", "updates")
           : _T("Updates rated Critical by Microsoft, or fixing an exploited vulnerability", "updates"));
$n->addExtraInfoRaw($statuses, _T("Status", "updates"));
$n->addExtraInfoRaw($reports, _T("Last report", "updates"));
$n->addActionItemArray($actions);
if ($linux) {
    $n->addActionItemArray($deployActions);
}
$n->addActionItemArray($restartActions);
$n->setParamInfo($params);
$n->setMainActionClasses($presences);
$n->start = 0;
$n->end = $total;
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, htmlspecialchars(addslashes($filter), ENT_QUOTES)));
updatesMachinesEmptyState($n, $filter, $linux ? _T("No Linux machines", "updates") : _T("No Windows machines", "updates"));
$n->display();
?>
