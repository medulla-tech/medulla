<?php
require_once("modules/mobile/includes/xmlrpc.php");

$id = isset($_GET['id']) ? $_GET['id'] : '';
$name = isset($_GET['name']) ? $_GET['name'] : '';

if (empty($id)) {
    new NotifyWidgetFailure(_T("File ID is missing", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
}

// Get the full file data to check if it's used by configurations
$files = xmlrpc_get_hmdm_files();
if (!is_array($files)) { $files = []; }

$file = null;
foreach ($files as $f) {
    if ((string)($f['id'] ?? '') === (string)$id) {
        $file = $f;
        break;
    }
}

if (!$file) {
    new NotifyWidgetFailure(_T("File not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
}

// Check if file is used by configurations
$usedByConfigs = $file['usedByConfigurations'] ?? [];
if (!empty($usedByConfigs) && is_array($usedByConfigs)) {
    // usedByConfigurations is an array of configuration names (strings)
    $configNames = array_filter($usedByConfigs, function($name) {
        return !empty($name) && is_string($name);
    });
    
    if (empty($configNames)) {
        // If we filtered everything out, continue with deletion
        goto allow_deletion;
    }
    
    $f = new PopupForm(_T("Cannot Delete File", "mobile"));
    $f->addText(sprintf(
        _T("The file <b>%s</b> cannot be deleted because it is used by the following configuration(s):", "mobile"),
        htmlspecialchars($name)
    ));
    $f->addText("<ul><li>" . implode("</li><li>", array_map('htmlspecialchars', $configNames)) . "</li></ul>");
    $f->addCancelButton("bback");
    $f->display();
    exit;
}

allow_deletion:

if (isset($_POST['bdelete'])) {
    $result = xmlrpc_delete_file_by_id($file);
    
    if (is_array($result) && $result['status'] === 'OK') {
        new NotifyWidgetSuccess(sprintf(_T("File '%s' successfully deleted", "mobile"), $name));
    } else {
        $errorMsg = is_array($result) ? ($result['message'] ?? 'Unknown error') : 'Unknown error';
        new NotifyWidgetFailure(sprintf(_T("Failed to delete file '%s': %s", "mobile"), $name, $errorMsg));
    }
    
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
} else {
    $f = new PopupForm(_T("Delete File", "mobile"));
    $f->addText(sprintf(_T("Are you sure you want to delete the file <b>%s</b>?", "mobile"), htmlspecialchars($name)));
    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => true));
    $hidden_name = new HiddenTpl("name");
    $f->add($hidden_name, array("value" => $name, "hide" => true));
    $f->addValidateButton("bdelete");
    $f->addCancelButton("bback");
    $f->display();
}

?>
