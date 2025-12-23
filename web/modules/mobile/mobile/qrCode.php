<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceNumber = isset($_REQUEST['device_number']) ? $_REQUEST['device_number'] : '';
$configId = isset($_REQUEST['configuration_id']) ? intval($_REQUEST['configuration_id']) : 1;

if (!$deviceNumber) {
    http_response_code(400);
    echo "<html><body><p>" . _T("Missing device number", "mobile") . "</p></body></html>";
    exit;
}

// Fetch QR code key for the configuration
$qrKey = xmlrpc_get_hmdm_configuration_by_id($configId);
if (empty($qrKey)) {
    http_response_code(500);
    echo "<html><body><p>" . _T("Unable to fetch configuration QR key", "mobile") . "</p></body></html>";
    exit;
}

$url = "/hmdm/rest/public/qr/" . urlencode($qrKey) . "?deviceId=" . urlencode($deviceNumber);
header("Location: " . $url);
exit;
