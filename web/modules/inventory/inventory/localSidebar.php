<?
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

$sidemenu= new SideMenu();

$sidemenu->setClass("inventory");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Incoming", 'inventory'), "inventory", "inventory", "incoming"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Bios", 'inventory'), "inventory", "inventory", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Hardware", 'inventory'), "inventory", "inventory", "hardware"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Software", 'inventory'), "inventory", "inventory", "software"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Network", 'inventory'), "inventory", "inventory", "network"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Controller", 'inventory'), "inventory", "inventory", "controller"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Registry", 'inventory'), "inventory", "inventory", "registry"));

if (isExpertMode()) {
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Drive", 'inventory'), "inventory", "inventory", "drive"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Input", 'inventory'), "inventory", "inventory", "input"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Memory", 'inventory'), "inventory", "inventory", "memory"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Monitor", 'inventory'), "inventory", "inventory", "monitor"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Port", 'inventory'), "inventory", "inventory", "port"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Printer", 'inventory'), "inventory", "inventory", "printer"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Sound", 'inventory'), "inventory", "inventory", "sound"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Storage", 'inventory'), "inventory", "inventory", "storage"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("VideoCard", 'inventory'), "inventory", "inventory", "videocard"));
}
?>
