<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 
require("graph/navbar.inc.php");
require("localSidebar.php");
require("modules/msc/includes/package_api.php");

$p = new PageGenerator(_T("Packages", 'msc'));
$p->setSideMenu($sidemenu);
$p->display(); 

$a_packages = array();
$a_pversions = array();
foreach (getAllPackages() as $package) {
    $a_packages[] = $package->label;
    $a_pversions[] = $package->version;
}

$n = new ListInfos($a_packages, _T("Package", 'msc'));
$n->addExtraInfo($a_pversions, _T("Version", 'msc'));

$n->addActionItem(new ActionItem(_T("Launch", "msc"),"start_command", "start", "msc", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Details", "msc"),"package_detail", "detail", "msc", "base", "computers"));

$n->drawTable(0);


?>
<style>
li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>

