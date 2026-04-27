<?php
if (!function_exists('_T')) {
    function _T($str, $domain = '')
    {
        return $str;
    }
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

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
    exit;
}

$name    = trim($_POST['add-phone'] ?? '');
$imei    = trim($_POST['add-imei'] ?? '');
$custom1 = trim($_POST['add-custom1'] ?? '');
$desc    = trim($_POST['desc-zone'] ?? '');
$config  = trim($_POST['configuration_id'] ?? '');

if ($name === '') {
    echo json_encode(['status' => 'error', 'message' => _T("The device name is required", "mobile")]);
    exit;
}

if (!preg_match('/^[a-zA-Z0-9\s]+$/', $name)) {
    echo json_encode(['status' => 'error', 'message' => _T("The device name contains invalid characters", "mobile")]);
    exit;
}

if ($config === '') {
    echo json_encode(['status' => 'error', 'message' => _T("Configuration is required", "mobile")]);
    exit;
}

$groups = null;
if (!empty($_POST['groups']) && is_array($_POST['groups'])) {
    $groups = array_map('intval', $_POST['groups']);
}

$result = xmlrpc_add_hmdm_device($name, $config, $desc, $groups, $imei, '', null, $custom1);

if ($result && isset($result['status']) && $result['status'] === 'OK') {
    // If groups were selected, do a follow-up update to ensure they stick
    // (HMDM may ignore groups on initial PUT creation)
    if ($groups !== null) {
        $data = $result['data'] ?? null;
        $deviceId = null;
        if (is_array($data)) {
            $deviceId = $data['id'] ?? null;
        }
        if (!$deviceId) {
            // Find the newly created device by name
            $allDevices = xmlrpc_get_hmdm_devices();
            if (is_array($allDevices)) {
                foreach ($allDevices as $dev) {
                    if (($dev['number'] ?? '') === $name) {
                        $deviceId = $dev['id'] ?? null;
                    }
                }
            }
        }
        if ($deviceId) {
            xmlrpc_add_hmdm_device($name, $config, $desc, $groups, '', '', $deviceId);
        }
    }
    echo json_encode(['status' => 'ok', 'message' => sprintf(_T("Device '%s' successfully created", "mobile"), htmlspecialchars($name))]);
} else {
    $error_msg = isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
    echo json_encode(['status' => 'error', 'message' => sprintf(_T("Failed to create device: %s", "mobile"), $error_msg)]);
}
exit;
