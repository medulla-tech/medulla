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
require_once("modules/security/includes/html.inc.php");

// Determine the type of exclusion and set parameters
$exclusionTypes = array(
    'software' => array(
        'param' => $_GET['software_name'] ?? '',
        'key' => 'names',
        'redirect' => 'security/security/index',
        'title' => _T("Exclude Software", "security"),
        'message' => _T("Add '%s' to excluded software?", "security"),
        'subMessage' => _T("All versions of this software will no longer appear in CVE reports.", "security")
    ),
    'cve' => array(
        'param' => $_GET['cve_id'] ?? '',
        'key' => 'cve_ids',
        'redirect' => 'security/security/allcves',
        'title' => _T("Exclude CVE", "security"),
        'message' => _T("Add '%s' to excluded CVEs?", "security"),
        'subMessage' => _T("This CVE will no longer appear in reports.", "security")
    ),
    'machine' => array(
        'param' => $_GET['machine_id'] ?? '',
        'name' => $_GET['machine_name'] ?? '',
        'key' => 'machines_ids',
        'redirect' => 'security/security/machines',
        'title' => _T("Exclude Machine", "security"),
        'message' => _T("Add '%s' to excluded machines?", "security"),
        'subMessage' => _T("This machine will no longer appear in CVE reports and dashboard counts.", "security"),
        'isInt' => true
    ),
    'group' => array(
        'param' => $_GET['group_id'] ?? '',
        'name' => $_GET['group_name'] ?? '',
        'key' => 'groups_ids',
        'redirect' => 'security/security/groups',
        'title' => _T("Exclude Group", "security"),
        'message' => _T("Add '%s' to excluded groups?", "security"),
        'subMessage' => _T("This group will no longer appear in CVE reports.", "security"),
        'isInt' => true
    )
);

// Find which exclusion type is being used
$type = null;
$config = null;
foreach ($exclusionTypes as $key => $cfg) {
    if (!empty($cfg['param'])) {
        $type = $key;
        $config = $cfg;
        break;
    }
}

$currentUser = $_SESSION['login'] ?? 'unknown';

if (isset($_POST['bconfirm']) && $config) {
    $value = isset($config['isInt']) ? intval($config['param']) : $config['param'];
    $itemName = isset($config['name']) && !empty($config['name']) ? $config['name'] : $config['param'];

    $success = ExclusionHelper::addExclusion($config['key'], $value, $currentUser);

    if ($success) {
        new NotifyWidgetSuccess(sprintf(_T("'%s' added to exclusions", "security"), $itemName));
    } else {
        new NotifyWidgetFailure(_T("Failed to add exclusion", "security"));
    }

    header("Location: " . urlStrRedirect($config['redirect']));
    exit;
}

// Show confirmation popup
if ($config) {
    $displayName = isset($config['name']) && !empty($config['name']) ? $config['name'] : $config['param'];
    $title = $config['title'];
    $message = sprintf($config['message'], htmlspecialchars($displayName));
    $subMessage = $config['subMessage'];
} else {
    $title = _T("Exclude", "security");
    $message = _T("Invalid exclusion request", "security");
    $subMessage = "";
}

$f = new PopupForm($title);
$f->addText("<br/>" . $message . "<br/><br/>");
$f->addText("<em>" . $subMessage . "</em><br/><br/>");
$f->addValidateButton("bconfirm", _T("Exclude", "security"));
$f->addCancelButton("bback");
$f->display();
?>
