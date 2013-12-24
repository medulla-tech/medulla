<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
require_once("modules/update/includes/xmlrpc.inc.php");
require_once("modules/update/includes/utils.inc.php");

echo "<br/><br/>";

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;


/* available buttons */
//$action = new ActionItem(_T("Enable", "update"), "enableUpdate", "display", "msc", "msc", "logs");
//$n->addActionItem(new ActionConfirmItem(_T("Unset backup", 'backuppc'), "index", "delete", "uuid", "backuppc", "backuppc", _T('Are you sure you want to unset backup for this computer?', 'backuppc')));
/*  $actionpause = new ActionPopupItem(_T("Pause", "msc"), "msctabspause", "pause", "msc", "base", "computers");
  $actionstop = new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers");
  $actionstatus = new ActionPopupItem(_T("Status", "msc"), "msctabsstatus", "status", "msc", "base", "computers");
  $actionstatus->setWidth("400");
  $actiondetails = new ActionItem(_T("Details", "msc"), "viewLogs", "display", "msc", "msc", "logs");
  $actionempty = new EmptyActionItem(); */

$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => array()
);

if (isset($_GET["status"]))
    $params['filters']['status'] = $_GET["status"];

if (isset($_GET["os_class_id"]))
    $params['filters']['os_class_id'] = $_GET["os_class_id"];

if (isset($_GET["filter"]) && $_GET["filter"])
    $params['filters']['name'] = $_GET["filter"];

extract(get_updates($params));

if (!$count) {
    print _T('No entry found', 'update');
    return;
}

//  Listinfo params
$listinfoParams = array();
foreach ($data as $row){
    $listinfoParams[] = array('id' => $row['id']);
}

$cols = listInfoFriendly($data);

// Update types strings
$cols['type_str'] = array_map('getUpdateTypeLabel', $cols['type_id']);

$n = new OptimizedListInfos($cols['title'], _T("Update title", "msc"));
$n->addExtraInfo($cols['uuid'], _T("UUID", "msc"));
$n->addExtraInfo($cols['type_str'], _T("Type", "msc"));
//$n->addActionItemArray($a_details);

$n->addActionItem(new ActionPopupItem(_T("Enable", "update"), "enableUpdate", "enable", "id", "update", "update"));
$n->addActionItem(new ActionPopupItem(_T("Disable", "update"), "disableUpdate", "disable", "id", "update", "update"));

$n->setParamInfo($listinfoParams);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $status));
$n->start = 0;
$n->end = $maxperpage;
$n->disableFirstColumnActionLink();

$n->display();
?>
