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

require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/machines.inc.php');
require('modules/msc/includes/command_history.php');

$filter = $_GET["filter"];

$files = msc_get_downloaded_files_list();

$actionDownload = new ActionItem(_T("Download file", "msc"), "download_file_get",  "download", "msc", "base", "computers");
$actionRemove = new ActionPopupItem(_T("Delete file", "msc"), "download_file_remove",  "delete", "msc", "base", "computers");

$actionsdl = array();
$actionsrm = array();

$fnames = array();
$flengths = array();
$ftimestamps = array();
$fcomputers = array();
$finodes = array();
$states = array();

$computersCache = array();

foreach($files as $file) {
    $uuid = $file[1];
    if (array_key_exists($uuid, $computersCache)) {
        $computer = $computersCache[$uuid];
    } else {
        $computer = getMachine(array('uuid' => $uuid), $ping = False);
        $computersCache[$uuid] = $computer;
    }
    if ((strlen($filter) == 0)
        || ((strlen($filter) > 0)
            && ((strpos($file[0], $filter) !== False) || (strpos($computer->hostname, $filter) !== False))
            )
        ) {
        $fnames[] = $file[0];
        $fcomputers[] = $computer->hostname;
        $ftimestamps[] = _toDate($file[2]);
        $finodes[] = array("id" => $file[4], "objectUUID" => $_GET["objectUUID"]);
        if (($file[0] == '') && ($file[3] == 0)) {
            $states[] = _T('Downloading', 'msc');
            $flengths[] = '';
            $actionsdl[] = new EmptyActionItem();
            $actionsrm[] = new EmptyActionItem();
        } else if (($file[0] == '') && ($file[3] == -1)) {
            $states[] = _T('Error', 'msc');
            $flengths[] = '';
            $actionsdl[] = new EmptyActionItem();
            $actionsrm[] = $actionRemove;            
        } else {
            $states[] = _T('Ready', 'msc');
            $flengths[] = $file[3];
            $actionsdl[] = $actionDownload;
            $actionsrm[] = $actionRemove;
        }
    }
}


$l = new ListInfos($ftimestamps, _T('Timestamp', 'msc'));
$l->addExtraInfo($fcomputers, _T('From computer', 'msc'));
$l->addExtraInfo($fnames, _T('File name', 'msc'));
$l->addExtraInfo($flengths, _T('Length', 'msc'));
$l->addExtraInfo($states, _T('Status', 'msc'));
$l->addActionItemArray($actionsdl);
$l->addActionItemArray($actionsrm);
$l->setTableHeaderPadding(1);
$l->disableFirstColumnActionLink();
$l->setParamInfo($finodes);
$l->setNavBar(new AjaxNavBar(count($fnames), $filter));
$l->display();

?>