<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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


/* Add new sidemenu item */

require_once("modules/dyngroup/includes/includes.php");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups", "dyngroup"), "base", "computers",  "list"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a group", "dyngroup"), "base", "computers", "computersgroupcreator", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All profiles", "dyngroup"), "base", "computers",  "list_profiles"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a profile", "dyngroup"), "base", "computers", "computersprofilecreator", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif"));

$items = array();
$groups = getAllGroups(array('canShow'=>true));
foreach ($groups as $group) {
    $isA = ($group->isDyn() ? (!$group->isRequest() ? _T('the result', 'dyngroup') : _T('the query', 'dyngroup')) : (_T('the static group', 'dyngroup')));
    
    $s = new SideMenuItemNoAclCheck(
             sprintf(_T("(G) Display %s '%s'", "dyngroup"), $isA, $group->getName()),
             "base", "computers", "display&gid=".$group->id."&groupname=".$group->name
    );
    $s->setCssId("displayid".$group->id);
    $items[$group->id] = $s;
    $sidemenu->addSideMenuItem($items[$group->id]);
}

$items = array();
$profiles = getAllProfiles(array('canShow'=>true));
foreach ($profiles as $profile) {
    $isA = ($profile->isDyn() ? (!$profile->isRequest() ? _T('the result', 'dyngroup') : _T('the query', 'dyngroup')) : (_T('the static profile', 'dyngroup')));
    
    $s = new SideMenuItemNoAclCheck(
             sprintf(_T("(P) Display %s '%s'", "dyngroup"), $isA, $profile->getName()),
             "base", "computers", "display&gid=".$profile->id."&groupname=".$profile->name
    );
    $s->setCssId("displayid".$profile->id);
    $items[$profile->id] = $s;
    $sidemenu->addSideMenuItem($items[$profile->id]);
}


?>
