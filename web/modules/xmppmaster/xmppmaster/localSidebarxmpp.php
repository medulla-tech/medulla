<?
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 */

$sidemenu= new SideMenu();
$sidemenu->setClass("xmppmaster");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All users tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditdeploy"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My teams tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditteam"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditmypastdeploys"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All users past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditpastdeploys"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My teams past tasks", 'xmppmaster'), "xmppmaster", "xmppmaster","auditmypastdeploysteam" ));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My Convergence", 'xmppmaster'), "xmppmaster", "xmppmaster","convergence" ));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All users convergence", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditconvergence"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("My teams convergence", 'xmppmaster'), "xmppmaster", "xmppmaster", "auditteamconvergence"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Quick Action results", "xmppmaster"), "xmppmaster", "xmppmaster", "ActionQuickGroup"));
?>
