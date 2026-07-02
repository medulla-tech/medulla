<?php
require_once("modules/mobile/includes/xmlrpc.php");

$id   = isset($_REQUEST['id'])   ? intval($_REQUEST['id'])                : 0;
$name = isset($_REQUEST['name']) ? htmlspecialchars($_REQUEST['name'])    : '';

if ($id <= 0) {
    new NotifyWidgetFailure(_T("Missing parameter id", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

if (isset($_POST['bconfirm'])) {
    $result = xmlrpc_delete_application_by_id($id);

    if (is_array($result) && !$result['error']) {
        new NotifyWidgetSuccess(sprintf(_T("Application %s successfully deleted", "mobile"), $name));
    } else {
        $errorMsg = is_array($result) && isset($result['message'])
            ? $result['message']
            : _T("Unknown error", "mobile");

        if ($errorMsg === "error.application.config.reference.exists") {
            $errorMsg = _T("Cannot delete application: it is referenced in one or more configurations. Remove it from configurations first.", "mobile");
        }

        new NotifyWidgetFailure(sprintf(_T("Error deleting application %s: %s", "mobile"), $name, $errorMsg));
    }

    header("Location: " . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

$f = new PopupForm(sprintf(_T("Delete application \"%s\"?", "mobile"), $name));
$f->setLevel('danger');

$hidden_id = new HiddenTpl("id");
$f->add($hidden_id, array("value" => $id, "hide" => true));

$hidden_name = new HiddenTpl("name");
$f->add($hidden_name, array("value" => $name, "hide" => true));

$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>
