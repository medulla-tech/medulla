<?php
require_once("modules/mobile/includes/xmlrpc.php");

// get parameters
$configId = isset($_REQUEST['config_id']) ? intval($_REQUEST['config_id']) : 0;
$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';

if ($configId <= 0) {
    new NotifyWidgetFailure(_T("Invalid configuration ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
    exit;
}

$configs = xmlrpc_get_hmdm_configurations();
$config = null;
foreach ($configs as $c) {
    if (isset($c['id']) && $c['id'] == $configId) {
        $config = $c;
        break;
    }
}

if (!$config) {
    new NotifyWidgetFailure(_T("Configuration not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
    exit;
}

$configName = $config['name'] ?? '';

if (empty($configName)) {
    new NotifyWidgetFailure(_T("Configuration name not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurationsList"));
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
            header("Location: " . urlStrRedirect("mobile/mobile/configQuickAction", array("config_id" => $configId)));
            exit;
        }
        break;
        
    default:
        new NotifyWidgetFailure(_T("Unknown action", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/configQuickAction", array("config_id" => $configId)));
        exit;
}

// send the push message using existing function
$result = xmlrpc_send_hmdm_push_message(
    'configuration',    // scope
    $messageType,       // message type
    $payload,           // payload
    '',                 // device number (empty for configuration scope)
    '',                 // group_id (empty for configuration scope)
    $configId           // configuration_id
);

// check result and redirect
if ($result && isset($result['status']) && $result['status'] === 'OK') {
    new NotifyWidgetSuccess(_T("Command sent successfully to configuration", "mobile"));
} else {
    new NotifyWidgetFailure(_T("Failed to send command to configuration", "mobile"));
}

header("Location: " . urlStrRedirect("mobile/mobile/functions", array("tab" => "tabpush")));
exit;

?>
