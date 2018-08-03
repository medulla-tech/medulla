<?php
/**
 * (c) 2016 siveo, http://www.siveo.net/
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

require_once("modules/dyngroup/includes/dyngroup.php"); // For Group Class
require_once("modules/glpi/includes/xmlrpc.php"); // For total_machines
require_once("modules/xmppmaster/includes/xmlrpc.php"); // For machines_online
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php"); // For xmlrpc_getListPresenceMachine

$machines_online = xmlrpc_getListPresenceMachine();
$uuids_online = [];
$all_machines = xmlrpc_get_all_uuids_and_hostnames();
$machines_offline = [];

$list = [];

// Get the uuids of the machines
foreach($machines_online as $machine)
{
    if($machine['agenttype'] != 'relayserver')
    {
        $uuids_online[] = $machine['uuid_inventorymachine'];
    }
    else
        unset($machine);
}

// Clean the array
$machines_online = [];

// Create the offline an online machines lists
foreach($all_machines as $machine)
{
    // Create formated machine
    if(!in_array($machine["uuid"],$uuids_online))
        $machines_offline[] = $machine;

    else
        $machines_online[] = $machine;
}

if($_GET['machines'] == 'online'){
    $groupname = sprintf (_T("Machines online at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_online;
}

else {
    $groupname = sprintf (_T("Machines offline at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_offline;
}

$group = new Group();
$group->create($groupname, False);
$group->miniAddMembers($groupmembers);

$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
exit;
