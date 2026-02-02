<?php
require_once("modules/mobile/includes/xmlrpc.php");

$device = isset($_GET['device']) ? $_GET['device'] : '';
$app = isset($_GET['app']) ? $_GET['app'] : '';
$severity = isset($_GET['severity']) ? intval($_GET['severity']) : -1;

$result = xmlrpc_export_hmdm_device_logs($device, $app, $severity);

exit();
?>
