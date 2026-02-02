<?php
/**
 * Ajax endpoint for APK file upload
 * Uploads file via xmlrpc_upload_web_ui_files and returns metadata
 */

// Base includes (same pattern as other AJAX endpoints)
$WEBROOT = realpath(__DIR__ . '/../../../');
if ($WEBROOT === false) {
    error_log("ajaxUploadApk: failed to resolve web root from " . __DIR__);
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['status' => 'error', 'error' => 'Server configuration error']);
    exit;
}
require_once($WEBROOT . '/includes/session.inc.php');
require_once($WEBROOT . '/includes/xmlrpc.inc.php');
require_once(__DIR__ . '/../includes/xmlrpc.php');

if (!function_exists('xmlCall')) {
    error_log("ajaxUploadApk: xmlCall() not defined after including xmlrpc.inc.php");
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode(['status' => 'error', 'error' => 'Internal server error: RPC helper missing']);
    exit;
}

header('Content-Type: application/json');

try {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        echo json_encode(['status' => 'error', 'error' => 'Invalid request method']);
        exit;
    }

    if (!isset($_POST['action']) || $_POST['action'] !== 'upload_apk') {
        echo json_encode(['status' => 'error', 'error' => 'Invalid action']);
        exit;
    }

    if (!isset($_FILES['apk_file']) || $_FILES['apk_file']['error'] !== UPLOAD_ERR_OK) {
        $error_code = isset($_FILES['apk_file']) ? $_FILES['apk_file']['error'] : 'No file';
        echo json_encode(['status' => 'error', 'error' => 'File upload error: ' . $error_code]);
        exit;
    }

    $file = $_FILES['apk_file'];
    $file_ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

    // Validate file extension
    if ($file_ext !== 'apk' && $file_ext !== 'xapk') {
        echo json_encode(['status' => 'error', 'error' => 'Only APK and XAPK files are allowed']);
        exit;
    }

    // Determine MIME type
    $mime_type = ($file_ext === 'apk')
        ? 'application/vnd.android.package-archive'
        : 'application/octet-stream';

    error_log('[ajaxUploadApk] Uploading file: ' . $file['name'] . ' (type: ' . $mime_type . ')');

    // Call xmlrpc_upload_web_ui_files
    $response = xmlrpc_upload_web_ui_files($file['tmp_name'], $file['name'], $mime_type);

    error_log('[ajaxUploadApk] Response: ' . json_encode($response));

    if ($response === false || $response === null) {
        echo json_encode(['status' => 'error', 'error' => 'Upload failed']);
        exit;
    }

    // Success shape
    if (isset($response['status']) && $response['status'] === 'OK' && isset($response['data'])) {
        echo json_encode([
            'status' => 'success',
            'data' => $response['data']
        ]);
    } else {
        $error_msg = isset($response['error']) ? $response['error'] : 'Unknown error';
        echo json_encode(['status' => 'error', 'error' => $error_msg]);
    }
} catch (Exception $e) {
    error_log('ajaxUploadApk exception: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['status' => 'error', 'error' => $e->getMessage()]);
}
exit;
