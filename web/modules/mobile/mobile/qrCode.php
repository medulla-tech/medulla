<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceNumber = isset($_REQUEST['device_number']) ? $_REQUEST['device_number'] : '';
$configId = isset($_REQUEST['configuration_id']) ? intval($_REQUEST['configuration_id']) : 1;

if (!$deviceNumber) {
    header("Location: " . urlStrRedirect("mobile/mobile/index", array("error" => "missing_device_number")));
    exit;
}

// Fetch QR code key for the configuration
$qrKey = xmlrpc_get_hmdm_configuration_by_id($configId);
if (empty($qrKey) || !is_array($qrKey) || empty($qrKey['qrCodeKey'])) {
    header("Location: " . urlStrRedirect("mobile/mobile/index", array("error" => "qr_key_missing")));
    exit;
}

$url = "/hmdm/rest/public/qr/" . urlencode($qrKey['qrCodeKey']) . "?deviceId=" . urlencode($deviceNumber);
header("Location: " . $url);
exit;
