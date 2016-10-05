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

//If nothing to display : redirect to sysprep list
if(isset($_GET['display']))
{
	//Display sidemenu
	$page = new PageGenerator(_T('View '.$_GET['display'].' Windows Sysprep Answer Files', 'imaging'));
	$page->setSideMenu($sidemenu);
	$page->display();

	//$file must be existing
	if(!($file = xmlrpc_selectWindowsAnswerFile($_GET['display'])))
	{
		$file = array();
	}
	echo '<pre>';
print_r($parameters);
	foreach($file as $line)
	{
		echo htmlentities($line);
	}
	echo '</pre>';
}
else{
	header("location: main.php?module=imaging&submod=manage&action=sysprepList");
}
?>