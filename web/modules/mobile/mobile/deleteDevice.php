<?php
require_once("modules/mobile/includes/xmlrpc.php");

$deviceId = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($deviceId <= 0) {
    new NotifyWidgetFailure(_T("Invalid device ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

// Get device info for confirmation
$devices = xmlrpc_get_hmdm_devices();
$device = null;
foreach ($devices as $d) {
    if (isset($d['id']) && $d['id'] == $deviceId) {
        $device = $d;
        break;
    }
}

if (!$device) {
    new NotifyWidgetFailure(_T("Device not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$deviceNumber = $device['number'] ?? _T("Unknown", "mobile");

if (isset($_POST['bdelete'])) {
    $result = xmlrpc_delete_hmdm_device_by_id($deviceId);
    
    if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Device '%s' successfully deleted", "mobile"), $deviceNumber));
    } else {
        new NotifyWidgetFailure(sprintf(_T("Failed to delete device '%s'", "mobile"), $deviceNumber));
    }
    
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
} else {
    $f = new PopupForm(_T("Delete Device", "mobile"));
    $f->addText(sprintf(_T("Are you sure you want to delete the device <b>%s</b>?", "mobile"), htmlspecialchars($deviceNumber)));
    
    $description = $device['description'] ?? '';
    if (!empty($description)) {
        $f->addText(sprintf(_T("Description: %s", "mobile"), htmlspecialchars($description)));
    }
    
    $f->addText('<br><strong style="color: #d9534f;">' . _T("Warning: This action cannot be undone!", "mobile") . '</strong>');
    
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $deviceId, "hide" => true));
    
    $f->addValidateButton("bdelete");
    $f->addCancelButton("bback");
    $f->display();
}
?>
