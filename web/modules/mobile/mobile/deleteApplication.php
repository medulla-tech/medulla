<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Simple delete handler for applications: calls xmlrpc wrapper and redirects back with notification.

$name = "";
$id = 0;

if (isset($_GET['name'])) {
    $name = htmlentities($_GET['name']);
}

if (isset($_GET['id'])) {
    $id = htmlentities($_GET['id']);
} else {
    new NotifyWidgetFailure(_T("Missing parameter id", "mobile"));
    header("location:" . urlStrRedirect("mobile/mobile/applications"));
    exit;
}

if (isset($_GET['action']) && $_GET['action'] === 'deleteApplication') {
    $result = xmlrpc_delete_application_by_id($_GET['id']);
    if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Application %s successfully deleted", "mobile"), $name));
        header("location:" . urlStrRedirect("mobile/mobile/applications"));
        exit;
    } else {
        new NotifyWidgetFailure(sprintf(_T("Impossible to delete application %s", "mobile"), $name));
        header("location:" . urlStrRedirect("mobile/mobile/applications"));
        exit;
    }
}

?>
