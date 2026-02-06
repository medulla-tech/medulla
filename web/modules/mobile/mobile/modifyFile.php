<?php

require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$fileId = isset($_GET['id']) ? $_GET['id'] : '';
$files = xmlrpc_get_hmdm_files();
if (!is_array($files)) { $files = []; }

$file = null;
foreach ($files as $f) {
    if ((string)($f['id'] ?? '') === (string)$fileId) { $file = $f; break; }
}

if (!$file) {
    new NotifyWidgetFailure(_T("File not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$p = new PageGenerator(_T("Modify File", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$external = !empty($file['external']);
$filePath = $file['filePath'] ?? '';
$name = $external ? $filePath : basename($filePath);
$description = $file['description'] ?? '';
$devicePath = $file['devicePath'] ?? '';
$variableContent = !empty($file['replaceVariables']);

if (isset($_POST['bconfirm'])) {
    // Get the updated filename/URL
    $newFileName = $_POST['file_name'] ?? '';
    $filePath = !empty($newFileName) ? $newFileName : $file['filePath'];
    
    // Debug logging
    error_log("POST file_name: " . var_export($_POST['file_name'] ?? 'NOT SET', true));
    error_log("Calculated filePath: " . var_export($filePath, true));
    
    // Build minimal update payload
    $updateData = array(
        'id' => $fileId,
        'filePath' => $filePath,
        'replaceVariables' => isset($_POST['variable_content']),
        'description' => $_POST['description'] ?? '',
        'devicePath' => $_POST['path_device'] ?? '',
    );
    
    error_log("Update data being sent: " . var_export($updateData, true));
    
    $result = xmlrpc_update_hmdm_file($updateData);
    if ($result) {
        new NotifyWidgetSuccess(_T("Changes saved successfully", "mobile"));
    } else {
        new NotifyWidgetFailure(_T("Failed to save changes", "mobile"));
    }
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
}

$f = new ValidatingForm();
$f->push(new Table());

$f->add(new TrFormElement(_T("Description", "mobile"), new InputTpl("description")));
$f->add(new TrFormElement(_T("External", "mobile"), new CheckboxTpl("external")));
$fileNameLabel = $external ? _T("URL", "mobile") : _T("File name", "mobile");
$f->add(new TrFormElement($fileNameLabel, new InputTpl("file_name")));
$f->add(new TrFormElement(_T("Path on device", "mobile"), new InputTpl("path_device")));
$f->add(new TrFormElement(_T("Variable content", "mobile"), new CheckboxTpl("variable_content")));

$f->pop();
$f->addButton("bconfirm", _T("Save", "mobile"));
$f->display();
?>

<script type="text/javascript">
jQuery(function() {
    jQuery('input[name="description"]').val(<?php echo json_encode($description); ?>);
    jQuery('input[name="external"]').prop('checked', <?php echo $external ? 'true' : 'false'; ?>).prop('disabled', true);
    jQuery('input[name="file_name"]').val(<?php echo json_encode($name); ?>);
    jQuery('input[name="path_device"]').val(<?php echo json_encode($devicePath); ?>);
    jQuery('input[name="variable_content"]').prop('checked', <?php echo $variableContent ? 'true' : 'false'; ?>);
    
    //cancel button
    jQuery('input[name="bconfirm"]').after('<input type="button" class="btnSecondary" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="location.href=\'main.php?module=mobile&submod=mobile&action=files\';" />');
});
</script>
