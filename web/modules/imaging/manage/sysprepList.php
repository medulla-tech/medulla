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

if(!isset($_GET['tab']) && $_GET['action'] == 'sysprepList')
{
	require("modules/imaging/manage/localSidebar.php");
	require("graph/navbar.inc.php");
	require_once('modules/imaging/includes/includes.php');
	require_once('modules/imaging/includes/xmlrpc.inc.php');
}

//Verify if any file must be deleted
if (isset($_GET['deleteFile'])){
    echo xmlrpc_deleteWindowsAnswerFile($_GET['deleteFile']);
    if (!isXMLRPCError())
    {
		new NotifyWidgetSuccess(_("The sysprep answer file has been removed from the imaging system."));
	}
}
if(isset($_GET['display']))
{
	//Add colors for xml
	echo '<link rel="stylesheet" href="modules/imaging/graph/css/default.min.css">';
	echo '<script src="modules/imaging/graph/highlight/highlight.min.js"></script>';
	echo '<script>hljs.initHighlightingOnLoad();</script>';

	//$file must be existing
	if(!($file = xmlrpc_selectWindowsAnswerFile($_GET['display'])))
	{
		$file = array();
	}
	echo '<pre>';
	foreach($file as $line)
	{
		echo htmlentities($line);
	}
	echo '</pre>';
}
else
{
//Get the list of answer files
$list = xmlrpc_Windows_Answer_list_File(0,-1);

//Display sidemenu
$page = new PageGenerator(_T("All Windows Answer Files", 'imaging'));
$page->setSideMenu($sidemenu);
$page->display();

//Create list of sysprep answer file
$table = new ListInfos($list['file'], _T("File name", "imaging"));

//Add informations on each row
$table->addExtraInfo($list['os'], _T("OS", "imaging"));
$table->addExtraInfo($list['description'], _T("Description", "imaging"));

//Add actions on each row
$table->addActionItem(new ActionItem(_T("Display sysprep file","imaging"), "sysprepView", "display", "display", "imaging", "manage"));
$table->addActionItem(new ActionItem(_T("Edit sysprep file","imaging"), "unattended", "edit", "edit", "imaging", "manage"));
$table->addActionItem(new ActionConfirmItem(_T("Delete sysprep file", 'imaging'), "sysprepList", "delete", "deleteFile", "imaging", "manage", _T('Are you sure you want to unset this sysrep answer file?', 'imaging')));

// Display the list
$table->display();
}
?>