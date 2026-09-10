<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
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

$groupnames = array(
    'green'   => _T("Antivirus status is OK at %s", "glpi"),
    'orange'  => _T("Antivirus is not up to date at %s", "glpi"),
    'red'     => _T("Antivirus is disabled at %s", "glpi"),
    'missing' => _T("No antivirus found at %s", "glpi"),
    'stale'   => _T("Antivirus information is unreliable at %s", "glpi"),
);

$state = isset($_GET['group']) ? $_GET['group'] : '';
if (!array_key_exists($state, $groupnames)) {
    new NotifyWidgetFailure(_T("Unknown antivirus status", "glpi"));
    header("Location: " . urlStrRedirect("dashboard/main/default"));
    exit;
}

$groupname = sprintf($groupnames[$state], date("Y-m-d H:i:s"));

$groupmembers = getMachineListByAntivirusState($state);

$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);

$truncate_limit = getMaxElementsForStaticList();
if ($truncate_limit == safeCount($groupmembers)) new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id, 'groupname'=>$groupname)));
exit;
