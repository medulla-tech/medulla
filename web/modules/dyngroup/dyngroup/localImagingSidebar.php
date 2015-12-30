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

if (isProfilesEnable() && areProfilesPossible()) {
    $sidemenu->addSideMenuItem(
        new SideMenuItem(_T("All imaging groups", "dyngroup"), "imaging", "manage",  "list_profiles","img/machines/icn_allGroups_active.gif", "img/machines/icn_allGroups_ro.gif")
    );
    $sidemenu->addSideMenuItem(
        new SideMenuItem(_T("Add an imaging group", "dyngroup"), "imaging", "manage", "computersprofilecreator", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif")
    );
}

if (isProfilesEnable()) {
    $items = array();
    $profiles = getAllProfiles(array('canShow'=>true));
    foreach ($profiles as $profile) {
        $isA = ($profile->isDyn() ? (!$profile->isRequest() ? _T('Imaging group:', 'dyngroup') : _T('Dynamic imaging group:', 'dyngroup')) : (_T('Imaging group:', 'dyngroup')));

        $s = new SideMenuItemNoAclCheck(
                 sprintf("%s<br />%s", $isA, $profile->getName()),
                 "imaging", "manage", "display&gid=".$profile->id."&type=1&groupname=".$profile->name
        );
        $items[$profile->id] = $s;
        $sidemenu->addSideMenuItem($items[$profile->id]);
    }
}


?>

