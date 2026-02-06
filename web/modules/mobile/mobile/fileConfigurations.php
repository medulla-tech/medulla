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
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
}

$p = new PageGenerator(_T("Assign Configurations to File", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$name = basename($file['filePath'] ?? '');
$usedByConfigs = $file['usedByConfigurations'] ?? [];

$configs = xmlrpc_get_hmdm_configurations();
if (!is_array($configs)) { $configs = []; }

if (isset($_POST['bconfirm'])) {
    // Collect selected configuration IDs
    $selectedConfigIds = [];
    foreach ($configs as $cfg) {
        $cid = $cfg['id'] ?? '';
        if (isset($_POST['config_' . $cid])) {
            $selectedConfigIds[] = (int)$cid;
        }
    }
    
    // Call the configuration linking function
    $result = xmlrpc_assign_file_to_configurations($fileId, $selectedConfigIds);
    
    if ($result && (!is_array($result) || $result['status'] !== 'ERROR')) {
        new NotifyWidgetSuccess(_T("Configurations assigned successfully", "mobile"));
    } else {
        $errorMsg = is_array($result) ? ($result['message'] ?? 'Unknown error') : 'Unknown error';
        new NotifyWidgetFailure(sprintf(_T("Failed to assign configurations: %s", "mobile"), $errorMsg));
    }
    header("Location: " . urlStrRedirect("mobile/mobile/files"));
    exit;
}

$f = new ValidatingForm();
$f->push(new Table());

$f->add(new TrFormElement(_T("File name", "mobile"), new SpanElement(htmlspecialchars($name))));

$configCheckboxes = '';
foreach ($configs as $cfg) {
    $cid = $cfg['id'] ?? '';
    $cname = htmlspecialchars($cfg['name'] ?? ('#'.$cid));
    $checked = in_array($cname, $usedByConfigs) ? 'checked' : '';
    $configCheckboxes .= "<label style='display:block;margin:5px 0;'><input type='checkbox' name='config_{$cid}' value='1' {$checked} /> {$cname}</label>";
}

if (empty($configCheckboxes)) {
    $configCheckboxes = '<em>' . _T("No configurations available", "mobile") . '</em>';
}

$f->add(new TrFormElement(_T("Configurations", "mobile"), new SpanElement($configCheckboxes, "pkgs")));

$f->pop();
$f->addButton("bconfirm", _T("Save", "mobile"));
$f->display();
?>

<script type="text/javascript">
jQuery(function() {
    // Add cancel button after the save button
    jQuery('input[name="bconfirm"]').after('<input type="button" class="btnSecondary" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="location.href=\'main.php?module=mobile&submod=mobile&action=files\';" />');
});
</script>
