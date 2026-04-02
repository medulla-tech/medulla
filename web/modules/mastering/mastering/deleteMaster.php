<?php
require_once("modules/mastering/includes/xmlrpc.php");


$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";

$masterId = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : "";
$masterName = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";

if(isset($_POST["bconfirm"])){
    $result = xmlrpc_delete_master($server, $entity, $masterId);


    if(isset($result["status"]) && $result["status"] == 0){
        $msg = (isset($result["msg"])) ? $result["msg"] : sprintf(_T("Master %s successfully deleted", "mastering"), $masterName);
        new NotifyWidgetSuccess($msg);
        header("location: ".urlStrRedirect("mastering/mastering/masters"));
        exit;
    }
}


$mode = "";

$title = sprintf(_T("Delete Master %s", "mastering"), $masterName);
$p = new PageGenerator($title);
$p->display();

$f = new ValidatingForm(["title"=>$title, "action"=>urlStrRedirect("mastering/mastering/deleteMaster", $_GET)]);
$f->push(new Table());

$f->addValidateButton("bconfirm");
$f->addOnClickButton(_T("Cancel", "admin"), urlStrRedirect("mastering/mastering/masters"));

$f->display();