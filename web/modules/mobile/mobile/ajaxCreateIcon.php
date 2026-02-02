<?php
// Ensure session and core XML-RPC helpers are loaded (same pattern as other ajax endpoints)
// Resolve web root reliably and include required helpers in correct order
$WEBROOT = realpath(__DIR__ . '/../../../');
if ($WEBROOT === false) {
    error_log("ajaxCreateIcon: failed to resolve web root from " . __DIR__);
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Server configuration error']);
    exit;
}
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

if (!function_exists('xmlCall')) {
    error_log("ajaxCreateIcon: xmlCall() not defined after including xmlrpc.inc.php");
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Internal server error: RPC helper missing']);
    exit;
}
header('Content-Type: application/json');

$response = ['success' => false, 'error' => ''];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    $response['error'] = 'Method not allowed';
    echo json_encode($response);
    exit;
}

$name = trim($_POST['name'] ?? '');
$fileId = trim($_POST['fileId'] ?? '');
$fileName = trim($_POST['fileName'] ?? '');
$id = isset($_POST['id']) ? trim($_POST['id']) : null;

if ($name === '') {
    $response['error'] = _T('Icon name is required', 'mobile');
    echo json_encode($response);
    exit;
}

if ($fileId === '') {
    $response['error'] = _T('File ID is required', 'mobile');
    echo json_encode($response);
    exit;
}

$iconData = [
    'name' => $name,
    'fileId' => (int)$fileId,
    'fileName' => $fileName
];
if ($id !== null && $id !== '') {
    $iconData['id'] = (int)$id;
}

try {
    $result = xmlrpc_add_hmdm_icon($iconData);
    if ($result !== false && $result !== null) {
        $response['success'] = true;
        $response['data'] = $result;
    } else {
        $response['error'] = _T('Failed to create icon', 'mobile');
    }
} catch (Exception $e) {
    $response['error'] = $e->getMessage();
}

echo json_encode($response);
exit;

?>
