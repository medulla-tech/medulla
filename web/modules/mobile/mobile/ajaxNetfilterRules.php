<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? strtolower(trim($_GET['filter'])) : '';
$field  = isset($_GET['field'])  ? trim($_GET['field'])  : 'all';

$rules = xmlrpc_get_netfilter_rules();
if (!is_array($rules)) $rules = [];

if ($filter !== '') {
    $rules = array_values(array_filter($rules, function($r) use ($filter, $field) {
        if ($field === 'type') {
            return strpos(strtolower($r['ruleType'] ?? ''), $filter) !== false;
        }
        // 'all' or 'domain'
        return strpos(strtolower($r['domain'] ?? ''), $filter) !== false
            || ($field === 'all' && strpos(strtolower($r['ruleType'] ?? ''), $filter) !== false);
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

    $toggleTarget = urlStrRedirect("mobile/mobile/netfilterRuleAction");
    $checked = $enabled ? ' checked' : '';
    $toggles[] = sprintf(
        '<input type="checkbox"%s onchange="mobileToggleNetfilterRule(%d, \'%s\', \'%s\')" style="cursor:pointer;" title="%s">',
        $checked,
        $ruleId,
        $enabled ? 'disable' : 'enable',
        htmlspecialchars($toggleTarget, ENT_QUOTES),
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

    $params[] = ['rule_id' => $ruleId, 'domain' => $domain];
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
echo '<script>(function(){var $tb=jQuery(".listinfos:last tbody");if(!$tb.children("tr").length){$tb.append("<tr><td colspan=\"20\" style=\"text-align:center;color:#888;padding:20px;font-style:italic;\">" + ' . json_encode(_T("No rules found", "mobile")) . ' + "</td></tr>");}})();</script>';
?>
<script>
function mobileToggleNetfilterRule(ruleId, actionType, targetUrl) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = targetUrl;
    var fields = {
        'rule_id': ruleId,
        'action_type': actionType,
        'auth_token': '<?php echo htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8'); ?>'
    };
    for (var key in fields) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = fields[key];
        form.appendChild(input);
    }
    document.body.appendChild(form);
    form.submit();
}
</script>
