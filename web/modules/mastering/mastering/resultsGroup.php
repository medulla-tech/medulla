<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
// name is action name
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$type = (isset($_GET["type"])) ? htmlentities($_GET["type"]) : "";
$target = (isset($_GET["target"])) ? htmlentities($_GET["target"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$start = (isset($_GET["start"])) ? htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["start"])) ? htmlentities($_GET["start"]) : $maxperpage;
$filter=(isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

$params = [
    "id" => $id,
    "gid" => $gid,
    "uuid" => $uuid,
    "name" => $name,
    "type" => $type,
    "target" => $target,
    "entity" => $entity,
    "server" => $server,
    "start" => $start,
    "end" => $end,
    "filter"=>$filter,
];

if($type == "group"){
    $p = new PageGenerator(sprintf(_T("Results for action %s on group %s", 'mastering'),  $name));
}
else{
    $p = new PageGenerator(sprintf(_T("Results for action %s on new machines", 'mastering'),  $name));
}

$p->setSideMenu($sidemenu);
$p->display();

// $entitiesList = [];
// $entitiesIds = [];

// list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();


$ajax = new AjaxFilter(urlStrRedirect("mastering/mastering/ajaxResultsGroup"), "container", $params);

// $ajax->setElements($entitiesList);
// $ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>