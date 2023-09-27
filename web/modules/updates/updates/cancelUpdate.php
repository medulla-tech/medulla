<?php
require_once("modules/xmppmaster/includes/xmlrpc.php");
$idmachine = (!empty($_GET['id_machine'])) ? htmlentities($_GET['id_machine']) : 0;
$updateid = (!empty($_GET['update_id'])) ? htmlentities($_GET['update_id']) : "";

if(!empty($_POST['bcancelupdate'])){

    $result = xmlrpc_cancel_update($idmachine, $updateid);
    $result = true;
    if($result){
        new NotifyWidgetSuccess(sprintf(_T("The update %s has been removed from pending", "updates"), $updateid));
    }
    else{
        new NotifyWidgetFailure(sprintf(_T("A problem occurs, impossible to remove %s from pending", "updates"), $updateid));
    }
    header("location: ".urlStrRedirect("updates/updates/index"));
    exit;
}

$f = new PopupForm(_("Cancel pending update"));
$f->addText(sprintf(_("You will cancel update <b>%s</b>."),$updateid));
$f->addValidateButton("bcancelupdate");
$f->addCancelButton("bback");
$f->display();
?>
