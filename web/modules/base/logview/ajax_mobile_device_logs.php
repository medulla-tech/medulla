<?php
header('Content-type: application/json');

require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../mobile/includes/xmlrpc.php");

$device   = isset($_GET['device'])   ? trim($_GET['device'])   : '';
$package  = isset($_GET['package'])  ? trim($_GET['package'])  : '';
$severity = isset($_GET['severity']) ? trim($_GET['severity'])  : '-1';
$page     = isset($_GET['page'])     ? max(1, intval($_GET['page'])) : 1;
$pagesize = isset($_GET['pagesize']) ? intval($_GET['pagesize']) : 50;

$logs = xmlrpc_get_hmdm_device_logs($device, $package, $severity, $pagesize, $page);
if (!is_array($logs)) {
    $logs = [];
}

$severity_labels = [
    'VERBOSE' => 'Verbose',
    'DEBUG'   => 'Debug',
    'INFO'    => 'Info',
    'WARNING' => 'Warning',
    'ERROR'   => 'Error',
];

$rows = [];
foreach ($logs as $row) {
    $ts   = isset($row['time']) && $row['time'] > 0 ? date('Y-m-d H:i:s', $row['time']) : '';
    $dev  = htmlspecialchars($row['device']  ?? '', ENT_QUOTES, 'UTF-8');
    $pkg  = htmlspecialchars($row['package'] ?? '', ENT_QUOTES, 'UTF-8');
    $sev  = htmlspecialchars($row['severity'] ?? '', ENT_QUOTES, 'UTF-8');
    $msg  = htmlspecialchars($row['message'] ?? '', ENT_QUOTES, 'UTF-8');
    $rows[] = [$ts, $dev, $pkg, $sev, $msg];
}

echo json_encode([
    'data'            => $rows,
    'recordsTotal'    => count($rows),
    'recordsFiltered' => count($rows),
]);
?>
