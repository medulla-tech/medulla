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


require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Browse backup", 'backuppc').' ('.$_GET['cn'].')');
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/backuppc/includes/xmlrpc.php");

$response = get_share_names($_GET['host'], $_GET['backupnum']);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

$sharenames = $response['data'];
$count = count($sharenames);

$params = array();
for ($i=0;$i<$count;$i++)
    $params[] = array(
      'host'=>$_GET['host'], 
      'cn' => $_GET['cn'],
      'backupnum'=>$_GET['backupnum'], 
      'sharename'=>str_replace('&nbsp;','%20',htmlentities($sharenames[$i]))
    );

$n = new OptimizedListInfos($sharenames, _T("Folder", "backuppc"));
$n->setCssClass("folder"); // CSS for icons
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->start = 0;
$n->end = 50;

$n->setParamInfo($params); // Setting url params
$n->addActionItem(new ActionItem(_T("Browse", "backuppc"),"BrowseFiles","display","host", "backuppc", "backuppc"));

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent


$n->display();

// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");
?>

<style>
    .noborder { border:0px solid blue; }
</style>

