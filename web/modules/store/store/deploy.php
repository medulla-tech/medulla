<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * Medulla Store - Deploy package
 * Deploy a store package to machines or groups
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");

// Get package parameters
$packageUuid = $_GET['packageUuid'] ?? '';
$pid = $_GET['pid'] ?? '';

if (empty($packageUuid)) {
    $p = new PageGenerator(_T("Deploy Package", 'store'));
    $p->setSideMenu($sidemenu);
    $p->display();
    new NotifyWidgetFailure(_T('No package selected', 'store'));
    return;
}

// Get package info
$packageName = '';
$packageVersion = '';
try {
    $json = json_decode(get_xmpp_package($packageUuid), true);
    if ($json && isset($json['info'])) {
        $packageName = $json['info']['name'] ?? '';
        $packageVersion = $json['info']['version'] ?? '';
    }
} catch (Exception $e) {
    // Package not found
}

// Page title
$pageTitle = new PageGenerator(_T("Deploy Package", 'store'));
$pageTitle->setSideMenu($sidemenu);
$pageTitle->display();

// Tabbed content
$p = new TabbedPageGenerator();

// Package info displayed above tabs
$p->setDescription(
    '<div style="background:var(--gray-50);border:1px solid var(--gray-200);border-radius:8px;padding:14px 18px;margin-bottom:15px;display:flex;align-items:center;gap:12px;">'
    . '<img src="img/other/package.svg" width="28" height="28"/>'
    . '<div>'
    . '<div style="font-size:16px;font-weight:600;color:var(--color-text-dark);">' . htmlspecialchars($packageName ?: $packageUuid) . '</div>'
    . ($packageVersion ? '<div style="margin-top:2px;"><span style="background:#e9ecef;padding:2px 10px;border-radius:4px;font-family:monospace;font-size:12px;color:var(--color-text-medium);">v' . htmlspecialchars($packageVersion) . '</span></div>' : '')
    . '</div>'
    . '</div>'
);

// Tabs — pass package params to each tab
$tabParams = array('packageUuid' => $packageUuid, 'pid' => $pid, 'packageName' => $packageName, 'packageVersion' => $packageVersion);
$p->addTab("tabmachines", _T("Machines", "store"), "", "modules/store/store/tabMachinesDeploy.php", $tabParams);
$p->addTab("tabgroups", _T("Groups", "store"), "", "modules/store/store/tabGroupsDeploy.php", $tabParams);

$p->display();
?>
