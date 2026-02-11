<?php
require_once("modules/mobile/includes/xmlrpc.php");

$id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$name = isset($_GET['name']) ? htmlentities($_GET['name']) : '';

if ($id <= 0) {
    new NotifyWidgetFailure(_T("Invalid configuration ID", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
    exit;
}

if (isset($_POST['bdelete'])) {
    $result = xmlrpc_delete_configuration_by_id($id);
    
    if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Configuration '%s' successfully deleted", "mobile"), $name));
    } else {
        new NotifyWidgetFailure(sprintf(_T("Failed to delete configuration '%s'", "mobile"), $name));
    }
    
    header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
    exit;
} else {
    $f = new PopupForm(_T("Delete Configuration", "mobile"));
    $f->addText(sprintf(_T("Are you sure you want to delete the configuration <b>%s</b>?", "mobile"), htmlspecialchars($name)));
    $f->addText('<br><strong style="color: #d9534f;">' . _T("Warning: This action cannot be undone!", "mobile") . '</strong>');
    
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => true));
    
    $hidden_name = new HiddenTpl("name");
    $f->add($hidden_name, array("value" => $name, "hide" => true));
    
    $f->addValidateButton("bdelete");
    $f->addCancelButton("bback");
    $f->display();
}
?>
