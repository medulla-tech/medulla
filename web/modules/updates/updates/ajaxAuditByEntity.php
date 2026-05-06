<?php

require_once("modules/xmppmaster/includes/xmlrpc.php");

global $maxperpage;
$entityuuid = (isset($_GET['entity'])) ? htmlentities($_GET['entity']) : "UUID0";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";


$result = xmlrpc_get_audit_summary_updates_by_entity($entityuuid, $start, $maxperpage, $filter);

$datas = $result["datas"];
$count = $result["count"];

$detailAction = new ActionItem(_T("Detail", "xmppmaster"), "viewlogs", "display", "", "xmppmaster", "xmppmaster");
$titles = [];
$states = [];
$startcmds = [];
$detailActions = [];
$hostnames = [];
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
    $hostnames[] = $deploy["hostname"];
    $detailActions[] = $detailAction;
    $datas[$key]['hostname'] = $hostname;
}

$n = new OptimizedListInfos($titles, _T("Name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($hostnames, _T("Machine", "updates"));
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