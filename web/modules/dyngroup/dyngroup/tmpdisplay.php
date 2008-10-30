<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require("modules/base/graph/computers/index.css");

$p = new PageGenerator(_T("Temporary result display", "dyngroup"));
$p->setSideMenu($sidemenu);
$p->display();
$get = "&request=".$_GET['request'];
if (strlen($_GET['id'])) {
    $get = "&id=".$_GET['id'];
}
print "<a href='main.php?module=base&submod=computers&action=computersgroupcreator$get'>"._T('back', 'dyngroup')."</a>";

include("modules/pulse2/pulse2/computers_list.php");
# TODO put bool in the first page whereas it is actualy in the second

?>
