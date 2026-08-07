<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");


// Handle locally posted form for specific cases.
if($_POST != [] && isset($_POST["bconfirm"])){

    $ignoredKeys = ["codeToCopy", "old_", "auth_token", "mode", "bconfirm", "entity", "server", "name","description", "content"];
    $ignoredKeysRegex = "";
    foreach($ignoredKeys as $k){
        $ignoredKeysRegex .= "(".$k.")|";
    }
    $ignoredKeysRegex = rtrim($ignoredKeysRegex, '|');

    $payload = [];

    foreach($_POST as $pkey=>$pval){
        if(preg_match("#".$ignoredKeysRegex."#i", $pkey)){
            continue;
        }

        $payload[$pkey] = $pval;
    }

    $tmpEntity = (isset($_POST["entity"])) ? $_POST["entity"] : "";
    $tmpServer = (isset($_POST["server"])) ? $_POST["server"] : "";
    $tmpName = (isset($_POST["name"])) ? $_POST["name"] : "";
    $tmpDescription = (isset($_POST["description"])) ? $_POST["description"] : "";
    $tmpContent = (isset($_POST["content"])) ? $_POST["content"] : "";
    $tmpType = (isset($_POST["type"])) ? $_POST["type"] : "bash";

    if($tmpEntity == "" || $tmpServer == ""){
        new NotifyWidgetFailure(_T("No entity or server selected for this script","mastering"));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
        exit;
    }

    if($tmpName == ""){
        new NotifyWidgetFailure(_T("The script has no name","mastering"));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
        exit;
    }

    $result = xmlrpc_add_mastering_script($tmpServer, $tmpEntity, $tmpName, $tmpDescription, $tmpContent, $tmpType, $payload);
    if(isset($result["status"]) && $result["status"] == 0){
        new NotifyWidgetSuccess(sprintf(_T("Script %s successfully created", "mastering"), $tmpName));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
    }
    if(isset($result["status"]) && $result["status"] != 0){
        new NotifyWidgetFailure(sprintf(_T("Something happened during %s save. Reason : %s", "mastering"), $tmpName, $result["msg"]));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
    }
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
