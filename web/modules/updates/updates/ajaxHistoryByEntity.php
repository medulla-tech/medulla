<?php

require_once("modules/xmppmaster/includes/xmlrpc.php");

global $maxperpage;
echo '<pre>';
print_r($maxperpage);
echo '</pre>';

$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : -1;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";

// $datas = xmlrpc_get_entity_history($entityid, $start, $maxperpage, $filter);
// $count = $datas["total"];
// $rows = $datas["data"];
$count = 0;
$titles = [];
$machines = [];
// Table
$n = new OptimizedListInfos( $titles, _T("Title", "xmppmaster"));
// $n->setcssIds($ids_clusters);
// //$n->setMainActionClasses($clusters['datas']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $machines, _T("Computer", "xmppmaster"));
// $n->addExtraInfo( $clusters['datas']['nb_ars'], _T("Associated relays", "xmppmaster"));
// $n->addActionItemArray($actionEditClusters);
$n->setTableHeaderPadding(0);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamformRunning"));

// $n->setParamInfo($params);
$n->start = 0;
$n->end = $count;
$n->display();