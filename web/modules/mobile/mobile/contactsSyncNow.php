<?php
require_once("modules/mobile/includes/xmlrpc.php");

$configId = isset($_GET['id']) ? intval($_GET['id']) : (isset($_POST['id']) ? intval($_POST['id']) : 0);
if ($configId <= 0) {
    $f = new PopupForm(_T("Contacts Sync", "mobile"));
    $f->setLevel('danger');
    $f->addText(_T("Invalid configuration ID.", "mobile"));
    $f->addValidateButtonWithFade("bclose");
    $f->display();
    exit;
}

if (!isset($_POST['bconfirm'])) {
    $f = new PopupForm(_T("Sync contacts now?", "mobile"));
    $f->setLevel('default');
    $f->addText(_T("This will send a syncContacts push to all devices in this configuration.", "mobile"));
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $configId, "hide" => true));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
    exit;
}

verifyCSRFToken($_POST);

$result = xmlrpc_send_hmdm_push_message('configuration', 'syncContacts', '', '', '', $configId);

if ($result && isset($result['status']) && strtoupper($result['status']) === 'OK') {
    $f = new PopupForm(_T("Contacts Sync", "mobile"));
    $f->setLevel('success');
    $f->addText(_T("A <strong>syncContacts</strong> push has been sent to all devices in this configuration.", "mobile"));
    $f->addText(_T("Devices will re-import contacts from the configured VCF URL shortly.", "mobile"));
} else {
    $f = new PopupForm(_T("Contacts Sync", "mobile"));
    $f->setLevel('danger');
    $f->addText(_T("Failed to send sync push to devices.", "mobile"));
    $f->addText(_T("Please check the mmc-agent logs.", "mobile"));
}

$f->addValidateButtonWithFade("bclose");
$f->display();
?>
