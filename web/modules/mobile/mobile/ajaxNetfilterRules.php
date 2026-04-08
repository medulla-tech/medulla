<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? strtolower(trim($_GET['filter'])) : '';

$rules = xmlrpc_get_netfilter_rules();
if (!is_array($rules)) $rules = [];

if ($filter !== '') {
    $rules = array_values(array_filter($rules, function($r) use ($filter) {
        return strpos(strtolower($r['domain'] ?? ''), $filter) !== false;
    }));
}

$ids = $domains = $types = $dates = $toggles = [];
$actionDelete = [];
$params = [];

foreach ($rules as $index => $rule) {
    $ruleId   = (int)($rule['id'] ?? 0);
    $domain   = htmlspecialchars($rule['domain'] ?? '');
    $ruleType = $rule['ruleType'] ?? '';
    $enabled  = !empty($rule['enabled']);
    $createdAt = $rule['createdAt'] ?? 0;

    $ids[]    = 'nfr_' . $index;
    $domains[] = $domain;

    $typeColor = ($ruleType === 'BLOCK') ? '#c0392b' : '#27ae60';
    $types[] = sprintf(
        '<span style="color:%s; font-weight:bold;">%s</span>',
        $typeColor,
        htmlspecialchars($ruleType)
    );

    if ($createdAt > 0) {
        $dates[] = date('Y-m-d H:i', (int)($createdAt / 1000));
    } else {
        $dates[] = '-';
    }

    $toggleUrl = 'main.php?module=mobile&amp;submod=mobile&amp;action=netfilterRuleAction'
               . '&amp;rule_id=' . $ruleId
               . '&amp;action_type=' . ($enabled ? 'disable' : 'enable');
    $checked = $enabled ? ' checked' : '';
    $toggles[] = sprintf(
        '<input type="checkbox"%s onchange="window.location=\'%s\'" style="cursor:pointer;" title="%s">',
        $checked,
        $toggleUrl,
        $enabled ? _T('Disable', 'mobile') : _T('Enable', 'mobile')
    );

    $actionDelete[] = new ActionPopupItem(
        _T("Delete", "mobile"),
        "deleteNetfilterRule",
        "delete",
        "rule_id",
        "mobile",
        "mobile",
        null,
        500
    );

    $params[] = ['rule_id' => $ruleId];
}

$n = new OptimizedListInfos($domains, _T("Domain", "mobile"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$count = safeCount($rules);
$filter_val = isset($_REQUEST['filter']) ? $_REQUEST['filter'] : '';
$n->setNavBar(new AjaxNavBar($count, $filter_val));

$n->addExtraInfo($types,   _T("Type", "mobile"));
$n->addExtraInfo($dates,   _T("Created", "mobile"));
$n->addExtraInfo($toggles, _T("Enabled", "mobile"));
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->start = 0;
$n->display();
?>
