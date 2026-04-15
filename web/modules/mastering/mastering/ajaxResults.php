<?php

require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;


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

$results = xmlrpc_get_action_results($id, $uuid, $start, $maxperpage, $filter);

$count = $results["total"];
$datas = $results["data"];

$contents = [];
$ids = [];
$dates = [];

// Remove ainsi codes from strings
foreach($datas as $log){
    $ids[] = $log["id"];
    $content = preg_replace("#\x1b\[.{2,5}m#", "", base64_decode($log["content"]));
    $contents[] = preg_replace("#\x1b\[(.+)\]#", "", $content);
    $dates[] = $log["creation_date"];
}

$n = new OptimizedListInfos( $dates, _T("Date", "mastering"));
$n->addExtraInfo($contents, _T("Log", "mastering"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();
