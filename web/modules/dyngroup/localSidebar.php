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

require_once("modules/dyngroup/includes/dyngroup.php");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups"), "base", "computers",  "list"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a group"), "base", "computers", "creator", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif"));


$max = dyngroup_last_id();
$items = array();
$i = 0;

while ($i < $max) {
    $group = new Dyngroup($i);
    if ($group->getName()) {
        $name = $group->getName();

        if ($group->canShow()) {
            $s = new SideMenuItem(
                     sprintf(_T("Display %s '%s'"), ($group->isGroup()?_T("group"):_T("request")), $name),
                    "base", "computers", "display&id=$i"
                );
            $s->setCssId("displayid$i");
            $items[$i] = $s;
            $sidemenu->addSideMenuItem($items[$i]);
        }
    }
    $i++;
}

?>

