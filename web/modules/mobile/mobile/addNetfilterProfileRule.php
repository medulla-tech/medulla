<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$profile_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
if ($profile_id <= 0) {
    new NotifyWidgetFailure(_T("Invalid profile ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfiles"));
    exit;
}

$profiles = xmlrpc_get_netfilter_profiles();
$profile  = null;
if (is_array($profiles)) {
    foreach ($profiles as $pr) {
        if ((int)($pr['id'] ?? 0) === $profile_id) { $profile = $pr; break; }
    }
}
if (!$profile) {
    new NotifyWidgetFailure(_T("Profile not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfiles"));
    exit;
}
$profile_rule_type = ($profile['filterMode'] ?? 'BLOCKLIST') === 'ALLOWLIST' ? 'ALLOW' : 'BLOCK';

$p = new PageGenerator(_T("Add Profile Rule", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST['badd_rule'])) {
    $domain = trim($_POST['domain'] ?? '');
    if ($domain !== '') {
        $result = xmlrpc_add_netfilter_profile_rule($profile_id, $domain, $profile_rule_type);
        if ($result) {
            new NotifyWidgetSuccess(_T("Rule added", "mobile"));
            header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfileRules") . "&id=" . $profile_id);
            exit;
        } else {
            new NotifyWidgetFailure(_T("Failed to add rule", "mobile"));
        }
    } else {
        new NotifyWidgetFailure(_T("Domain is required", "mobile"));
    }
}
?>
<?php
$f = new Form();
$f->push(new Table());

$domainInput = new InputTpl('domain', '/^.+$/');
$f->add(new TrFormElement(_T('Domain', 'mobile'), $domainInput), ['placeholder' => _T('e.g. youtube.com', 'mobile')]);

$f->pop();
$f->addValidateButtonWithValue('badd_rule', _T('Add rule', 'mobile'));
$f->addButton('bcancel', _T('Cancel', 'mobile'), 'btnSecondary', 'onclick="history.back();"', 'button');
$f->display();
?>
