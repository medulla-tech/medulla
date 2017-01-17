<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

$groupmembers = array();

foreach ($gg as $entry){
    $uuid = $entry[0];
    $cn   = $entry[1];
    $groupmembers["$uuid##$cn"] = array('hostname' => $cn, 'uuid' => $uuid);
}

file_put_contents("/tmp/new",print_r( $groupmembers, true));
// Group name
$groupname = sprintf (_T("Machine with custom menu on entity [%s] at %s", "imaging"),$location_name ,date("Y-m-d H:i:s"));

// header("Location: " . urlStrRedirect("base/computers/index", array($groupmembers)));
// exit;

$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);
$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
exit;
?>
