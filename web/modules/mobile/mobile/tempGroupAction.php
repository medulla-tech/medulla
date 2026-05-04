<?php
if (!function_exists('_T')) {
    function _T($str, $domain = '') { return $str; }
}
$WEBROOT = realpath(__DIR__ . '/../../../');
if ($WEBROOT === false) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Server configuration error']);
    exit;
}
chdir($WEBROOT);
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

header('Content-Type: application/json');

$deviceKeys = isset($_POST['device_keys']) && is_array($_POST['device_keys']) ? $_POST['device_keys'] : [];

if (empty($deviceKeys)) {
    echo json_encode(['status' => 'error', 'message' => _T("No devices provided", "mobile")]);
    exit;
}

$tmpName = '_tmp_' . time();

xmlrpc_add_hmdm_group($tmpName);

$tmpGroupId = null;
$allGroups = xmlrpc_get_hmdm_groups();
foreach ($allGroups as $grp) {
    if (isset($grp['name']) && $grp['name'] === $tmpName) {
        $tmpGroupId = $grp['id'];
        break;
    }
}

if (!$tmpGroupId) {
    echo json_encode(['status' => 'error', 'message' => _T("Failed to create temporary group", "mobile")]);
    exit;
}

$allDevices = xmlrpc_get_hmdm_devices();
if (is_array($allDevices)) {
    $deviceMap = [];
    foreach ($allDevices as $device) {
        $devId = $device['id'] ?? $device['deviceId'] ?? null;
        if ($devId) {
            $deviceMap[(string)$devId] = $device;
        }
    }

    foreach ($deviceKeys as $key) {
        $parts = explode('##', $key, 2);
        $devId = isset($parts[1]) ? $parts[1] : null;
        if (!$devId || !isset($deviceMap[$devId])) {
            continue;
        }
        $device = $deviceMap[$devId];
        $existingGroups = $device['groups'] ?? [];
        $newGroupsList = [];
        foreach ($existingGroups as $grp) {
            if (isset($grp['id'])) {
                $newGroupsList[] = $grp['id'];
            }
        }
        $newGroupsList[] = $tmpGroupId;
        xmlrpc_add_hmdm_device(
            $device['number'],
            $device['configurationId'],
            $device['description'] ?? '',
            $newGroupsList,
            $device['imei'] ?? '',
            $device['phone'] ?? '',
            $devId
        );
    }
}

echo json_encode(['status' => 'ok', 'group_id' => $tmpGroupId]);
