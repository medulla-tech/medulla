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


$p = new PageGenerator(_T("Actions on Entity", 'mastering'));

$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();

$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxActionList"), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>