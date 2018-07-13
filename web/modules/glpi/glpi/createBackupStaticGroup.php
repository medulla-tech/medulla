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
require_once("modules/backuppc/includes/xmlrpc.php"); // For get_all_hosts
require_once("modules/glpi/includes/xmlrpc.php"); // For xmlrpc_get_all_uuids_and_hostnames

// Get all the machines
$all_machines = xmlrpc_get_all_uuids_and_hostnames();

// Get all the machines in backup
$machines_in_backup = get_all_hosts();

// Get the uuids of machines in backup
$uuids_backup = [];
foreach ($machines_in_backup as $machine)
{
    $uuids_backup[] = $machine['uuid'];
}

$machines_in_backup = [];
$machines_not_backup = [];
// Create the backup and no backup machines lists
foreach($all_machines as $machine)
{
    if(!in_array($machine["uuid"],$uuids_backup))
        $machines_not_backup[] = $machine;

    else
        $machines_in_backup[] = $machine;
}

if($_GET['backup'] == 'yes'){
    $groupname = sprintf (_T("Machines backup configured at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_in_backup;
}

else {
    $groupname = sprintf (_T("Machines backup not configured at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_not_backup;
}

$group = new Group();
$group->create($groupname, False);
$group->miniAddMembers($groupmembers);

$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));

exit;
