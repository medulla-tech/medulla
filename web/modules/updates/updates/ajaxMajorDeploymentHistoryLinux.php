<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorDeploymentHistoryLinux.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$distribution = !empty($_GET['distribution']) ? strtolower(trim((string) $_GET['distribution'])) : "linux";
$hasEntity = isset($_GET['entity_id']) || isset($_GET['entity']);
$entityId = isset($_GET['entity_id']) ? (int) $_GET['entity_id'] : (isset($_GET['entity']) ? (int) $_GET['entity'] : -1);
$filter = isset($_GET['filter']) ? (string) $_GET['filter'] : "";

if (!$hasEntity || $entityId < 0) {
    echo '<div class="error">' . _T("Missing entity for Linux major deployment history.", "updates") . '</div>';
    return;
}

global $maxperpage;
$start = (isset($_GET['start']) && is_numeric($_GET['start'])) ? (int) $_GET['start'] : 0;
$limit = (isset($maxperpage) && is_numeric($maxperpage)) ? (int) $maxperpage : 50;
$end = (isset($_GET['end']) && is_numeric($_GET['end'])) ? (int) $_GET['end'] : ($start + $limit - 1);

$result = xmlrpc_get_linux_major_deployment_history_by_entity($distribution, $entityId, $start, $limit, $filter);
if (!is_array($result)) {
    $result = array();
}
$datas = isset($result['datas']) && is_array($result['datas']) ? $result['datas'] : array();
$count = isset($result['count']) ? (int) $result['count'] : count($datas);

$detailAction = new ActionItem(
    _T("View deployment details", "xmppmaster"),
    "viewlogs",
    "audit",
    "computer",
    "xmppmaster",
    "xmppmaster"
);

$titles = array();
$machines = array();
$users = array();
$startcmds = array();
$states = array();
$detailActions = array();
$params = array();

foreach ($datas as $deploy) {
    $title = isset($deploy['title']) ? (string) $deploy['title'] : "";
    $hostname = isset($deploy['hostname']) ? (string) $deploy['hostname'] : "";
    $rawStatus = isset($deploy['state']) ? (string) $deploy['state'] : "";

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

    $titles[] = $title;
    $machines[] = $hostname;
    $users[] = isset($deploy['login']) ? (string) $deploy['login'] : "";
    $startcmds[] = isset($deploy['startcmd']) ? (string) $deploy['startcmd'] : "";
    $states[] = '<span class="status-badge ' . $badgeClass . '">' . htmlspecialchars($rawStatus) . '</span>';
    $detailActions[] = $detailAction;

    $params[] = array(
        'uuid' => isset($deploy['uuid']) ? $deploy['uuid'] : '',
        'hostname' => $hostname,
        'gid' => isset($deploy['gid']) ? $deploy['gid'] : (isset($deploy['grp_id']) ? $deploy['grp_id'] : ''),
        'cmd_id' => isset($deploy['cmd_id']) ? $deploy['cmd_id'] : '',
        'login' => isset($deploy['login']) ? $deploy['login'] : '',
        'title' => $title,
        'start' => isset($deploy['start']) ? $deploy['start'] : '',
        'endcmd' => isset($deploy['endcmd']) ? $deploy['endcmd'] : '',
        'startcmd' => isset($deploy['startcmd']) ? $deploy['startcmd'] : '',
        'sessionid' => isset($deploy['sessionid']) ? $deploy['sessionid'] : '',
    );
}

$n = new OptimizedListInfos($titles, _T("Deployment", "updates"));
$n->setResizable();
$n->disableFirstColumnActionLink();
$n->addExtraInfo($machines, _T("Machine", "updates"));
$n->addExtraInfo($users, _T("User", "updates"));
$n->addExtraInfo($startcmds, _T("Started at", "updates"));
$n->addExtraInfoRaw($states, _T("Status", "xmppmaster"));
$n->addActionItemArray($detailActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamMajorDeploymentHistoryLinux"));
$n->setParamInfo($params);
$n->setEmptyState(_T("No deployment history", "updates"), _T("No Linux major deployments have been recorded for this entity in the last month.", "updates"));
$n->startreal = $start;
$n->endreal = $end;
$n->start = 0;
$n->end = count($titles) - 1;

echo '<h2>' . _T("Past Linux major deployments (last month)", "updates") . '</h2>';
echo '<div class="audit-updates-table">';
$n->display();
echo '</div>';
?>
