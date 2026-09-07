<?php

require_once("modules/mastering/includes/xmlrpc.php");

$mode = "";

$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$name = (isset($_GET["name"])) ? $_GET["name"] : "";
$target = (isset($_GET["target"])) ? $_GET["target"] : "";
$description = (isset($_GET["description"])) ? $_GET["description"] : "";

if($_POST != []){
    if(isset($_POST["uuid"], $_POST["name"], $_POST["description"])){

        $tmpUuid = $_POST["uuid"];
        $tmpName = $_POST["name"];
        $tmpDesc = $_POST["description"];
        if($tmpName == ""){
                new NotifyWidgetFailure(_T("Master name can't be empty", "mastering"));
        }
        else if($tmpUuid == ""){
                new NotifyWidgetFailure(_T("Wrong target", "mastering"));
        }
        else{
            $result = xmlrpc_edit_master_infos($tmpUuid, $tmpName, $tmpDesc);

            if($result["status"] == 0){
                new NotifyWidgetSuccess(htmlentities($result["msg"]));
            }
            else{
                new NotifyWidgetFailure(htmlentities($result["msg"]));
            }
            header("location:".urlStrRedirect("mastering/mastering/masters"));
        }
    }
    header("location:".urlStrRedirect("mastering/mastering/masters"));
    exit;
}

// Rules:
// - no uuid || no entity = no master selected

$p = new PageGenerator(sprintf(_T("Edit Master %s", "mastering"), htmlentities($name)));
$p->display();

$f = new ValidatingForm(["action"=>urlStrRedirect("mastering/mastering/editMaster")]);
$f->push(new Table());


$f->add(new TrFormElement(_T("Master Name", "mastering"), new InputTpl("name")), ["placeholder"=>_T("Master Name", "mastering"), "value" => htmlentities($name)]);
$f->add(new TrFormElement(_T("Description", "mastering"), new InputTpl("description")), ["placeholder"=>_T("Description", "mastering"), "value" => htmlentities($description)]);
$f->pop();

$f->add(new HiddenTpl("server"), ["value"=>$server, "hide"=>true]);
$f->add(new HiddenTpl("entity"), ["value"=>$entity, "hide"=>true]);
$f->add(new HiddenTpl("uuid"), ["value"=>$uuid, "hide"=>true]);
$f->pop();
$f->addValidateButton(_T("Confirm", "mastering"));

$f->display();
?>
