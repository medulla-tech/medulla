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
 * Security Module - Pages with one tab per platform
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/html.inc.php");

$pages = array(
    'index' => array(_T("Dashboard", 'security'), 'dashboard.php'),
    'softwares' => array(_T("Software list", 'security'), 'softwares.php'),
    'allcves' => array(_T("CVEs", 'security'), 'allcves.php'),
    'machines' => array(_T("Machines", 'security'), 'machines.php'),
);
list($title, $file) = $pages[$_GET['action'] ?? ''] ?? $pages['index'];

$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();

if (!$hasContract) {
    if (in_array($contractStatusReason, array('contract_required', 'not_configured'))) {
        ContractRequiredBox::show();
    } else {
        ServiceUnavailableBox::show();
    }
    return;
}

SecurityFilter::platformTabs("modules/security/security/" . $file);
?>
