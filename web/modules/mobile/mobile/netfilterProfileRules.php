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

$p = new PageGenerator(sprintf(_T("Rules: %s", "mobile"), htmlspecialchars($profile['name'] ?? '')));
$p->setSideMenu($sidemenu);
$p->display();

$rules = xmlrpc_get_netfilter_profile_rules($profile_id);
if (!is_array($rules)) $rules = [];

$_url_add  = urlStrRedirect('mobile/mobile/addNetfilterProfileRule') . '&id=' . $profile_id;
$_url_back = urlStrRedirect('mobile/mobile/netfilterProfiles');
$_lbl_add  = addslashes(_T('Add rule', 'mobile'));
$_lbl_back = addslashes(_T('Back to profiles', 'mobile'));
?>
<script type="text/javascript">
jQuery(function() {
    var $h2 = jQuery('h2').first();
    $h2.wrap('<div style="display:flex;align-items:center;justify-content:space-between;"></div>');
    $h2.after(
        '<span style="flex-shrink:0;margin-left:16px;">'
        + '<button class="btnPrimary" type="button" onclick="location.href=\'<?php echo $_url_add; ?>\'"><?php echo $_lbl_add; ?></button>'
        + ' <button class="btnSecondary" type="button" onclick="location.href=\'<?php echo $_url_back; ?>\'"><?php echo $_lbl_back; ?></button>'
        + '</span>'
    );
});
</script>

<?php if (empty($rules)): ?>
<p style="color:#888;font-style:italic;"><?php echo _T('No rules yet.', 'mobile'); ?></p>
<?php else: ?>
<?php
$domains = $dates = [];
$actionDelete = $params = [];

foreach ($rules as $rule) {
    $rid  = (int)($rule['id'] ?? 0);
    $dom  = htmlspecialchars($rule['domain'] ?? '');
    $createdAt = $rule['createdAt'] ?? 0;

    $domains[] = $dom;
    $dates[]   = $createdAt > 0 ? date('Y-m-d H:i', (int)($createdAt / 1000)) : '-';

    $actionDelete[] = new ActionPopupItem(
        _T("Delete", "mobile"),
        "deleteNetfilterProfileRule",
        "delete",
        "rule_id",
        "mobile",
        "mobile",
        null,
        500
    );
    $params[] = ['rule_id' => $rid, 'profile_id' => $profile_id, 'domain' => $dom];
}

$n = new OptimizedListInfos($domains, _T("Domain", "mobile"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($dates, _T("Created", "mobile"));
$n->setNavBar(new AjaxNavBar(count($domains), ''));
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);
$n->start = 0;
$n->display();
?>
<?php endif; ?>
