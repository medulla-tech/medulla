<?php
/**
 * (c) 2016-2017 SIVEO  http://siveo.net
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

require_once("modules/dyngroup/includes/dyngroup.php"); # for Group Class
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/imaging/includes/xmlrpc.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
require_once("modules/base/includes/computers.inc.php");

$requestedlocation = $_GET['location'];

$gg = xmlrpc_getCustomMenubylocation($requestedlocation);

$location_name = xmlrpc_getLocationName($requestedlocation);


$listforunregistred = array();

$groupmembers = array();

$newregisterd = array();

foreach ($gg as $entry){
    $uuid = $entry[0];
    $cn   = $entry[1];
    $nic_uuid   = $entry[2];
    $listforunregistred[]=$uuid;
    $groupmembers["$uuid##$cn"] = array('hostname' => $cn, 'uuid' => $uuid);
    $newregisterd[]=array('hostname' => $cn, 'uuid' => $uuid, 'nic_uuid' => $nic_uuid);
}

//unregistre machine.
xmlrpc_delComputersImaging($listforunregistred);


// Group name
$groupname = sprintf (_T("Machine with custom menu on entity [%s] at %s", "imaging"),$location_name ,date("Y-m-d H:i:s"));

$group = new Profile();
$group->create($groupname, False);
$group->addMembers($groupmembers);
$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

// link group to server entity
xmlrpc_set_profile_imaging_server($group->id, $requestedlocation);

$params = array();

$params['target_opt_kernel'] = 'quiet';
$params['target_opt_raw_mode'] = '';
$params['target_uuid'] = $group->id;
$params['target_name'] = $groupname;
$params['update_nt_boot'] = '';
$params['default_name'] = 'Default Boot Menu';
$params['disklesscli'] = '';
$params['background_uri'] = '##PULSE2_BOOTSPLASH_FILE##';
$params['target_opt_parts'] = [];
$params['timeout'] = '10';
$params['bootcli'] = '';
$params['dont_check_disk_size'] = '';
$params['hidden_menu'] = '';
$params['message'] = '-- Warning! Your PC is being backed up or restored. Do not reboot !';
$params['target_opt_image'] = '';
//$params['choose_network'] = nic_uuid;
$ret = xmlrpc_setMyMenuProfile($group->id, $params);
header("Location: " . urlStrRedirect("imaging/manage/display", array('gid'=>$group->id)));
exit;
?>



