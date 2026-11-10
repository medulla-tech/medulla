<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter      = isset($_GET['filter'])      ? strtolower(trim($_GET['filter'])) : '';
$filter_mode = isset($_GET['filter_mode']) ? strtoupper(trim($_GET['filter_mode'])) : 'all';
$enabled_f   = isset($_GET['enabled'])     ? $_GET['enabled'] : 'all';

$profiles = xmlrpc_get_netfilter_profiles();
if (!is_array($profiles)) $profiles = [];

$profiles = array_values(array_filter($profiles, function($p) use ($filter, $filter_mode, $enabled_f) {
    if ($filter !== '' && strpos(strtolower($p['name'] ?? ''), $filter) === false) return false;
    if ($filter_mode !== 'ALL' && $filter_mode !== 'all' && ($p['filterMode'] ?? '') !== $filter_mode) return false;
    if ($enabled_f !== 'all') {
        $is_on = !empty($p['enabled']);
        if ($enabled_f === '1' && !$is_on) return false;
        if ($enabled_f === '0' && $is_on)  return false;
    }
    return true;
}));

$ids = $names = $modes = $rule_counts = $config_counts = $toggles = [];
$actionEdit = $actionDelete = [];
$params = [];

foreach ($profiles as $index => $profile) {
    $pid        = (int)($profile['id'] ?? 0);
    $name       = htmlspecialchars($profile['name'] ?? '');
    $mode       = $profile['filterMode'] ?? 'BLOCKLIST';
    $enabled    = !empty($profile['enabled']);
    $ruleCount  = (int)($profile['ruleCount'] ?? 0);
    $cfgCount   = (int)($profile['configCount'] ?? 0);

    $ids[]   = 'nfp_' . $index;
    $names[] = $name;

    $modeColor = ($mode === 'ALLOWLIST') ? '#27ae60' : '#c0392b';
    $modes[] = sprintf('<span style="color:%s;font-weight:bold;">%s</span>', $modeColor, htmlspecialchars($mode));

    $rule_counts[]   = $ruleCount;
    $config_counts[] = $cfgCount;

    $toggles[] = $enabled
        ? '<span style="color:#27ae60;font-weight:bold;">' . _T('Yes', 'mobile') . '</span>'
        : '<span style="color:#999;">' . _T('No', 'mobile') . '</span>';

    $actionEdit[]   = new ActionItem(_T("Edit", "mobile"), "netfilterProfileEdit", "edit", "id", "mobile", "mobile");
    $actionRules[]  = new ActionItem(_T("Rules", "mobile"), "netfilterProfileRules", "display", "id", "mobile", "mobile");
    $actionAddRule[] = new ActionItem(_T("Add rule", "mobile"), "addNetfilterProfileRule", "add", "id", "mobile", "mobile");
    $actionDelete[] = new ActionPopupItem(_T("Delete", "mobile"), "deleteNetfilterProfile", "delete", "id", "mobile", "mobile", null, 500);

    $params[] = ['id' => $pid, 'name' => $name];
}

$n = new OptimizedListInfos($names, _T("Profile name", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($profiles);
$filter_val = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : '';
$n->setNavBar(new AjaxNavBar($count, $filter_val));

$n->addExtraInfo($modes,         _T("Filter mode", "mobile"));
$n->addExtraInfo($rule_counts,   _T("Rules", "mobile"));
$n->addExtraInfo($config_counts, _T("Configurations", "mobile"));
$n->addExtraInfo($toggles,       _T("Enabled", "mobile"));
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionRules);
$n->addActionItemArray($actionAddRule);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();
echo '<script>(function(){var $tb=jQuery(".listinfos:last tbody");if(!$tb.children("tr").length){$tb.append("<tr><td colspan=\"20\" style=\"text-align:center;color:#888;padding:20px;font-style:italic;\">" + ' . json_encode(_T("No netfilter profiles found", "mobile")) . ' + "</td></tr>");}})();</script>';
?>
