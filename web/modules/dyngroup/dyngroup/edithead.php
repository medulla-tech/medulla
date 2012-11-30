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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once("modules/pulse2/includes/utilities.php");

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

$gid = idGet();
$group = getPGobject($gid, True);
$edition = True;

if ($group->isDyn()) {
    if ($group->type == 0) {
        $title = _T("Edit a dynamic group", 'dyngroup');
    } else {
        /* shouldn't happen */
        $title = _T("Edit a profile", 'dyngroup');
    }
    $p = new PageGenerator($title);
    $p->setSideMenu($sidemenu);
    $p->display();

    require("creator.php");
} else {
    if ($group->type == 0) {
        $title = _T("Edit a static group", 'dyngroup');
    } else {
        $title = _T("Edit a profile", 'dyngroup');
    }
    $p = new PageGenerator($title);
    $p->setSideMenu($sidemenu);
    $p->display();

    require("add_groups.php");
}

?>

