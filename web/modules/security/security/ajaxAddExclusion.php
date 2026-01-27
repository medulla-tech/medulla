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
 * Security Module - AJAX Add Exclusion Popup
 */

require_once("modules/security/includes/xmlrpc.php");

// Determine if it's a software or CVE exclusion
$softwareName = $_GET['software_name'] ?? '';
$softwareVersion = $_GET['software_version'] ?? '';
$cveId = $_GET['cve_id'] ?? '';

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

if (isset($_POST['bconfirm'])) {
    // Get current policies
    $policies = xmlrpc_get_policies();

    $success = false;
    $itemName = '';

    if (!empty($softwareName)) {
        // Add software to exclusions (by name only, excludes all versions)
        $itemName = $softwareName;

        $currentExclusions = $policies['exclusions']['names'] ?? array();
        if (!in_array($softwareName, $currentExclusions)) {
            $currentExclusions[] = $softwareName;

            // Build updated policies
            $updatedPolicies = array(
                'display' => $policies['display'],
                'exclusions' => array(
                    'vendors' => $policies['exclusions']['vendors'] ?? array(),
                    'names' => $currentExclusions,
                    'cve_ids' => $policies['exclusions']['cve_ids'] ?? array()
                )
            );

            $result = xmlrpc_set_policies($updatedPolicies, $currentUser);
            $success = ($result === true || $result === 1);
        } else {
            // Already excluded
            $success = true;
        }
    } elseif (!empty($cveId)) {
        // Add CVE to exclusions
        $itemName = $cveId;

        $currentExclusions = $policies['exclusions']['cve_ids'] ?? array();
        if (!in_array($cveId, $currentExclusions)) {
            $currentExclusions[] = $cveId;

            // Build updated policies
            $updatedPolicies = array(
                'display' => $policies['display'],
                'exclusions' => array(
                    'vendors' => $policies['exclusions']['vendors'] ?? array(),
                    'names' => $policies['exclusions']['names'] ?? array(),
                    'cve_ids' => $currentExclusions
                )
            );

            $result = xmlrpc_set_policies($updatedPolicies, $currentUser);
            $success = ($result === true || $result === 1);
        } else {
            // Already excluded
            $success = true;
        }
    }

    if ($success) {
        new NotifyWidgetSuccess(sprintf(_T("'%s' added to exclusions", "security"), $itemName));
    } else {
        new NotifyWidgetFailure(_T("Failed to add exclusion", "security"));
    }

    // Redirect back to the appropriate page
    if (!empty($softwareName)) {
        header("Location: " . urlStrRedirect("security/security/index"));
    } else {
        header("Location: " . urlStrRedirect("security/security/allcves"));
    }
    exit;
}

// Show confirmation popup
if (!empty($softwareName)) {
    $title = _T("Exclude Software", "security");
    $message = sprintf(_T("Add '%s' to excluded software?", "security"), htmlspecialchars($softwareName));
    $subMessage = _T("All versions of this software will no longer appear in CVE reports.", "security");
} else {
    $displayName = $cveId;
    $title = _T("Exclude CVE", "security");
    $message = sprintf(_T("Add '%s' to excluded CVEs?", "security"), htmlspecialchars($cveId));
    $subMessage = _T("This CVE will no longer appear in reports.", "security");
}

$f = new PopupForm($title);
$f->addText("<br/>" . $message . "<br/><br/>");
$f->addText("<em>" . $subMessage . "</em><br/><br/>");
$f->addValidateButton("bconfirm", _T("Exclude", "security"));
$f->addCancelButton("bback");
$f->display();
?>
