<?php
require_once("modules/mobile/includes/xmlrpc.php");

$photoId = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($photoId <= 0) {
    new NotifyWidgetFailure(_T("Invalid photo ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/photosList"));
    exit;
}

if (isset($_POST['bconfirm'])) {
    $result = xmlrpc_delete_photo($photoId);

    if ($result && isset($result['status']) && strtoupper($result['status']) === 'OK') {
        new NotifyWidgetSuccess(_T("Photo deleted successfully", "mobile"));
    } else {
        new NotifyWidgetFailure(_T("Failed to delete photo", "mobile"));
    }

    header("Location: " . urlStrRedirect("mobile/mobile/photosList"));
    exit;
} else {
    $f = new PopupForm(_T("Delete this photo", "mobile"));
    $f->setLevel('danger');

    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $photoId, "hide" => true));

    $f->addDangerButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
