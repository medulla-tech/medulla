<?
/**
 * (c) 2020 Siveo, http://siveo.net
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

$sidemenu= new SideMenu();
$sidemenu->setClass("admin");
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("List of Relays","admin"), "admin", "admin", "relaysList")
);
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Clusters List", 'admin'), "admin", "admin", "clustersList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("New Cluster", 'admin'), "admin", "admin", "newCluster"));
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Rules","admin"), "admin", "admin", "rules")
);
// ------------------------------------------
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Management of Organizational Entities","admin"), "admin", "admin", "manage_entity_organisation")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Client Entities Management","admin"), "admin", "admin", "manage_user_entity")
);
// ------------------------------------------
?>
