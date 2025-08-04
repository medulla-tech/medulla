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

$sidemenu = new SideMenu();
$sidemenu->setClass("admin");
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("List of Relays", "admin"), "admin", "admin", "relaysList")
);
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Clusters List", 'admin'), "admin", "admin", "clustersList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("New Cluster", 'admin'), "admin", "admin", "newCluster"));
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Rules", "admin"), "admin", "admin", "rules")
);

$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Entities Management", "admin"), "admin", "admin", "entitiesManagement")
);
