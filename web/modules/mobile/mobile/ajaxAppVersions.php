<?php
require_once("modules/mobile/includes/xmlrpc.php");
header('Content-Type: application/json');
$appId = isset($_GET['app_id']) ? intval($_GET['app_id']) : 0;
if ($appId <= 0) { echo json_encode([]); exit; }
$versions = xmlrpc_get_application_versions($appId);
echo json_encode($versions ?: []);
