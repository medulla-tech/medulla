<?php
require_once("modules/mobile/includes/xmlrpc.php");

$profile_id = isset($_GET['profile_id']) ? intval($_GET['profile_id']) : 0;
$rule_id    = isset($_GET['rule_id'])    ? intval($_GET['rule_id'])    : 0;
$domain     = isset($_GET['domain'])     ? htmlspecialchars($_GET['domain'])     : '';

if (isset($_POST['bconfirm']) && $profile_id > 0 && $rule_id > 0) {
    xmlrpc_delete_netfilter_profile_rule($profile_id, $rule_id);
    header('Location: ' . urlStrRedirect("mobile/mobile/netfilterProfileRules") . "&id=" . $profile_id);
    exit;
}

$f = new PopupForm($domain !== ''
    ? sprintf(_T("Delete rule for '%s'?", "mobile"), $domain)
    : _T("Delete this rule", "mobile"));
$f->setLevel('danger');

$hidden_pid = new HiddenTpl("profile_id");
$f->add($hidden_pid, array("value" => $profile_id, "hide" => true));

$hidden_rid = new HiddenTpl("rule_id");
$f->add($hidden_rid, array("value" => $rule_id, "hide" => true));

$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>
