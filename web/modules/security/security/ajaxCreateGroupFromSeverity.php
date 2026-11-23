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
require_once("modules/security/includes/html.inc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

$severity = SecurityFilter::severity();
$location = SecurityFilter::location();
$platform = SecurityFilter::platform();
$exploitedOnly = SecurityFilter::exploitedOnly();
$filter = $_GET['filter'] ?? '';
$filter = is_string($filter) ? trim($filter) : '';

if ($severity === null) {
    new NotifyWidgetFailure(_T("Invalid severity level", "security"));
    exit;
}

$severityLabels = array(
    'Critical' => _T("Critical", "security"),
    'High' => _T("High", "security"),
    'Medium' => _T("Medium", "security"),
    'Low' => _T("Low", "security")
);
$severityLabel = isset($severityLabels[$severity]) ? $severityLabels[$severity] : $severity;

// Handle confirmation
if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);
    $redirect = urlStrRedirect("security/security/index", []);
    // Get machines affected by this severity
    $machinesData = xmlrpc_get_machines_by_severity($severity, $location, $platform, $exploitedOnly, $filter);

    if (empty($machinesData)) {
        new NotifyWidgetFailure(_T("No machines found with this severity level", "security"));
    } else {
        $nameParts = array_filter(array(
            $severityLabel,
            SecurityFilter::platformLabel($platform),
            $exploitedOnly ? mb_strtolower(_T("Exploited", "security")) : '',
            $filter !== '' ? '"' . mb_substr($filter, 0, 30) . '"' : ''
        ), 'strlen');
        $groupName = sprintf("CVE %s - %s", implode(' ', $nameParts), date('Y-m-d H:i'));

        // Create static group (type = 0)
        $group = new Group();
        $group->type = 0; // Static group
        $groupId = $group->create($groupName, false); // false = not in favorites

        if ($groupId) {
            // Add machines to the group using miniAddMembers
            $result = $group->miniAddMembers($machinesData);

            if ($result && $result[0]) {
                $msg = sprintf(
                    count($machinesData) == 1
                        ? _T("Group '%s' created with %d machine", "security")
                        : _T("Group '%s' created with %d machines", "security"),
                    htmlspecialchars($groupName, ENT_QUOTES, 'UTF-8'),
                    count($machinesData)
                );
                new NotifyWidgetSuccess($msg);
                if (hasCorrectAcl("security", "security", "groupDetail")) {
                    $redirect = urlStrRedirect("security/security/groupDetail", array(
                        'group_id' => intval($groupId),
                        'group_name' => $groupName,
                        'back' => SecurityFilter::back()
                    ));
                }
            } else {
                new NotifyWidgetFailure(_T("Group created but failed to add machines", "security"));
            }
        } else {
            new NotifyWidgetFailure(_T("Failed to create group", "security"));
        }
    }

    header("Location: " . $redirect);
    exit;
}

// Get machine count for this severity
$machinesData = xmlrpc_get_machines_by_severity($severity, $location, $platform, $exploitedOnly, $filter);
$machineCount = count($machinesData);

// Show confirmation popup
$title = _T("Create Group from CVE Severity", "security");
$f = new PopupForm($title);

if ($machineCount > 0) {
    $f->addText("<p>" . sprintf(
        $machineCount == 1
            ? _T("Create a static group with <strong>%d machine</strong> affected by <strong>%s</strong> severity CVEs?", "security")
            : _T("Create a static group with <strong>%d machines</strong> affected by <strong>%s</strong> severity CVEs?", "security"),
        $machineCount,
        $severityLabel
    ) . "</p>");

    $f->addValidateButtonWithValue("bconfirm", _T("Create Group", "security"));
} else {
    $f->addText("<p>" . _T("No machines found with this severity level.", "security") . "</p>");
}

$f->addCancelButton("bback");
$f->display();
?>
