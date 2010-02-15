<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: localSidebar.php 382 2008-03-03 15:13:24Z cedric $
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
$sidemenu->setClass("audit");
#$sidemenu->setBackgroundImage("img/users/icn_logview_large.gif");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All", "base"), "base","audit","indexall", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Users and Groups", "base"), "base","audit","indexbase", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));

if(in_array("samba", $_SESSION["modulesList"])) {    
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Samba", "base"), "base","audit","indexsamba", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
}
if(in_array("mail", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Mail", "base"), "base","audit","indexmail", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
}
if(in_array("proxy", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Proxy", "base"), "base","audit","indexproxy", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
}
if(in_array("network", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Network", "base"), "base","audit","indexnetwork", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
}
if(in_array("sshlpk", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("SSHLPK", "base"), "base","audit","indexsshlpk", 
    "img/common/logview_active.png", "img/common/logview_inactive.png"));
}

?>
