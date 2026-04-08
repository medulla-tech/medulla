<?php
require_once("modules/mobile/includes/xmlrpc.php");

$rule_id = isset($_GET['rule_id']) ? intval($_GET['rule_id']) : 0;

if (isset($_POST['bconfirm']) && $rule_id > 0) {
    xmlrpc_delete_netfilter_rule($rule_id);
    header('Location: ' . urlStrRedirect("mobile/mobile/netfilterRules"));
    exit;
}

$f = new PopupForm(_T("Delete this rule", "mobile"));
$f->setLevel('danger');

$hidden = new HiddenTpl("rule_id");
$f->add($hidden, array("value" => $rule_id, "hide" => true));

$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>
