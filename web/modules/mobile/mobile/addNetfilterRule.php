<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Add Filter Rule", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST['add_domain']) && !empty($_POST['domain'])) {
    $domain = trim($_POST['domain']);
    $rule_type = in_array($_POST['rule_type'] ?? '', ['BLOCK', 'ALLOW']) ? $_POST['rule_type'] : 'BLOCK';
    $result = xmlrpc_add_netfilter_rule($domain, $rule_type);
    if ($result) {
        new NotifyWidgetSuccess(_T("Rule added", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/netfilterRules"));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to add rule", "mobile"));
    }
}
?>

<?php
$f = new Form();
$f->push(new Table());

$domainInput = new InputTpl('domain', '/^.+$/');
$f->add(new TrFormElement(_T('Domain', 'mobile'), $domainInput), ['placeholder' => _T('e.g. example.com or *.tiktok.com', 'mobile')]);

$ruleTypeSelect = new SelectItem('rule_type');
$ruleTypeSelect->setElements([_T('BLOCK', 'mobile'), _T('ALLOW', 'mobile')]);
$ruleTypeSelect->setElementsVal(['BLOCK', 'ALLOW']);
$f->add(new TrFormElement(_T('Type', 'mobile'), $ruleTypeSelect));

$f->pop();
$f->addValidateButtonWithValue('add_domain', _T('Add rule', 'mobile'));
$f->display();
?>
