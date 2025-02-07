<?php

// Check if convergence is defined and is worth 1
if (isset($_GET['convergence']) && $_GET['convergence'] == 1) {
    $cmd_id = $_GET['cmd_id'];
    xmlrpc_convergence_reschedule($cmd_id);
    header("location: " . urlStrRedirect($_GET['module'] . '/' . $_GET['submod'] . '/' . $_GET['previous']));
    new NotifyWidgetSuccess(_T("Convergence has been successfully rescheduled !"));
    exit;
} else {
    header("location: " . urlStrRedirect($_GET['module'] . '/' . $_GET['submod'] . '/' . $_GET['previous']));
    new NotifyWidgetFailure(_T("An error occurred while rescheduling convergence !"));
    exit;
}