<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get pagination parameters
$page_num = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$page_size = isset($_GET['pagesize']) ? (int)$_GET['pagesize'] : 50;
$message_filter = isset($_GET['message']) ? $_GET['message'] : "";
$user_filter = isset($_GET['user']) ? $_GET['user'] : "";

// Fetch audit logs
$audit_logs = xmlrpc_get_hmdm_audit_logs($page_size, $page_num, $message_filter, $user_filter);
?>

<h3><?php echo _T("Audit Logs", "mobile"); ?></h3>
<p><?php echo _T("Audit log records from HMDM", "mobile"); ?></p>

<div id='audit-logs-container'>
    <?php if (is_array($audit_logs) && count($audit_logs) > 0): ?>
        <table class="listinfos" cellspacing="0">
            <thead>
                <tr>
                    <td><?php echo _T("Date and time", "mobile"); ?></td>
                    <td><?php echo _T("User login", "mobile"); ?></td>
                    <td><?php echo _T("IP Address", "mobile"); ?></td>
                    <td><?php echo _T("Action", "mobile"); ?></td>
                    <td><?php echo _T("Details", "mobile"); ?></td>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($audit_logs as $log): ?>
                    <tr>
                        <td><?php echo isset($log['date']) ? htmlspecialchars($log['date']) : '-'; ?></td>
                        <td><?php echo isset($log['login']) ? htmlspecialchars($log['login']) : '-'; ?></td>
                        <td><?php echo isset($log['ip']) ? htmlspecialchars($log['ip']) : '-'; ?></td>
                        <td><?php echo isset($log['action']) ? htmlspecialchars($log['action']) : '-'; ?></td>
                        <td><?php echo _T("Details", "mobile"); ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    <?php else: ?>
        <div class="info-box">
            <?php echo _T("No audit logs found", "mobile"); ?>
        </div>
    <?php endif; ?>
</div>

<?php

