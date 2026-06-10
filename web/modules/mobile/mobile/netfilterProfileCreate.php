<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Create Filter Profile", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST['bcancel'])) {
    header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfiles"));
    exit;
}

if (isset($_POST['bsave'])) {
    $name        = trim($_POST['profile_name'] ?? '');
    $filter_mode = in_array($_POST['filter_mode'] ?? '', ['BLOCKLIST', 'ALLOWLIST'])
                   ? $_POST['filter_mode'] : 'BLOCKLIST';

    if ($name === '') {
        new NotifyWidgetFailure(_T("Profile name is required", "mobile"));
    } else {
        $result = xmlrpc_create_netfilter_profile($name, $filter_mode);
        if ($result && isset($result['id'])) {
            header("Location: " . urlStrRedirect("mobile/mobile/netfilterProfileEdit") . "&id=" . intval($result['id']));
            exit;
        } else {
            new NotifyWidgetFailure(_T("Failed to create profile", "mobile"));
        }
    }
}
?>

<?php
$f = new Form();
$f->push(new Table());

$nameInput = new InputTpl('profile_name', '/^.+$/');
$f->add(new TrFormElement(_T('Profile name', 'mobile'), $nameInput), [
    'value'       => htmlspecialchars($_POST['profile_name'] ?? ''),
    'placeholder' => _T('e.g. Social Media Block', 'mobile'),
]);

$modeSelect = new SelectItem('filter_mode');
$modeSelect->setElements([
    _T('Blocklist (block listed domains)', 'mobile'),
    _T('Allowlist (only allow listed domains)', 'mobile'),
]);
$modeSelect->setElementsVal(['BLOCKLIST', 'ALLOWLIST']);
$f->add(new TrFormElement(_T('Filter mode', 'mobile'), $modeSelect));

$f->pop();
$f->addValidateButtonWithValue('bsave', _T('Create profile', 'mobile'));
$f->addCancelButton('bcancel');
$f->display();
?>
