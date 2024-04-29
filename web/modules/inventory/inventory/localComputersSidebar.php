<?php
/*
 * (c) 2015 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Medulla 2, http://medulla.mandriva.org
 *
 * Medulla 2 is free software; you can redistribute it and/or modify
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

// These entries are on computers page, loaded from base/computers/localSidebar.php

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Entities", "inventory"), "base", "computers",  "entityList", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add an entity", "inventory"), "base", "computers", "addEntity", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Entity rules", "inventory"), "base", "computers", "entityRules", "", ""));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add entity rule", "inventory"), "base", "computers", "addEntityRule", "", ""));
?>
