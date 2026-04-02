<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$type = (isset($_GET["type"])) ? htmlentities($_GET["type"]) : "";
$elementName = (isset($_GET["elementName"])) ? htmlentities($_GET["elementName"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";

$params = [
    "id" => $id,
    "gid" => $gid,
    "uuid" => $uuid,
    "name" => $name,
    "type" => $type,
    "elementName" => $elementName,
    "entity" => $entity,
    "server" => $server,
];

if($type == "machine"){
    $p = new PageGenerator(sprintf(_T("Results for action <%s> %s on machine %s", 'mastering'), $id, $name, $elementName));
}
else if($type == "group"){
    $p = new PageGenerator(sprintf(_T("Results for action <%s> %s on group %s", 'mastering'), $id, $name, $elementName));
}
else if ($type == "new"){
    $p = new PageGenerator(sprintf(_T("Results for action <%s> %s on new machine", 'mastering'), $id, $name));
}
else{
    $p = new PageGenerator(sprintf(_T("Results for action <%s> %s", 'mastering'), $id, $name));

}
$p->setSideMenu($sidemenu);
$p->display();

// $entitiesList = [];
// $entitiesIds = [];

// list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();


$ajax = new AjaxFilter(urlStrRedirect("mastering/mastering/ajaxResults"), "container", $params);

// $ajax->setElements($entitiesList);
// $ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>