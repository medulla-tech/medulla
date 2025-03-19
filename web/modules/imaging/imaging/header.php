<?php

/*
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

global $stateid;
global $SYNCHROSTATE_TODO;
global $CUSTOM_MENU;
global $IN_GROUP;


if ($CUSTOM_MENU == 1) {
    /* This is a machine custom menu, so we propose to restore default location
     * menu */
    print "<table><tr><td>";
    printf(_T('This computer has a <u>custom boot menu</u>. <a href="%s">Click here</a> to get back the default one.', 'imaging'), $_SERVER['REQUEST_URI'] . '&reset_defaultMenu=1');
    ;
    print "</td></tr></table>";
}

if ($_GET['gid']) {
    /* This is a group custom menu, so we propose to restore default location
     * menu */
    print "<table><tr><td>";
    printf(_T('<a href="%s">Click here</a> to get back the default menu.', 'imaging'), $_SERVER['REQUEST_URI'] . '&reset_defaultMenu=1');
    print "</td></tr></table>";
}

if ($IN_GROUP == 1) {
    /* This machine is in an imaging group, so we propose to leave the group */
    $params = getParams();
    $uuid = $params['uuid'];

    if (safeCount($group = arePartOfAProfile(array($uuid)))) {

        $groupname = $group[$uuid]['groupname'];
        $groupid = $group[$uuid]['groupid'];
        print "<table><tr><td>";
        printf(_T('This computer is currently member of "%s". <a href="%s">Click here</a> to leave the group and customize the boot menu.', 'imaging'), $groupname, $_SERVER['REQUEST_URI'] . '&leave_group=1&group_uuid=' . $groupid);
        print "</td></tr></table>";
    }
}
?>
