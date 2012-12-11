<?
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

if ($_GET['group'] == 'green') {
    $groupname = sprintf (_T("Latest inventory is less than %s days at %s", "inventory"), $_GET['days'], date("Y-m-d H:i:s"));
}
else {
    $groupname = sprintf (_T("Latest inventory is more than %s days at %s", "inventory"), $_GET['days'], date("Y-m-d H:i:s"));
}

$machines = $_SESSION['inventoryDashboard'][$_GET['group']];

$groupmembers = array();

foreach ($machines as $key => $value) {
    $groupmembers[$key . '##' . $value] = array(
        "hostname" => $value,
        "uuid" => $key,
    );
}

$group = new Group();
$group->create($groupname, False);
$group->addMembers($groupmembers);

header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
exit;
