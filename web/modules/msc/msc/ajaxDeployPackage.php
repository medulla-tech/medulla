<?php
require_once 'modules/msc/includes/commands_xmlrpc.inc.php';
require_once 'modules/msc/includes/scheduler_xmlrpc.php';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
	http_response_code(405);
	exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

verifyCSRFToken(is_array($data) ? $data : []);

// This ajax page permits to deploy a package using params from POST
$pid = $data['pid'];
$uuids = $data['uuids'];
$deploy_params = $data['deploy_params'];
$mirror = $data['mirror'];
$method = $data['method'];

// Adding command
$cmd_id = add_command_api($pid, $uuids, $deploy_params, $method, '', array(), 0);

// Starting command
scheduler_start_these_commands('', array($cmd_id));

?>
