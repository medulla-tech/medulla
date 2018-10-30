<?php
/**
 * (c) 2017 siveo   http://siveo.net
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
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
require_once("modules/base/includes/computers.inc.php");

require_once("modules/pkgs/includes/xmlrpc.php");


$vendor=$_GET['vendor'];
$software=$_GET['software'];
$version=$_GET['version'];
$count=$_GET['count'];
$licencemax=$_GET['licencemax'];


$licensescount = getLicensesComputer($vendor,$software,$version);

$locationname =xmlrpc_getLocationName($licensescount[0]['entityid']);



$groupmembers = array();

foreach ($licensescount as $gg ){
    $uuid = 'UUID'.$gg['computer'];
    $cn = $gg['name'];
    $groupmembers["$uuid##$cn"] = array('hostname' => $cn, 'uuid' => $uuid);
}
$groupname = sprintf (_T("Machine licence [$vendor $software  $version : %s/%s ] at %s", "glpi"),$count,$licencemax, date("Y-m-d H:i:s"));

$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);
$truncate_limit = getMaxElementsForStaticList();

//ICI
if ($truncate_limit == count($groupmembers))
{
    $str = sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit);
    new NotifyWidgetWarning($str);
    xmlrpc_setfrompkgslogxmpp( $str,
                                "IMG",
                                '',
                                0,
                                "",
                                'Manuel',
                                '',
                                '',
                                '',
                                "session user ".$_SESSION["login"],
                                'Packaging | List | Manual');
}
$parm=array();
$parm['gid']=$group->id;
header("Location: " . urlStrRedirect("base/computers/display", $parm));
exit;
?>
