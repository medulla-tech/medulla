<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

// Actions list for entity

$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET['uuid']) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$entity = (isset($_GET["entity"])) ? $_GET["entity"] : "";
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";
$target = (isset($_GET["target"])) ? htmlentities($_GET["target"]) : "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";

$p = new PageGenerator(sprintf(_T("Actions on Machine %s", 'mastering'), $target));

$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();

$params = [
    "uuid" => $uuid,
    "gid" => $gid,
    "entity" => $entity,
    "server" => $server,
    "target" => $target
];

$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxActionListMachine", $params), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>
