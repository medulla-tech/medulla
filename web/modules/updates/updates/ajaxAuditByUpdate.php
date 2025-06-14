<?php

require_once("modules/xmppmaster/includes/xmlrpc.php");

global $maxperpage;
$kb = (isset($_GET['kb'])) ? htmlentities($_GET['kb']) : "";
$updateid = (isset($_GET['kb'])) ? htmlentities($_GET['updateid']) : "";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

$result = xmlrpc_get_audit_summary_updates_by_update($updateid, $start, $maxperpage, $filter);

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
    $states[] = $deploy["state"];
    $startcmds[] = $deploy["startcmd"];
    $hostnames[] = $deploy["hostname"];
    $detailActions[] = $detailAction;
    $datas[$key]['hostname'] = $hostname;
}

$n = new OptimizedListInfos($titles, _T("Title", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($hostnames, _T("Machine", "updates"));
$n->addExtraInfo($startcmds, _T("Started at", "updates"));

$n->addExtraInfo($states, _T("Status", "xmppmaster"));
$n->addActionItemArray($detailActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->setParamInfo($datas);
$n->display();