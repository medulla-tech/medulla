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
 */

$sidemenu = new SideMenu();
$sidemenu->setClass("security");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("CVE Summary", 'security'), "security", "security", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Results by Machine", 'security'), "security", "security", "machines"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Results by Entity", 'security'), "security", "security", "entities"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Results by Group", 'security'), "security", "security", "groups"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All CVEs", 'security'), "security", "security", "allcves"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Settings", 'security'), "security", "security", "settings"));
?>
