<?php
/**
 * (c) 2016 Siveo, http://siveo.net
 * $Id$
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


require("modules/kiosk/graph/index.css");
require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pulse2/includes/utilities.php");
require("graph/navbar.inc.php");
require("modules/kiosk/kiosk/localSidebar.php");

$p = new PageGenerator(_T("List of profils"));
$p->setSideMenu($sidemenu);
$p->display();


$n = new OptimizedListInfos(xmlrpc_get_profiles_name_list(), _T("Profile Name", "pkgs"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($desc, _T("Associated packages", "pkgs"));

// parameters are :
// - label
// - action
// - class (icon)
// - profile get parameter
// - module
// - submodule
$n->addActionItem(new ActionPopupItem(_T("Associate Packages"), "edit", "list", "profile", "kiosk", "kiosk"));
$n->addActionItem(new ActionPopupItem(_T("Associate Users"), "edit", "users", "profile", "kiosk", "kiosk"));
$n->addActionItem(new ActionPopupItem(_T("Edit Profil"), "edit", "edit", "profile", "kiosk", "kiosk"));
$n->addActionItem(new ActionPopupItem(_T("Delete Profil"), "delete", "delete", "profile", "kiosk", "kiosk"));
$n->setNavBar(new AjaxNavBar($count, $filter1));

$n->display();
?>
