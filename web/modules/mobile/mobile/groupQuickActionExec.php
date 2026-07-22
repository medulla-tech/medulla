<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceKeys = isset($_POST['device_keys']) && is_array($_POST['device_keys']) ? $_POST['device_keys'] : [];
$groupId = isset($_REQUEST['group_id']) ? intval($_REQUEST['group_id']) : 0;
$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';

if (empty($deviceKeys) && $groupId <= 0) {
    new NotifyWidgetFailure(_T("No devices or group specified", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$messageType = '';
$payload = '';

$allowedActions = ['reboot', 'configUpdated', 'lockDevice', 'wipe', 'runApp', 'uninstallApp', 'deleteFile', 'deleteDir', 'purgeDir', 'permissiveMode', 'intent', 'runCommand', 'exitKiosk', 'clearDownloadHistory', 'grantPermissions'];

if (in_array($action, $allowedActions)) {
    $messageType = $action;
    $payload = isset($_POST['payload']) ? $_POST['payload'] : '';
} elseif ($action === 'custom') {
    $messageType = isset($_POST['message_type']) ? $_POST['message_type'] : '';
    $payload = isset($_POST['payload']) ? $_POST['payload'] : '';
    if (empty($messageType)) {
        new NotifyWidgetFailure(_T("Message type is required", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/index"));
        exit;
    }
} else {
    new NotifyWidgetFailure(_T("Unknown action", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

if (!empty($deviceKeys)) {
    $successCount = 0;
    $failCount = 0;

    foreach ($deviceKeys as $key) {
        $parts = explode('##', $key, 2);
        $deviceNumber = $parts[0];

        if (empty($deviceNumber)) {
            $failCount++;
            continue;
        }

        $result = xmlrpc_send_hmdm_push_message(
            'device',
            $messageType,
            $payload,
            $deviceNumber,
            '',
            ''
        );

        if ($result && isset($result['status']) && $result['status'] === 'OK') {
            $successCount++;
        } else {
            $failCount++;
        }
    }

    if ($successCount > 0 && $failCount === 0) {
        new NotifyWidgetSuccess(sprintf(_T("Command sent successfully to %d device(s)", "mobile"), $successCount));
    } elseif ($successCount > 0) {
        new NotifyWidgetSuccess(sprintf(_T("Command sent to %d device(s), failed for %d", "mobile"), $successCount, $failCount));
    } else {
        new NotifyWidgetFailure(_T("Failed to send command to devices", "mobile"));
    }
} else {
    $result = xmlrpc_send_hmdm_push_message(
        'group',
        $messageType,
        $payload,
        '',
        $groupId,
        ''
    );

    if ($result && isset($result['status']) && $result['status'] === 'OK') {
        new NotifyWidgetSuccess(_T("Command sent successfully to group", "mobile"));
    } else {
        new NotifyWidgetFailure(_T("Failed to send command to group", "mobile"));
    }
}

header("Location: " . urlStrRedirect("mobile/mobile/pushMessages"));
exit;
