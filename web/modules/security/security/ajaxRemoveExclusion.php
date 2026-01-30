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
require_once("modules/security/includes/html.inc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

$name = $_GET['name'] ?? '';
$type = $_GET['type'] ?? '';

// Type configuration
$typeConfig = array(
    'software' => array('key' => 'names', 'tab' => 'tabsoftware', 'title' => _T("Remove Software Exclusion", "security")),
    'cve' => array('key' => 'cve_ids', 'tab' => 'tabcves', 'title' => _T("Remove CVE Exclusion", "security")),
    'vendor' => array('key' => 'vendors', 'tab' => 'tabvendors', 'title' => _T("Remove Vendor Exclusion", "security")),
    'machine' => array('key' => 'machines_ids', 'tab' => 'tabmachines', 'title' => _T("Remove Machine Exclusion", "security"), 'isInt' => true),
    'group' => array('key' => 'groups_ids', 'tab' => 'tabgroups', 'title' => _T("Remove Group Exclusion", "security"), 'isInt' => true)
);

if (!isset($typeConfig[$type])) {
    new NotifyWidgetFailure(_T("Invalid exclusion type", "security"));
    header("Location: " . urlStrRedirect("security/security/settings"));
    exit;
}

$config = $typeConfig[$type];
$displayName = $name;

// Resolve display name for machines and groups
if ($type === 'machine' && !empty($name)) {
    $machineId = intval($name);
    $machineFilter = array('uuids' => array('UUID' . $machineId));
    $machinesList = getRestrictedComputersList(0, 1, $machineFilter, False);
    if (!empty($machinesList) && is_array($machinesList)) {
        foreach ($machinesList as $machine) {
            $info = $machine[1] ?? array();
            $hostname = is_array($info['cn'] ?? '') ? ($info['cn'][0] ?? '') : ($info['cn'] ?? '');
            if (!empty($hostname)) $displayName = $hostname;
            break;
        }
    }
} elseif ($type === 'group' && !empty($name)) {
    $group = new Group(intval($name), true, false, true);
    if ($group->exists && !empty($group->name)) $displayName = $group->name;
}

$currentUser = $_SESSION['login'] ?? 'unknown';

if (isset($_POST['bconfirm'])) {
    $value = isset($config['isInt']) ? intval($name) : $name;
    $success = ExclusionHelper::removeExclusion($config['key'], $value, $currentUser);

    if ($success) {
        new NotifyWidgetSuccess(sprintf(_T("'%s' removed from exclusions", "security"), $displayName));
    } else {
        new NotifyWidgetFailure(_T("Failed to remove exclusion", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => $config['tab'])));
    exit;
}

// Show confirmation popup
$f = new PopupForm($config['title']);
$f->addText("<br/>" . sprintf(_T("Remove '%s' from exclusions?", "security"), htmlspecialchars($displayName)) . "<br/><br/>");
$f->addValidateButton("bconfirm", _T("Remove", "security"));
$f->addCancelButton("bback");
$f->display();
?>
