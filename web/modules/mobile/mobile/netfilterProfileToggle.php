<?php
require_once("modules/mobile/includes/xmlrpc.php");

$profile_id  = isset($_POST['profile_id']) ? intval($_POST['profile_id']) : 0;
$action_type = isset($_POST['action_type']) ? $_POST['action_type'] : '';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ' . urlStrRedirect("mobile/mobile/netfilterProfiles"));
    exit;
}

verifyCSRFToken($_POST);

if ($profile_id > 0 && in_array($action_type, ['enable', 'disable'])) {
    $profiles = xmlrpc_get_netfilter_profiles();
    $target   = null;
    if (is_array($profiles)) {
        foreach ($profiles as $p) {
            if ((int)($p['id'] ?? 0) === $profile_id) {
                $target = $p;
                break;
            }
        }
    }
    if ($target) {
        $enabled = $action_type === 'enable';
        xmlrpc_update_netfilter_profile(
            $profile_id,
            $target['name'],
            $target['filterMode'],
            $enabled
        );
    }
}

header('Location: ' . urlStrRedirect("mobile/mobile/netfilterProfiles"));
exit;
?>
