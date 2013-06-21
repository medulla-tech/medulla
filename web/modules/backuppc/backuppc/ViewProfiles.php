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

$p = new PageGenerator(_T("Filesets", 'backuppc'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/backuppc/includes/xmlrpc.php");


// =========== BACKUP PROFILES =================================

$response = get_backup_profiles();

$profile_names = array();
$params = array();

foreach ($response as $profile)
    $profile_names[$profile['id']] = $profile['profilename'];

asort($profile_names);


foreach ($profile_names as $pid => $pname)
    $params[] = array('id' => $pid,'type' => 0);

$profile_names = array_values($profile_names);

if ($profile_names) {

    $count = count($profile_names);

    
    $n = new OptimizedListInfos($profile_names, _T("Fileset", "backuppc"));

    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = 0;
    $n->end = 50;

    $n->setParamInfo($params); // Setting url params
    $n->addActionItem(new ActionItem(_T("Edit profile", "backuppc"),"EditBackupProfile","edit","profile", "backuppc", "backuppc"));
    $n->addActionItem(new ActionPopupItem(_T("Delete profile", "backuppc"),"deleteProfile","delete","profile", "backuppc", "backuppc"));

    $n->display();
}


// =========== PERIOD PROFILES =================================

print "<br/><h2>"._T('Schedules','backuppc')."</h2>";

$response = get_period_profiles();

$profile_names = array();
$params = array();

foreach ($response as $profile)
    $profile_names[$profile['id']] = $profile['profilename'];

asort($profile_names);


foreach ($profile_names as $pid => $pname)
    $params[] = array('id' => $pid,'type' => 0);

$profile_names = array_values($profile_names);
    

if ($profile_names) {

    $count = count($profile_names);

    
    $n = new OptimizedListInfos($profile_names, _T("Schedule", "backuppc"));

    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = 0;
    $n->end = 50;

    $n->setParamInfo($params); // Setting url params
    $n->addActionItem(new ActionItem(_T("Edit", "backuppc"),"EditPeriodProfile","edit","profile", "backuppc", "backuppc"));
    $n->addActionItem(new ActionPopupItem(_T("Delete profile", "backuppc"),"deleteProfile","delete","profile", "backuppc", "backuppc"));

    $n->display();
}

// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");

?>

<style>
    .noborder { border:0px solid blue; }
</style>