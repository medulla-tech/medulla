<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Network Traffic Filtering", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
    return;
}

$settings = xmlrpc_get_netfilter_settings();
if (!is_array($settings)) {
    $settings = ['enabled' => false, 'filterMode' => 'BLOCKLIST'];
}

if (isset($_POST['save'])) {
    $enabled = !empty($_POST['enabled']);
    $filter_mode = in_array($_POST['filterMode'] ?? '', ['BLOCKLIST', 'ALLOWLIST']) ? $_POST['filterMode'] : 'BLOCKLIST';
    $result = xmlrpc_save_netfilter_settings($enabled, $filter_mode);
    if ($result) {
        new NotifyWidgetSuccess(_T("Settings saved", "mobile"));
        $settings['enabled'] = $enabled;
        $settings['filterMode'] = $filter_mode;
    } else {
        new NotifyWidgetFailure(_T("Failed to save settings", "mobile"));
    }
}
?>

<?php
$f = new Form();
$f->push(new Table());

$enabledCheckbox = new CheckboxTpl('enabled');
$f->add(new TrFormElement(_T('Filtering enabled', 'mobile'), $enabledCheckbox), ['value' => !empty($settings['enabled']) ? 'checked' : '']);

$filterModeSelect = new SelectItem('filterMode');
$filterModeSelect->setElements([
    _T('Blocklist (block listed domains)', 'mobile'),
    _T('Allowlist (only allow listed domains)', 'mobile'),
]);
$filterModeSelect->setElementsVal(['BLOCKLIST', 'ALLOWLIST']);
$filterModeSelect->setSelected($settings['filterMode'] ?? 'BLOCKLIST');
$f->add(new TrFormElement(_T('Filter mode', 'mobile'), $filterModeSelect));

$f->pop();
$f->addValidateButtonWithValue('save', _T('Save', 'mobile'));
$f->display();
?>

<?php
$_url_nfr_rules = urlStrRedirect('mobile/mobile/netfilterRules');
$_url_nfr_add   = urlStrRedirect('mobile/mobile/addNetfilterRule');
$_lbl_manage    = addslashes(_T('Manage rules', 'mobile'));
$_lbl_add_rule  = addslashes(_T('Add rule', 'mobile'));
?>
<script type="text/javascript">
jQuery(function() {
    var $h2 = jQuery('h2').first();
    $h2.wrap('<div style="display:flex;align-items:center;justify-content:space-between;"></div>');
    $h2.after(
        '<span style="flex-shrink:0;margin-left:16px;">'
        + '<button class="btnPrimary" type="button" onclick="location.href=\'<?php echo $_url_nfr_rules; ?>\'"><?php echo $_lbl_manage; ?></button>'
        + ' <button class="btnPrimary" type="button" onclick="location.href=\'<?php echo $_url_nfr_add; ?>\'"><?php echo $_lbl_add_rule; ?></button>'
        + '</span>'
    );
});
</script>
