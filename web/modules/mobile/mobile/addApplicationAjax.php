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

$type    = trim($_POST['type'] ?? '');
$name    = trim($_POST['name'] ?? '');
$pkg     = trim($_POST['pkg'] ?? '');
$version = trim($_POST['version'] ?? '');
$url     = trim($_POST['url'] ?? '');
$action  = trim($_POST['action'] ?? '');

if ($name === '') {
    echo json_encode(['status' => 'error', 'message' => _T("Application name is required.", "mobile")]);
    exit;
}
if (!in_array($type, ['app', 'web', 'intent'])) {
    echo json_encode(['status' => 'error', 'message' => _T("Application type is required.", "mobile")]);
    exit;
}

if ($type === 'app') {
    if ($pkg === '') {
        echo json_encode(['status' => 'error', 'message' => _T("Package name is required (ex: com.example.app).", "mobile")]);
        exit;
    }
    if (!preg_match('/^[a-zA-Z0-9_.]+$/', $pkg)) {
        echo json_encode(['status' => 'error', 'message' => _T("Package name contains invalid characters.", "mobile")]);
        exit;
    }
    if ($url !== '' && !filter_var($url, FILTER_VALIDATE_URL) && !preg_match('#^/#', $url)) {
        echo json_encode(['status' => 'error', 'message' => _T("APK URL is not valid.", "mobile")]);
        exit;
    }
} elseif ($type === 'web') {
    if ($url === '') {
        echo json_encode(['status' => 'error', 'message' => _T("URL is required for web applications.", "mobile")]);
        exit;
    }
    if (!filter_var($url, FILTER_VALIDATE_URL) && !preg_match('#^/#', $url)) {
        echo json_encode(['status' => 'error', 'message' => _T("URL is not valid.", "mobile")]);
        exit;
    }
} elseif ($type === 'intent') {
    if ($action === '') {
        echo json_encode(['status' => 'error', 'message' => _T("Action is required for intent applications.", "mobile")]);
        exit;
    }
}

$app = ['name' => $name, 'type' => $type];

if ($type === 'app') {
    $app['pkg'] = $pkg;
    if ($version !== '') $app['version'] = $version;
    if ($url !== '')     $app['url'] = $url;
    if (!empty($_POST['system']))         $app['system'] = true;
    if (!empty($_POST['runAfterInstall'])) $app['runAfterInstall'] = true;
    if (!empty($_POST['runAtBoot']))       $app['runAtBoot'] = true;
    $arch = trim($_POST['arch'] ?? '');
    if ($arch !== '') $app['arch'] = $arch;
    $filePath = trim($_POST['filePath'] ?? '');
    if ($filePath !== '') $app['filePath'] = $filePath;
    $versionCode = trim($_POST['versioncode'] ?? '');
    if ($versionCode !== '') $app['versionCode'] = $versionCode;
} elseif ($type === 'web') {
    $app['url'] = $url;
    if (!empty($_POST['useKiosk'])) $app['useKiosk'] = true;
} elseif ($type === 'intent') {
    $app['action'] = $action;
}

// Common icon fields (all types)
if (!empty($_POST['showicon']))  $app['showIcon'] = true;
$iconId = trim($_POST['icon_id'] ?? '');
if ($iconId !== '') $app['iconId'] = (int)$iconId;
$iconText = trim($_POST['icon_text'] ?? '');
if ($iconText !== '') $app['iconText'] = $iconText;

$resp = xmlrpc_add_hmdm_application($app);

if ($resp === false || $resp === null) {
    echo json_encode(['status' => 'error', 'message' => _T("Error while adding the application.", "mobile")]);
} else {
    echo json_encode(['status' => 'ok', 'message' => sprintf(_T("Application '%s' successfully added", "mobile"), htmlspecialchars($name))]);
}
exit;
