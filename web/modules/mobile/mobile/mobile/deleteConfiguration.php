<?php
require_once("modules/mobile/includes/xmlrpc.php");

$name = "";
$id = 0;

if (isset($_GET['name'])) {
    $name = htmlentities($_GET['name']);
}

if (isset($_GET['id'])) {
    $id = htmlentities($_GET['id']);
} else {
    new NotifyWidgetFailure(_T("Missing parameter id", "mobile"));
    header("location:" . urlStrRedirect("mobile/mobile/configurations"));
    exit;
}

if (isset($_GET['action']) && $_GET['action'] === 'deleteConfiguration') {
    $result = xmlrpc_delete_configuration_by_id($_GET['id']);
        if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Configuration %s successfully deleted", "mobile"), $name));
        header("location:" . urlStrRedirect("mobile/mobile/configurations"));
        exit;
    } else {
        new NotifyWidgetFailure(sprintf(_T("Impossible to delete configuration %s", "mobile"), $name));
        header("location:" . urlStrRedirect("mobile/mobile/configurations"));
        exit;
    }
}

?>
