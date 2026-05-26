<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

if(isset($_POST["Confirm"])){
    $newName = (isset($_POST["name"])) ? $_POST["name"] : "";
    $newDescription = (isset($_POST["description"])) ? $_POST["description"] : "";
    $newContent = (isset($_POST["content"])) ? base64_encode($_POST["content"]) : "";
    $newServer = isset($_POST["server"]) ? $_POST["server"] : "";
    $newEntity = isset($_POST["entity"]) ? $_POST["entity"] : "";

    if($newName == ""){
        new NotifyWidgetFailure(_T("The script has no name","mastering"));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
        exit;
    }
    if($newEntity == ""){
        new NotifyWidgetFailure(_T("No entity selected for this script","mastering"));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
        exit;
    }

    if($newContent == ""){
        new NotifyWidgetFailure(_T("No content found","mastering"));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
        exit;
    }


    $result = (array)xmlrpc_add_mastering_script($newServer, $newEntity, $newName, $newDescription, $newContent);

    if($result["status"] == 0){
        new NotifyWidgetSuccess(sprintf(_T("%s script added correctly", "mastering"), $newName));
    }
    else{
        new NotifyWidgetFailure(sprintf(_T("Impossible to add %s script", "mastering"), $newName));
    }
    header("location: ".urlStrRedirect("mastering/mastering/scripts"));
    exit;
}

// Actions list for entity
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET['uuid']) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$entity = (isset($_GET["entity"])) ? $_GET["entity"] : "";
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

$p = new PageGenerator(_T("New Script", 'mastering'));

$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();

$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxNewScript"), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);
$ajax->display();
$ajax->displayDivToUpdate();
?>
