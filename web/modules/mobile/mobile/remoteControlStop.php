<?php
require_once("modules/mobile/includes/xmlrpc.php");

$session_id = isset($_GET['session_id']) ? intval($_GET['session_id']) : 0;

if ($session_id > 0) {
    xmlrpc_stop_remote_control_session($session_id);
}

header('Content-Type: application/json');
echo json_encode(['ok' => true]);
