<?php
// AJAX endpoint to return HMDM icons as JSON
// Include session and core XML-RPC helper first, then module wrapper
$WEBROOT = realpath(__DIR__ . '/../../../');
if ($WEBROOT === false) {
    error_log("ajaxGetIcons: failed to resolve web root from " . __DIR__);
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Server configuration error']);
    exit;
}
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

if (!function_exists('xmlCall')) {
    error_log("ajaxGetIcons: xmlCall() not defined after including xmlrpc.inc.php");
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'error' => 'Internal server error: RPC helper missing']);
    exit;
}

header('Content-Type: application/json');

try {
    $icons = xmlrpc_get_hmdm_icons();
    if ($icons === false || $icons === null) {
        echo json_encode(['success' => false, 'error' => 'No icons available']);
        exit;
    }
    echo json_encode(['success' => true, 'data' => $icons]);
} catch (Exception $e) {
    error_log('ajaxGetIcons exception: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
exit;

?>