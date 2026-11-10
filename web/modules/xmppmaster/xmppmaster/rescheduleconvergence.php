<?php

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    exit;
}

verifyCSRFToken($_POST);

// Check if convergence is defined and is worth 1
if (isset($_POST['convergence']) && $_POST['convergence'] == 1) {
    $cmd_id = $_POST['cmd_id'];
    xmlrpc_convergence_reschedule($cmd_id);
    header("location: " . urlStrRedirect($_GET['module'] . '/' . $_GET['submod'] . '/' . $_POST['previous']));
    new NotifyWidgetSuccess(_T("Convergence has been successfully rescheduled.", "xmppmaster"));
    exit;
} else {
    header("location: " . urlStrRedirect($_GET['module'] . '/' . $_GET['submod'] . '/' . $_POST['previous']));
    new NotifyWidgetFailure(_T("An error occurred while rescheduling convergence.", "xmppmaster"));
    exit;
}
