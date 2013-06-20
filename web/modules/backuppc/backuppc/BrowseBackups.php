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

$p = new PageGenerator(_T("View restore points", 'backuppc'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/backuppc/includes/xmlrpc.php");

$response = get_backup_list($_GET['host']);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

if ($response['data']) {

    $backups = $response['data'][0];
    $bk_time = $response['data'][4];
    $ages = $response['data'][6];
    $times = array();
    $count = count($backups);

    $params = array();
    for ($i=0;$i<$count;$i++)
    {
        $params[] = array('host'=>$_GET['host'], 'backupnum'=>$backups[$i]);
        preg_match("#.+ (.+)#",$bk_time[$i],$result);
        $time = time() - floatval($ages[$i])*24*60*60; 
        $times[] = strftime(_T("%A, %B %e %Y",'backuppc'),$time).' - '.$result[1] ;
    }

    $n = new OptimizedListInfos($times, _T("Backup#", "backuppc"));
    //$n->addExtraInfo($types, _T("Type", "backuppc"));
    $n->setCssClass("file"); // CSS for icons
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = 0;
    $n->end = 50;

    $n->setParamInfo($params); // Setting url params
    $n->addActionItem(new ActionItem(_T("View", "backuppc"),"BrowseShareNames","display","host", "backuppc", "backuppc"));

    print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

    $n->display();
}

// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");

?>

<style>
    .noborder { border:0px solid blue; }
</style>
