<?php
require_once("modules/mastering/includes/xmlrpc.php");

$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$name = (isset($_GET["name"])) ? $_GET["name"] : "";
$target = (isset($_GET["target"])) ? $_GET["target"] : "";
$id = (isset($_GET["id"])) ? $_GET["id"] : "";
$from = (isset($_GET["from"])) ? $_GET["from"] : "index";

$params = [
    "server" =>$server,
    "entity" =>$entity,
    "gid" =>$gid,
    "uuid"=>$uuid,
    "name" =>$name,
    "target" =>$target,
];
if($_POST["bconfirm"]){
    $ret = xmlrpc_delete_action($id);
    if($ret["status"] == 0){
        new NotifyWidgetSuccess(_T($ret["msg"], "mastering"));
    }
    else{
        new NotifyWidgetFailure(_T($ret["msg"], "mastering"));
    }
    header("location:".urlStrRedirect("mastering/mastering/".$from, $params));
    exit;
}

if($uuid == "" && $gid == ""){
    $f = new PopupForm(sprintf(_T("Delete Action %s for New Machines", "mastering"), $name));
}
else{
    $f = new PopupForm(sprintf(_T("Delete Action %s for %s", "mastering"), $name, $target));
}

$f->setLevel('danger');
$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");

$f->display();
?>
