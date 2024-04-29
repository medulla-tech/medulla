<?php
/*
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

$sidemenu= new SideMenu();
$sidemenu->setClass("manage computers");
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Imaging server status","imaging"), "imaging", "manage", "index")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Manage masters","imaging"), "imaging", "manage", "master")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Manage boot services","imaging"), "imaging", "manage", "service")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Default boot menu","imaging"), "imaging", "manage", "bootmenu")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Post-imaging scripts","imaging"), "imaging", "manage", "postinstall")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Imaging Configuration","imaging"), "imaging", "manage", "configuration")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Windows System Image Manager","imaging"), "imaging", "manage", "systemImageManager")
);

if (in_array("dyngroup", $_SESSION["modulesList"])) {
    require("modules/dyngroup/dyngroup/localImagingSidebar.php");
}
?>
