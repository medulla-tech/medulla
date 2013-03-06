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


require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require("modules/dyngroup/graph/index.css");

$p = new PageGenerator(_T("Profiles list", 'dyngroup'));
$p->setSideMenu($sidemenu);
$p->display();


if (isset($_GET['gid'])) {
    $gid = $_GET['gid'];
} else {
    $gid = '';
}
$ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxListGroups"), "container", array('gid' => $gid, 'type' => 1));
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
