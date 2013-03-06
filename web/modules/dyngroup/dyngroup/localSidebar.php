<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Add new sidemenu item */

require_once("modules/dyngroup/includes/includes.php");
require_once("modules/pulse2/includes/profiles_xmlrpc.inc.php");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups", "dyngroup"), "base", "computers",  "list"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a group", "dyngroup"), "base", "computers", "computersgroupcreator", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif"));

$items = array();
$groups = getAllGroups(array('canShow'=>true, 'localSidebar'=>true));
foreach ($groups as $group) {
    $isA = ($group->isDyn() ? (!$group->isRequest() ? _T('Static group:', 'dyngroup') : _T('Dynamic group:', 'dyngroup')) : (_T('Static group:', 'dyngroup')));

    $s = new SideMenuItemNoAclCheck(
             sprintf("%s<br />%s", $isA, $group->getName()),
             "base", "computers", "display&gid=".$group->id."&groupname=".$group->name
    );
    $s->setCssId("displayid".$group->id);
    $items[$group->id] = $s;
    $sidemenu->addSideMenuItem($items[$group->id]);
}

?>
