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

$_is_hmdm_admin = false;
try {
    $current_hmdm_user = xmlrpc_get_current_hmdm_user();
    if ($current_hmdm_user && isset($current_hmdm_user['userRole'])) {
        $role_name = $current_hmdm_user['userRole']['name'] ?? '';
        $_is_hmdm_admin = (stripos($role_name, 'admin') !== false);
    }
} catch (Exception $e) {
    error_log("Error checking HMDM user role: " . $e->getMessage());
}

if (!$_is_hmdm_admin) {
    http_response_code(403);
    echo json_encode(['status' => 'error', 'message' => _T("Access denied. Only administrators can manage users.", "mobile")]);
    exit;
}

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
    exit;
}

$login       = trim($_POST['login']   ?? '');
$user_id     = trim($_POST['user_id'] ?? '') ?: null;
$role_id     = isset($_POST['role_id']) ? (int)$_POST['role_id'] : null;
$all_devices = !empty($_POST['all_devices']) && $_POST['all_devices'] != '0';
$all_configs = !empty($_POST['all_configs'])  && $_POST['all_configs']  != '0';
$device_groups = (isset($_POST['device_groups']) && is_array($_POST['device_groups']))
    ? array_map('intval', $_POST['device_groups']) : [];
$config_ids    = (isset($_POST['config_ids']) && is_array($_POST['config_ids']))
    ? array_map('intval', $_POST['config_ids']) : [];

if ($login === '') {
    echo json_encode(['status' => 'error', 'message' => _T("Login is required", "mobile")]);
    exit;
}

if ($login !== 'admin' && !xmlCall('base.existUser', [$login])) {
    if ($user_id !== null) {
        xmlrpc_delete_hmdm_user($user_id);
        echo json_encode([
            'status' => 'ok',
            'message' => sprintf(_T("User '%s' no longer exists in Medulla - HMDM account deleted", "mobile"), $login),
            'deleted' => true
        ]);
    } else {
        echo json_encode([
            'status' => 'error',
            'message' => sprintf(_T("User '%s' does not exist in Medulla", "mobile"), $login)
        ]);
    }
    exit;
}

if (!$role_id) {
    $roles = xmlrpc_get_hmdm_all_roles();
    error_log("Configure user - Role lookup. Provided role_id: $role_id, All roles: " . json_encode($roles));

    if (is_array($roles) && !empty($roles)) {
        foreach ($roles as $r) {
            if (isset($r['name']) && strtolower(trim($r['name'])) === 'user') {
                $role_id = (int)$r['id'];
                error_log("Found 'user' role with ID: $role_id");
                break;
            }
        }

        if (!$role_id) {
            foreach ($roles as $r) {
                if (isset($r['id']) && empty($r['superAdmin'])) {
                    $role_id = (int)$r['id'];
                    error_log("Using first non-superadmin role ID: $role_id (name: " . ($r['name'] ?? 'unknown') . ")");
                    break;
                }
            }
        }

        if (!$role_id && !empty($roles)) {
            $role_id = (int)($roles[0]['id'] ?? 0);
            error_log("Using first role ID: $role_id");
        }
    }
}

if (!$role_id) {
    echo json_encode(['status' => 'error', 'message' => _T("Could not determine user role", "mobile")]);
    exit;
}

$result = xmlrpc_create_or_update_hmdm_user(
    $login, $role_id, $all_devices, $all_configs,
    $user_id ? (int)$user_id : null,
    $device_groups, $config_ids
);

if ($result !== null && isset($result['status']) && $result['status'] === 'OK') {
    $msg = $user_id
        ? sprintf(_T("Access updated for '%s'", "mobile"), $login)
        : sprintf(_T("MDM access configured for '%s'", "mobile"), $login);
    echo json_encode(['status' => 'ok', 'message' => $msg]);
} else {
    $err = isset($result['message']) ? $result['message'] : _T("Failed to save user", "mobile");
    echo json_encode(['status' => 'error', 'message' => $err]);
}
exit;
