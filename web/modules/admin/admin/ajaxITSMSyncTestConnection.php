<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * file: admin/ajaxITSMSyncTestConnection.php
 * Module: ITSM Synchronisation - Test Connection AJAX endpoint
 */

ob_start();

require_once("modules/admin/includes/xmlrpc.php");

function itsmsync_json_response($payload, $statusCode = 200)
{
    $noise = '';
    while (ob_get_level() > 0) {
        $chunk = ob_get_clean();
        if ($chunk !== false && $chunk !== '') {
            $noise .= $chunk;
        }
    }

    if (trim($noise) !== '') {
        error_log('[itsm-test-ajax] non-json output captured: ' . trim($noise));
    }

    if (!is_array($payload)) {
        $payload = array('success' => false, 'message' => 'Invalid payload');
    }

    http_response_code((int) $statusCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload);
    exit;
}

function itsmsync_connection_signature($connection_mode, $source)
{
    $mode = (string) $connection_mode;
    $parts = array('mode=' . $mode);

    if ($mode === 'db') {
        $parts[] = 'db_host=' . trim((string) ($source['db_host'] ?? ''));
        $parts[] = 'db_port=' . trim((string) ($source['db_port'] ?? '3306'));
        $parts[] = 'db_name=' . trim((string) ($source['db_name'] ?? ''));
        $parts[] = 'db_user=' . trim((string) ($source['db_user'] ?? ''));
        $parts[] = 'db_pass=' . trim((string) ($source['db_pass'] ?? ''));
    } else {
        $parts[] = 'api_url=' . trim((string) ($source['api_url'] ?? ''));
        $parts[] = 'app_token=' . trim((string) ($source['app_token'] ?? ''));
        $parts[] = 'user_token=' . trim((string) ($source['user_token'] ?? ''));
    }

    return hash('sha256', implode('|', $parts));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    itsmsync_json_response(array('success' => false, 'message' => 'Invalid request method'), 405);
}

if (!isset($_POST['auth_token']) || !isset($_SESSION['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
    itsmsync_json_response(array('success' => false, 'message' => 'Security token validation failed'), 403);
}

$itsm_type = isset($_POST['itsm_type']) ? (string) $_POST['itsm_type'] : 'glpi';
$connection_mode = isset($_POST['connection_mode']) ? (string) $_POST['connection_mode'] : '';
$client_id = '';
if (isset($_POST['entiteid']) && $_POST['entiteid'] !== '') {
    $client_id = (string) $_POST['entiteid'];
} elseif (isset($_POST['client_id']) && $_POST['client_id'] !== '') {
    $client_id = (string) $_POST['client_id'];
}

$config = array();

if ($connection_mode === 'db') {
    $config['conn.db_host'] = isset($_POST['db_host']) ? (string) $_POST['db_host'] : '';
    $config['conn.db_port'] = isset($_POST['db_port']) ? (string) $_POST['db_port'] : '3306';
    $config['conn.db_name'] = isset($_POST['db_name']) ? (string) $_POST['db_name'] : '';
    $config['conn.db_user'] = isset($_POST['db_user']) ? (string) $_POST['db_user'] : '';
    $config['conn.db_pass'] = isset($_POST['db_pass']) ? (string) $_POST['db_pass'] : '';
} elseif ($connection_mode === 'api') {
    $config['conn.api_url'] = isset($_POST['api_url']) ? (string) $_POST['api_url'] : '';
    $config['auth.app_token'] = isset($_POST['app_token']) ? (string) $_POST['app_token'] : '';
    $config['auth.user_token'] = isset($_POST['user_token']) ? (string) $_POST['user_token'] : '';
}

$result = xmlrpc_itsmsync_test_connection($itsm_type, $connection_mode, $config);
if (!is_array($result)) {
    $result = array('success' => false, 'message' => 'Invalid backend response');
}

if ($client_id !== '' && in_array($connection_mode, array('api', 'db'), true)) {
    $signature = itsmsync_connection_signature($connection_mode, $_POST);
    $marker = array(
        'conn.test_mode' => $connection_mode,
        'conn.test_signature' => $signature,
        'conn.test_ok' => (!empty($result['success']) ? '1' : '0'),
        'conn.test_at' => gmdate('Y-m-d H:i:s'),
        'enabled' => (!empty($result['success']) ? '1' : '0'),
        'conn.test_hash' => '',
    );
    xmlrpc_itsmsync_save_client_config($client_id, $marker);
}

itsmsync_json_response($result, 200);
