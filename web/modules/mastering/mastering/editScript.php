<?php

require_once("modules/mastering/includes/xmlrpc.php");

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

if($_POST != [] && isset($_POST["bconfirm"])){

    $ignoredKeys = ["codeToCopy", "old_", "auth_token", "bconfirm", "entity", "server", "name","description", "content"];
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
    $tmpId = (isset($_POST["id"])) ? $_POST["id"] : "";
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

    $result = xmlrpc_edit_mastering_script($tmpServer, $tmpEntity, $tmpId, $tmpName, $tmpDescription, $tmpContent, $tmpType, $payload);
    if(isset($result["status"]) && $result["status"] == 0){
        new NotifyWidgetSuccess(sprintf(_T("Script %s successfully edited", "mastering"), $tmpName));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
    }
    if(isset($result["status"]) && $result["status"] != 0){
        new NotifyWidgetFailure(sprintf(_T("Something happened during %s save. Reason : %s", "mastering"), $tmpName, $result["msg"]));
        header("location: ".urlStrRedirect("mastering/mastering/scripts"));
    }
    exit;
}
$params = $_GET;
unset($params["action"]);

$params["mode"] = "edit";

$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$params["server"] = $server;
// Get the datas from db
$datas = xmlrpc_get_mastering_script($entity, $id);
$params["parameters"] = [];

$params["id"] = $id;
$params["entity"] = $entity;
$params["server"] = $server;

if($datas != []){
$sufixPage = htmlentities($datas["payload"]["script"]);

$params["name"] = $datas["name"];

$_SESSION["parameters"]["content"] = $datas["content"];
$_SESSION["parameters"] = $datas["payload"];
$_SESSION["parameters"]["name"] = htmlentities($datas["name"]);
$_SESSION["parameters"]["description"] = htmlentities($datas["description"]);
$_SESSION["parameters"]["content"] = $datas["content"];


$ajax = new AjaxFilter(urlStrRedirect("mastering/mastering/ajaxForm".$sufixPage, $params), "container");
$ajax->display();
$ajax->displayDivToUpdate();
}
// $ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxEditScript"), "container", "entity");

// $ajax->setElements($entitiesList);
// $ajax->setElementsVal($entitiesIds);

// $ajax->display();
// $ajax->displayDivToUpdate();
?>
