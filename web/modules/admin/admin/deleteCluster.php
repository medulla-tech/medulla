<?php
require_once("modules/xmppmaster/includes/xmlrpc.php");

$id_cluster = $_GET['id'];
$cluster_name = $_GET['name'];

if (isset($_POST["bconfirm"])) {
    $result = xmlrpc_delete_cluster($id_cluster);
    if($result['state'] == 'success'){
        new NotifyWidgetSuccess(_T("The cluster <b>$cluster_name</b> has been deleted", "admin"));
    } else {
        new NotifyWidgetFailure(_T("Error during <b>$cluster_name</b> deletion", "admin"));
    }
    header("Location: " . urlStrRedirect("admin/admin/clustersList", array()));
    exit;
} else {
    $f = new PopupForm(_T("Delete " . $cluster_name));
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" =>$uuid, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}