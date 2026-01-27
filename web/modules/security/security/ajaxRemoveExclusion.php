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
 * Security Module - AJAX Remove Exclusion Popup
 */

require_once("modules/security/includes/xmlrpc.php");

$name = $_GET['name'] ?? '';
$type = $_GET['type'] ?? '';  // 'software' or 'cve'

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

if (isset($_POST['bconfirm'])) {
    // Get current policies
    $policies = xmlrpc_get_policies();

    // Determine which exclusion list to modify
    if ($type === 'software') {
        $exclusionKey = 'names';
    } elseif ($type === 'cve') {
        $exclusionKey = 'cve_ids';
    } else {
        new NotifyWidgetFailure(_T("Invalid exclusion type", "security"));
        header("Location: " . urlStrRedirect("security/security/settings"));
        exit;
    }

    // Remove the item from exclusions
    $currentExclusions = $policies['exclusions'][$exclusionKey] ?? array();
    $newExclusions = array_values(array_filter($currentExclusions, function($item) use ($name) {
        return $item !== $name;
    }));

    // Build updated policies (only exclusions, keep display as-is)
    $updatedPolicies = array(
        'display' => $policies['display'],
        'exclusions' => array(
            'vendors' => $policies['exclusions']['vendors'] ?? array(),
            'names' => $exclusionKey === 'names' ? $newExclusions : ($policies['exclusions']['names'] ?? array()),
            'cve_ids' => $exclusionKey === 'cve_ids' ? $newExclusions : ($policies['exclusions']['cve_ids'] ?? array())
        )
    );

    $result = xmlrpc_set_policies($updatedPolicies, $currentUser);
    if ($result === true || $result === 1) {
        new NotifyWidgetSuccess(sprintf(_T("'%s' removed from exclusions", "security"), $name));
    } else {
        new NotifyWidgetFailure(_T("Failed to remove exclusion", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings"));
    exit;
}

// Show confirmation popup
if ($type === 'software') {
    $title = _T("Remove Software Exclusion", "security");
    $message = sprintf(_T("Remove '%s' from excluded software?", "security"), htmlspecialchars($name));
} else {
    $title = _T("Remove CVE Exclusion", "security");
    $message = sprintf(_T("Remove '%s' from excluded CVEs?", "security"), htmlspecialchars($name));
}

$f = new PopupForm($title);
$f->addText("<br/>" . $message . "<br/><br/>");
$f->addValidateButton("bconfirm", _T("Remove", "security"));
$f->addCancelButton("bback");
$f->display();
?>
