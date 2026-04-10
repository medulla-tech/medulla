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

$source      = trim($_POST['file-source'] ?? '');
$fileName    = trim($_POST['file_name'] ?? '');
$description = trim($_POST['description'] ?? '');
$pathOnDevice = trim($_POST['path_device'] ?? '');

if ($fileName === '') {
    echo json_encode(['status' => 'error', 'message' => _T("File name is required", "mobile")]);
    exit;
}

$variableContent = (isset($_POST['variable_content']) && $_POST['variable_content'] === '1') ? 1 : 0;

$configIds = [];
if (!empty($_POST['configs']) && is_array($_POST['configs'])) {
    $configIds = array_map('intval', $_POST['configs']);
}

if ($source === 'upload') {
    if (!isset($_FILES['file_upload']) || $_FILES['file_upload']['error'] !== UPLOAD_ERR_OK) {
        echo json_encode(['status' => 'error', 'message' => _T("Please select a file to upload", "mobile")]);
        exit;
    }
    $tmpPath  = $_FILES['file_upload']['tmp_name'];
    $origName = $_FILES['file_upload']['name'];
    $result   = xmlrpc_add_hmdm_file($tmpPath, $origName, null, $fileName, $pathOnDevice, $description, $variableContent, $configIds);
} elseif ($source === 'external') {
    $fileUrl = trim($_POST['file_url'] ?? '');
    if ($fileUrl === '') {
        echo json_encode(['status' => 'error', 'message' => _T("File URL is required", "mobile")]);
        exit;
    }
    if (!filter_var($fileUrl, FILTER_VALIDATE_URL)) {
        echo json_encode(['status' => 'error', 'message' => _T("Please enter a valid URL", "mobile")]);
        exit;
    }
    $result = xmlrpc_add_hmdm_file(null, null, $fileUrl, $fileName, $pathOnDevice, $description, $variableContent, $configIds);
} else {
    echo json_encode(['status' => 'error', 'message' => _T("Invalid file source", "mobile")]);
    exit;
}

if ($result === true || (is_array($result) && isset($result['id']))) {
    echo json_encode(['status' => 'ok', 'message' => sprintf(_T("File '%s' successfully added", "mobile"), htmlspecialchars($fileName))]);
} else {
    $error_msg = _T("Failed to add file", "mobile");
    if (is_array($result) && isset($result['message'])) {
        if ($result['message'] === 'error.duplicate.file') {
            $error_msg = _T("A file with the same name already exists", "mobile");
        } else {
            $error_msg = $result['message'];
        }
    }
    echo json_encode(['status' => 'error', 'message' => $error_msg]);
}
exit;
