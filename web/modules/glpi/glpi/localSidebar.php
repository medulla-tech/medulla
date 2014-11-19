<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Add new sidemenu item */

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Entities", "glpi"), "base", "computers",  "entityList", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add an entity", "glpi"), "base", "computers", "addEntity", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Locations", "glpi"), "base", "computers",  "locationList", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a location", "glpi"), "base", "computers", "addLocation", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Entity rules", "glpi"), "base", "computers", "entityRules", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add entity rule", "glpi"), "base", "computers", "addEntityRule", "", ""));

?>
