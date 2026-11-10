<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * Reflex Module - Side menu
 */

require_once("modules/reflex/includes/xmlrpc.php");

$sidemenu = new SideMenu();
$sidemenu->setClass("reflex");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Dashboard", 'reflex'), "reflex", "reflex", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Alerts", 'reflex'), "reflex", "reflex", "alerts"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Alerts History", 'reflex'), "reflex", "reflex", "alertsHistory"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Probes", 'reflex'), "reflex", "reflex", "probes"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Machines", 'reflex'), "reflex", "reflex", "machines"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Settings", 'reflex'), "reflex", "reflex", "settings"));
