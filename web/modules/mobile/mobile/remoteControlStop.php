<?php
require_once("modules/mobile/includes/xmlrpc.php");

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Content-Type: application/json');
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

verifyCSRFToken($_POST);

$session_id = isset($_POST['session_id']) ? intval($_POST['session_id']) : 0;

if ($session_id > 0) {
    xmlrpc_stop_remote_control_session($session_id);
}

header('Content-Type: application/json');
echo json_encode(['ok' => true]);
