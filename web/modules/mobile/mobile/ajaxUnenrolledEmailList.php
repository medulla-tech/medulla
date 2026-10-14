<?php
require_once("modules/mobile/includes/xmlrpc.php");

header('Content-Type: application/json');

$devices = xmlrpc_get_hmdm_devices();
if (!is_array($devices)) $devices = [];

$result = [];
foreach ($devices as $d) {
    $email = trim($d['custom1'] ?? '');
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) continue;

    // A device is considered not enrolled if it has never connected (no permissions data)
    $permissions = $d['info']['permissions'] ?? $d['permissions'] ?? null;
    if (is_array($permissions) && count($permissions) > 0) continue;

    $result[] = ['name' => $d['number'] ?? '', 'email' => $email];
}

echo json_encode($result);
