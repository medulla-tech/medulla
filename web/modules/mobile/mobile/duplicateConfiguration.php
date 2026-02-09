<?php
/**
 * Duplicate Configuration
 * Creates a copy of an existing configuration with a new name
 */
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/imaging/includes/class_form.php");

$p = new PageGenerator(_T("Duplicate Configuration", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$config_id = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($config_id <= 0) {
    new NotifyWidgetFailure(_T("Invalid configuration ID", "mobile"));
    echo '<p><a href="' . urlStrRedirect("mobile/mobile/configurations") . '">' . _T("Back to configurations", "mobile") . '</a></p>';
    exit;
}

// Get original configuration
$originalConfig = xmlrpc_get_hmdm_configuration_by_id($config_id);

if (!$originalConfig) {
    new NotifyWidgetFailure(_T("Configuration not found", "mobile"));
    echo '<p><a href="' . urlStrRedirect("mobile/mobile/configurations") . '">' . _T("Back to configurations", "mobile") . '</a></p>';
    exit;
}

$originalName = $originalConfig['name'] ?? '';
$originalDescription = $originalConfig['description'] ?? '';

// Handle form submission
if (isset($_POST['bconfirm'])) {
    $newName = isset($_POST['name']) ? trim($_POST['name']) : '';
    $newDescription = isset($_POST['description']) ? trim($_POST['description']) : '';
    
    if (empty($newName)) {
        new NotifyWidgetFailure(_T("Configuration name is required", "mobile"));
    } else {
        $result = xmlrpc_copy_hmdm_configuration($config_id, $newName, $newDescription);
        
        if ($result && isset($result['status']) && $result['status'] === 'OK') {
            new NotifyWidgetSuccess(_T("Configuration duplicated successfully", "mobile"));
            header("Location: " . urlStrRedirect("mobile/mobile/configurations"));
            exit;
        } else {
            $errorMsg = isset($result['message']) ? $result['message'] : _T("Failed to duplicate configuration", "mobile");
            new NotifyWidgetFailure($errorMsg);
        }
    }
}

// Build the form
$form = new Form();
$form->push(new Table());

// Display original configuration info
$infoSpan = new SpanElement(sprintf(_T("Duplicating configuration: %s", "mobile"), '<strong>' . htmlspecialchars($originalName) . '</strong>'));
$form->add(new TrFormElement('', $infoSpan));

$nameInput = new InputTpl('name', '/^.{1,255}$/');
$form->add(new TrFormElement(_T('New configuration name', 'mobile'), $nameInput));

$descTextarea = new TextareaTpl('description');
$descTextarea->setRows(4);
$form->add(new TrFormElement(_T('Description', 'mobile'), $descTextarea), array("value" => $originalDescription));

$form->add(new HiddenTpl('config_id', $config_id));

$form->addValidateButton('bconfirm', _T('Duplicate', 'mobile'));
$form->addCancelButton('bback');

$form->pop();
$form->display();

?>
