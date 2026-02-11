<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get parameters
$groupId = isset($_REQUEST['group_id']) ? intval($_REQUEST['group_id']) : 0;
$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';

if ($groupId <= 0) {
    new NotifyWidgetFailure(_T("Invalid group ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

$groups = xmlrpc_get_hmdm_groups();
$group = null;
foreach ($groups as $g) {
    if (isset($g['id']) && $g['id'] == $groupId) {
        $group = $g;
        break;
    }
}

if (!$group) {
    new NotifyWidgetFailure(_T("Group not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

$groupName = $group['name'] ?? '';

if (empty($groupName)) {
    new NotifyWidgetFailure(_T("Group name not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

$messageType = '';
$payload = '';

switch ($action) {
    case 'configUpdated':
        $messageType = 'configUpdated';
        $payload = '';
        break;
        
    case 'custom':
        $messageType = isset($_POST['message_type']) ? $_POST['message_type'] : '';
        $payload = isset($_POST['payload']) ? $_POST['payload'] : '';
        
        if (empty($messageType)) {
            new NotifyWidgetFailure(_T("Message type is required", "mobile"));
            header("Location: " . urlStrRedirect("mobile/mobile/groupQuickAction", array("group_id" => $groupId)));
            exit;
        }
        break;
        
    default:
        new NotifyWidgetFailure(_T("Unknown action", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/groupQuickAction", array("group_id" => $groupId)));
        exit;
}

//send the push message using existing function
$result = xmlrpc_send_hmdm_push_message(
    'group',            // scope (always group for group quick actions)
    $messageType,       // message type
    $payload,           // payload
    '',                 // device number (empty string for group scope)
    $groupId,           // group_id
    ''                  // configuration_id (empty string for group scope)
);

// check result and redirect
if ($result && isset($result['status']) && $result['status'] === 'OK') {
    new NotifyWidgetSuccess(_T("Command sent successfully to group", "mobile"));
} else {
    new NotifyWidgetFailure(_T("Failed to send command to group", "mobile"));
}

header("Location: " . urlStrRedirect("mobile/mobile/functions", array("tab" => "tabpush")));
exit;

?>
