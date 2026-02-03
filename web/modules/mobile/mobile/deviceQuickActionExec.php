<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get parameters
$deviceId = isset($_REQUEST['id']) ? intval($_REQUEST['id']) : 0;
$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';

if ($deviceId <= 0) {
    new NotifyWidgetFailure(_T("Invalid device ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$devices = xmlrpc_get_hmdm_devices();
$device = null;
foreach ($devices as $d) {
    if (isset($d['id']) && $d['id'] == $deviceId) {
        $device = $d;
        break;
    }
}

if (!$device) {
    new NotifyWidgetFailure(_T("Device not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$deviceNumber = $device['number'] ?? '';

if (empty($deviceNumber)) {
    new NotifyWidgetFailure(_T("Device number not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$messageType = '';
$payload = '';

switch ($action) {
    case 'reboot':
        $messageType = 'reboot';
        $payload = '';
        break;
        
    case 'configUpdated':
        $messageType = 'configUpdated';
        $payload = '';
        break;
        
    case 'custom':
        $messageType = isset($_POST['message_type']) ? $_POST['message_type'] : '';
        $payload = isset($_POST['payload']) ? $_POST['payload'] : '';
        
        if (empty($messageType)) {
            new NotifyWidgetFailure(_T("Message type is required", "mobile"));
            header("Location: " . urlStrRedirect("mobile/mobile/quickAction", array("id" => $deviceId)));
            exit;
        }
        break;
        
    default:
        new NotifyWidgetFailure(_T("Unknown action", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/quickAction", array("id" => $deviceId)));
        exit;
}

//send the push message using existing function
$result = xmlrpc_send_hmdm_push_message(
    'device',           // scope (always device for quick actions)
    $messageType,       // message type
    $payload,           // payload
    $deviceNumber,      // device number
    '',                 // group_id (empty string for device scope)
    ''                  // configuration_id (empty string for device scope)
);

// check result and redirect
if ($result && isset($result['status']) && $result['status'] === 'OK') {
    new NotifyWidgetSuccess(_T("Command sent successfully to device", "mobile"));
} else {
    new NotifyWidgetFailure(_T("Failed to send command to device", "mobile"));
}

header("Location: " . urlStrRedirect("mobile/mobile/index"));
exit;

?>
