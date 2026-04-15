<?php
global $maxperpage;

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
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

$p = new PageGenerator(sprintf(_T("Results for action %s on machine %s", 'mastering'), $name, $target));

$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mastering/mastering/ajaxResults", $params), "container");

// $ajax->setElements($entitiesList);
// $ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>