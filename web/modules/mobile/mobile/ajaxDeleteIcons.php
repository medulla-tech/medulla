<?php
// AJAX endpoint to delete an HMDM icon by id
// Include session and core XML-RPC helper first, then module wrapper
$WEBROOT = realpath(__DIR__ . '/../../../');
if ($WEBROOT === false) {
    error_log("ajaxDeleteIcons: failed to resolve web root from " . __DIR__);
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Server configuration error']);
    exit;
}
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

if (!function_exists('xmlCall')) {
    error_log("ajaxDeleteIcons: xmlCall() not defined after including xmlrpc.inc.php");
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Internal server error: RPC helper missing']);
    exit;
}

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

$id = trim($_POST['id'] ?? '');
if ($id === '') {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing id']);
    exit;
}

try {
    $res = xmlrpc_delete_hmdm_icons_by_id(intval($id));
    if ($res === FALSE || $res === null) {
        echo json_encode(['success' => false, 'error' => 'Failed to delete icon']);
        exit;
    }
    echo json_encode(['success' => true, 'data' => $res]);
    exit;
} catch (Exception $e) {
    error_log('ajaxDeleteIcons exception: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    exit;
}

?>