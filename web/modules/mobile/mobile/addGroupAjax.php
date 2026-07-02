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
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
    exit;
}

$name = trim($_POST['name'] ?? '');

if ($name === '') {
    echo json_encode(['status' => 'error', 'message' => _T("Group name is required", "mobile")]);
    exit;
}

if (!preg_match('/^[a-zA-Z0-9\s\-_:]+$/', $name)) {
    echo json_encode(['status' => 'error', 'message' => _T("Group name contains invalid characters", "mobile")]);
    exit;
}

$result = xmlrpc_add_hmdm_group($name);

if (!($result && is_array($result) && isset($result['status']) && $result['status'] === 'OK')) {
    $error_msg = isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
    echo json_encode(['status' => 'error', 'message' => sprintf(_T("Failed to create group: %s", "mobile"), $error_msg)]);
    exit;
}

$deviceKeys = (!empty($_POST['devices']) && is_array($_POST['devices'])) ? $_POST['devices'] : [];

if (!empty($deviceKeys)) {
    $groupId = null;
    $allGroups = xmlrpc_get_hmdm_groups();
    if (is_array($allGroups)) {
        foreach ($allGroups as $grp) {
            if ($grp['name'] === $name) {
                $groupId = $grp['id'];
                break;
            }
        }
    }

    if ($groupId) {
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
                $parts = explode('##', $key);
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
                $newGroupsList[] = $groupId;
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
    }
}

echo json_encode(['status' => 'ok', 'message' => sprintf(_T("Group '%s' successfully created", "mobile"), htmlspecialchars($name))]);
exit;
