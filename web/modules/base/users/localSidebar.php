<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

$sidemenu = new SideMenu();
$sidemenu->setClass("users");
$sidemenu->setBackgroundImage("img/users/icn_users_large.gif");
$sidemenu->addSideMenuItem(new SideMenuItem(_("List"), "base","users","index", "img/users/icn_global_active.gif", "img/users/icn_global.gif"));
$sidemenu->addSideMenuItem(new SideMenuItem(_("Add"), "base","users","add", "img/users/icn_addUser_active.gif", "img/users/icn_addUser.gif"));
if (in_array("bulkimport", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_("Bulk import (CSV)"), "base", "users", "bulkimport", "img/users/icn_addUser_active.gif", "img/users/icn_addUser.gif"));
}
if ($_SESSION["login"] != "root") {
    $sidemenu->addSideMenuItem(new SideMenuItem(_("Change your password"), "base","users","passwd", "img/access/icn_global_active.gif", "img/access/icn_global.gif"));
}

/* Display the global password policy settings if enabled */
if (in_array("ppolicy", $_SESSION["modulesList"])) {
    require_once("modules/ppolicy/includes/localSidebar.php");
}

?>
