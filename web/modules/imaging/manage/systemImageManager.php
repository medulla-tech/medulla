<?php
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
 *
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

require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');
?>

<?php

$page = new TabbedPageGenerator();
//Display sidemenu
$page->setSideMenu($sidemenu);

$tabList = array(
	'unattended' => _T('Sysprep generator', "imaging"),
	'sysprepList' => _T('Sysprep list', "imaging"),
// 	'services' => _T('Services', "imaging"),
// 	'power' => _T('Power', "imaging"),
);

foreach ($tabList as $tab => $str) {
    $page->addTab("$tab", $str, "", "modules/imaging/manage/$tab.php");
}
	$page->display();
 ?>
