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
    echo json_encode(['status' => 'error', 'message' => _T("Access denied. Only administrators can manage roles.", "mobile")]);
    exit;
}

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
    exit;
}

$action = trim($_POST['action'] ?? '');

if ($action === 'delete') {
    $role_id = isset($_POST['role_id']) ? (int)$_POST['role_id'] : 0;

    if (!$role_id) {
        echo json_encode(['status' => 'error', 'message' => _T("Role ID is required", "mobile")]);
        exit;
    }

    $result = xmlrpc_delete_hmdm_role($role_id);

    if ($result === true) {
        echo json_encode(['status' => 'ok', 'message' => _T("Role deleted successfully", "mobile")]);
    } else {
        echo json_encode(['status' => 'error', 'message' => _T("Failed to delete role", "mobile")]);
    }
    exit;
}

$role_id = isset($_POST['role_id']) ? (int)$_POST['role_id'] : 0;
$name = trim($_POST['name'] ?? '');
$description = trim($_POST['description'] ?? '');
$permission_ids = isset($_POST['permission_ids']) && is_array($_POST['permission_ids'])
    ? array_map('intval', $_POST['permission_ids'])
    : [];

if ($name === '') {
    echo json_encode(['status' => 'error', 'message' => _T("Role name is required", "mobile")]);
    exit;
}

$result = xmlrpc_create_or_update_hmdm_role(
    $name,
    $description,
    $permission_ids,
    $role_id ?: null
);

if ($result !== null) {
    if (isset($result['status']) && $result['status'] === 'OK') {
        $msg = $role_id
            ? sprintf(_T("Role '%s' updated successfully", "mobile"), $name)
            : sprintf(_T("Role '%s' created successfully", "mobile"), $name);
        echo json_encode(['status' => 'ok', 'message' => $msg]);
    } elseif (isset($result['status']) && $result['status'] === 'ERROR') {
        echo json_encode(['status' => 'error', 'message' => $result['message'] ?? _T("Operation failed", "mobile")]);
    } else {
        $msg = $role_id
            ? sprintf(_T("Role '%s' updated successfully", "mobile"), $name)
            : sprintf(_T("Role '%s' created successfully", "mobile"), $name);
        echo json_encode(['status' => 'ok', 'message' => $msg]);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => _T("Failed to save role", "mobile")]);
}
