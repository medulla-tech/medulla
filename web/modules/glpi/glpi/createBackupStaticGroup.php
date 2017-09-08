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

// Get all the machines
$all_machines = getComputersList();
// Get all the machines in backup
$machines_in_backup = get_all_hosts();

// Get the uuids of machines in backup
$uuids_backup = [];
foreach ($machines_in_backup as $machine)
{
    echo '<pre>';
    print_r($machine);
    echo '</pre>';

    $uuids_backup[] = $machine['uuid'];
}

$machines_in_backup = [];
$machines_not_backup = [];
// Create the backup and no backup machines lists
foreach($all_machines as $machine)
{
    $tmp = [];

    // Create formated machine
    $tmp[$machine[1]["objectUUID"][0].'##'.$machine[1]["cn"][0]] = ["hostname" => $machine[1]["cn"][0], 'uuid' =>$machine[1]["objectUUID"][0]];

    if(!in_array($machine[1]['objectUUID'][0],$uuids_backup))
        $machines_not_backup += $tmp;

    else
        $machines_in_backup += $tmp;
}

echo '<pre>';
print_r($machines_in_backup);
echo '</pre>';

echo '<pre>';
print_r($machines_not_backup);
echo '</pre>';

if($_GET['backup'] == 'yes'){
    $groupname = sprintf (_T("Machines in backup at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_in_backup;
}

else {
    $groupname = sprintf (_T("Machines not in backup at %s", "glpi"), date("Y-m-d H:i:s"));
    $groupmembers = $machines_not_backup;
}


$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);

$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));

exit;
