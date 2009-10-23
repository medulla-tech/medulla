<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: list.php 3865 2009-03-05 09:24:10Z cdelfosse $
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
require("modules/dyngroup/graph/index.css");

$p = new PageGenerator(_T("Profiles list", 'dyngroup'));
$p->setSideMenu($sidemenu);
$p->display();


if (isset($_GET['gid'])) {
    $gid = $_GET['gid'];
} else {
    $gid = '';
}
$ajax = new AjaxFilter("modules/dyngroup/dyngroup/ajaxListGroups.php", "container", array('gid' => $gid, 'type' => 1));
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
