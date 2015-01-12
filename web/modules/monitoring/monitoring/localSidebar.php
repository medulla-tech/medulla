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
$sidemenu->setClass("monitoring");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Dashboard", 'monitoring'), "monitoring", "monitoring", "index"));
//$sidemenu->addSideMenuItem(new SideMenuItem(_T("Hosts", 'monitoring'), "monitoring", "monitoring", "host"));
//$sidemenu->addSideMenuItem(new SideMenuItem(_T("Graphics", 'monitoring'), "monitoring", "monitoring", "viewgraphics"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Configuration", 'monitoring'), "monitoring", "monitoring", "editconfiguration"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("History", 'monitoring'), "monitoring", "monitoring", "history"));

?>
