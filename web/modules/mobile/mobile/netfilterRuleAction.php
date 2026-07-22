<?php
require_once("modules/mobile/includes/xmlrpc.php");

$rule_id = isset($_GET['rule_id']) ? intval($_GET['rule_id']) : 0;
$action_type = isset($_GET['action_type']) ? $_GET['action_type'] : '';

if ($rule_id > 0 && in_array($action_type, ['enable', 'disable'])) {
    $rules = xmlrpc_get_netfilter_rules();
    $target = null;
    if (is_array($rules)) {
        foreach ($rules as $r) {
            if ((int)($r['id'] ?? 0) === $rule_id) {
                $target = $r;
                break;
            }
        }
    }
    if ($target) {
        $enabled = $action_type === 'enable';
        xmlrpc_update_netfilter_rule($rule_id, $target['domain'], $target['ruleType'], $enabled);
    }
}

header('Location: ' . urlStrRedirect("mobile/mobile/netfilterRules"));
exit;
