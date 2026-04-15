<?php

require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

// echo '<pre>';
// print_r($_GET);
// echo '</pre>';

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$type = (isset($_GET["type"])) ? htmlentities($_GET["type"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";

$actionResult = new ActionItem(_T("Show results", "mastering"), "results", "display", "mastering", "mastering", "mastering");


$results = xmlrpc_get_machines_action_results($id, $start, $maxperpage, $filter);
// $results = xmlrpc_get_action_results($id, $uuid, $start, $maxperpage, $filter);

$count = $results["total"];
$datas = $results["data"];

$contents = [];
$uuids = [];
$session_ids = [];
$dates = [];
$params = [];
$actionResults = [];

foreach($datas as $entry){
    $uuids[] = $entry["uuid"];
    $session_ids[] = $entry["session_id"];
    // $content = preg_replace("#\x1b\[.{2,5}m#", "", base64_decode($log["content"]));
    // $contents[] = preg_replace("#\x1b\[(.+)\]#", "", $content);
    $dates[] = $entry["creation_date"];

    $p = $entry;

    $p["id"] = $id;
    $p["entity"] = $entity;
    $p["type"] = $type;
    $p["server"] = $server;

    $params[] = $p;
    $actionResults[] = $actionResult;
}

$n = new OptimizedListInfos( $uuids, _T("Machine", "mastering"));
$n->addExtraInfo($session_ids, _T("Session", "mastering"));
$n->addExtraInfo($dates, _T("dates", "mastering"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->addActionItemArray($actionResults);
$n->setParamInfo($params);

$n->end = $count;
$n->start = 0;
$n->display();
