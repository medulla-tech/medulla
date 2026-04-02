<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET['uuid']) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

// param is used to forward $_GET parameters from the previous to the next page.
$params = [
    "uuid" => $uuid,
    "gid" => $gid,
    "name" => $name,
    "filter"=> $filter,
];

if($name == "N/P" && $uuid != "" && $gid ==""){
    $p = new PageGenerator(_T("Detail on actions for New Machine", 'mastering'));
    $params["type"] = "new";
}
else if($uuid != "" && $name != "N/P" && $gid == ""){
    $p = new PageGenerator(sprintf(_T("Detail on actions for machine %s", 'mastering'), $name) );
    $params["type"] = "machine";

}
else if($uuid == "" && $gid != "" && $name != ""){
    $p = new PageGenerator(sprintf(_T("Detail on actions for group %s", 'mastering'), $name) );
    $params["type"] = "group";
}
else{
    $p = new PageGenerator(_T("Detail on actions on Entity", 'mastering'));
    $params["type"] = "all";

}

$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();



$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxActionList", $params), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>