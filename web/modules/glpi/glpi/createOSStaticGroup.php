<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 * (c) 2018-2021 Siveo, http://www.siveo.net
 *
 * $Id$
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

require_once("modules/dyngroup/includes/dyngroup.php"); # for Group Class
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/locations_xmlrpc.inc.php");
require_once("modules/base/includes/computers.inc.php");

$requestedOS = $_GET['os'];

// Get user locations
$groupmembers = array();
if($requestedOS == "Other")
  $requestedOS = "no operating";

$requestedVersion = $_GET['version'];
$groupname = sprintf (_T("Machine with %s %s installed at %s", "glpi"), $requestedOS, $requestedVersion, date("Y-m-d H:i:s"));;
$result = xmlrpc_get_machines_with_os_and_version($requestedOS, $requestedVersion);

foreach($result as $entry){
  $uuid = 'UUID'.$entry['id'];
  $cn = $entry['hostname'];
  $groupmembers["$uuid##$cn"] = array('hostname' => $cn, 'uuid' => $uuid, 'groupname'=>$groupname);
}

$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);

$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == count($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
exit;
