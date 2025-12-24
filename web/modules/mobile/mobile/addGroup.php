<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$errors = [];
$values = [
    'name' => ''
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    $values['name'] = trim($_POST['name'] ?? '');

    // Validation
    if ($values['name'] === '') {
        $errors['name'] = _T("Group name is required", "mobile");
    } elseif (!preg_match('/^[a-zA-Z0-9\s\-_]+$/', $values['name'])) {
        $errors['name'] = _T("Group name contains invalid characters", "mobile");
    }

    // If no errors, add the group
    if (empty($errors)) {
        $result = xmlrpc_add_hmdm_group($values['name']);
        
        if ($result && ((is_array($result) && isset($result['status']) && $result['status'] === 'OK') || isset($result['id']))) {
            new NotifyWidgetSuccess(sprintf(_T("Group '%s' successfully created", "mobile"), $values['name']));
            header("Location: " . urlStrRedirect("mobile/mobile/groups"));
            exit;
        } else {
            $error_msg = is_array($result) && isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
            new NotifyWidgetFailure(sprintf(_T("Failed to create group: %s", "mobile"), $error_msg));
        }
    } else {
        // Display validation errors
        foreach ($errors as $field => $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

$p = new PageGenerator(_T("Add a group", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$formAddGroup = new Form();
$formAddGroup->push(new Table());

// Group name
$formAddGroup->add(
    new TrFormElement(
        _T("Group name", 'mobile') . "*",
        new InputTpl('name', '/^[a-zA-Z0-9\s\-_]+$/', $values['name'])
    ),
    array(
        "value" => $values['name'],
        "placeholder" => _T("Enter group name", "mobile"),
        "required" => true
    )
);

// Validation button
$formAddGroup->addValidateButton("test", _T("Add", "mobile"));

// Display form
$formAddGroup->pop();
$formAddGroup->display();
?>
