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
    
    // Handle dict response with error and message fields
    if (is_array($result) && !$result['error']) {
        new NotifyWidgetSuccess(sprintf(_T("Application %s successfully deleted", "mobile"), $name));
        header("location:" . urlStrRedirect("mobile/mobile/applications"));
        exit;
    } else {
        // Extract error message if available
        $errorMsg = is_array($result) && isset($result['message']) 
            ? $result['message'] 
            : _T("Unknown error", "mobile");
        
        // Translate specific HMDM error messages
        if ($errorMsg === "error.application.config.reference.exists") {
            $errorMsg = _T("Cannot delete application: it is referenced in one or more configurations. Remove it from configurations first.", "mobile");
        }
        
        new NotifyWidgetFailure(sprintf(_T("Error deleting application %s: %s", "mobile"), $name, $errorMsg));
        header("location:" . urlStrRedirect("mobile/mobile/applications"));
        exit;
    }
}

?>
