<?php
/**
 * (c) 2018-2023 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/kiosk/includes/xmlrpc.php");

$sidemenu = new SideMenu();
$sidemenu->setClass("kiosk");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Profile List", 'kiosk'), "kiosk", "kiosk", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add Profile", 'kiosk'), "kiosk", "kiosk", "add"));
if(xmlrpc_get_conf_kiosk()['enable_acknowledgements'] == true) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Installation Requests", "kiosk"), "kiosk", "kiosk", "acknowledges"));
}
