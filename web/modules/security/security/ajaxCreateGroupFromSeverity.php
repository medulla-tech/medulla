<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Security Module - AJAX Create Group from Severity
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

$severity = isset($_GET['severity']) ? $_GET['severity'] : '';
$location = isset($_GET['location']) ? $_GET['location'] : '';

// Validate severity
$validSeverities = array('Critical', 'High', 'Medium', 'Low');
if (!in_array($severity, $validSeverities)) {
    new NotifyWidgetFailure(_T("Invalid severity level", "security"));
    exit;
}

// Handle confirmation
if (isset($_POST['bconfirm'])) {
    // Get machines affected by this severity
    $machinesData = xmlrpc_get_machines_by_severity($severity, $location);

    if (empty($machinesData)) {
        new NotifyWidgetFailure(_T("No machines found with this severity level", "security"));
    } else {
        // Generate automatic group name: CVE <Severity> - YYYY-MM-DD HH:MM
        $groupName = sprintf("CVE %s - %s", $severity, date('Y-m-d H:i'));

        // Create static group (type = 0)
        $group = new Group();
        $group->type = 0; // Static group
        $groupId = $group->create($groupName, true); // true = visible

        if ($groupId) {
            // Add machines to the group using miniAddMembers
            $result = $group->miniAddMembers($machinesData);

            if ($result && $result[0]) {
                $msg = sprintf(
                    _T("Group '%s' created with %d machines", "security"),
                    $groupName,
                    count($machinesData)
                );
                new NotifyWidgetSuccess($msg);
            } else {
                new NotifyWidgetFailure(_T("Group created but failed to add machines", "security"));
            }
        } else {
            new NotifyWidgetFailure(_T("Failed to create group", "security"));
        }
    }

    // Redirect to security index
    header("Location: " . urlStrRedirect("security/security/index", []));
    exit;
}

// Get machine count for this severity
$machinesData = xmlrpc_get_machines_by_severity($severity, $location);
$machineCount = count($machinesData);

// Severity labels for display
$severityLabels = array(
    'Critical' => _T("Critical", "security"),
    'High' => _T("High", "security"),
    'Medium' => _T("Medium", "security"),
    'Low' => _T("Low", "security")
);
$severityLabel = isset($severityLabels[$severity]) ? $severityLabels[$severity] : $severity;

// Show confirmation popup
$title = _T("Create Group from CVE Severity", "security");
$f = new PopupForm($title);

if ($machineCount > 0) {
    $f->addText("<p>" . sprintf(
        _T("Create a static group with <strong>%d machines</strong> affected by <strong>%s</strong> severity CVEs?", "security"),
        $machineCount,
        $severityLabel
    ) . "</p>");

    $f->addValidateButton("bconfirm", _T("Create Group", "security"));
} else {
    $f->addText("<p>" . _T("No machines found with this severity level.", "security") . "</p>");
}

$f->addCancelButton("bback");
$f->display();
?>
