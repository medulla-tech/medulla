<?
/*
 *  (c) 2016 siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

$sidemenu= new SideMenu();
$sidemenu->setClass("xmppmaster");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All users tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditdeploy"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My teams tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditteam"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditmypastdeploys"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All users past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditpastdeploys"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My teams past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster","auditmypastdeploysteam" ));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My Convergence", 'xmppmaster'), "xmppmaster", "xmppmaster","auditconvergence" ));
?>
