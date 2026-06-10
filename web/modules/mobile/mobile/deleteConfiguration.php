<?php
require_once("modules/mobile/includes/xmlrpc.php");

$id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$name = isset($_GET['name']) ? htmlentities($_GET['name']) : '';

if ($id <= 0) {
    new NotifyWidgetFailure(_T("Invalid configuration ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
    exit;
}

if (isset($_POST['bconfirm'])) {
    $configs = xmlrpc_get_hmdm_configurations();
    if (is_array($configs) && count($configs) <= 1) {
        new NotifyWidgetFailure(_T("Cannot delete the last configuration. Duplicate it first to create a new one.", "mobile"));
        header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
        exit;
    }

    $result = xmlrpc_delete_configuration_by_id($id);
    
    if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Configuration '%s' successfully deleted", "mobile"), $name));
    } else {
        new NotifyWidgetFailure(sprintf(_T("Failed to delete configuration '%s'", "mobile"), $name));
    }
    
    header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
    exit;
} else {
    $f = new PopupForm(sprintf(_T("Delete configuration '%s'?", "mobile"), $name));
    $f->setLevel('danger');

    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => true));

    $hidden_name = new HiddenTpl("name");
    $f->add($hidden_name, array("value" => $name, "hide" => true));

    $f->addDangerButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
