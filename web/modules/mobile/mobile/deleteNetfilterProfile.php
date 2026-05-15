<?php
require_once("modules/mobile/includes/xmlrpc.php");

$profile_id = isset($_GET['id']) ? intval($_GET['id']) : 0;

if (isset($_POST['bconfirm']) && $profile_id > 0) {
    xmlrpc_delete_netfilter_profile($profile_id);
    header('Location: ' . urlStrRedirect("mobile/mobile/netfilterProfiles"));
    exit;
}

$f = new PopupForm(_T("Delete this profile", "mobile"));
$f->setLevel('danger');

$hidden = new HiddenTpl("id");
$f->add($hidden, array("value" => $profile_id, "hide" => true));

$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>
