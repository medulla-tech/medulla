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

require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");

$gid = quickGet('gid');
if (!$gid) { // TODO !!
    require("modules/base/computers/localSidebar.php");
    $request = quickGet('request');
    $r = new Request();
    $r->parse($request);
    $result = new Result($r, $group->getBool());
    $result->replyToRequest();
    $result->displayResListInfos();
} else {
    require("modules/imaging/manage/localSidebar.php");
    $group = getPGobject($gid, true);
    if (isset($items[$gid])) {
        $item = $items[$gid];
    } else {
        $item = null;
    }
    if ($group->type == 0) {
        __my_header(sprintf(_T("Group '%s' content", "dyngroup"), $group->getName()), $sidemenu, $item, $group);
    } else {
        __my_header(sprintf(_T("Display profile '%s' content", "dyngroup"), $group->getName()), $sidemenu, $item, $group);
    }
    $group->prettyDisplay();
}

function __my_header($label, $sidemenu, $item, $group) {
    $p = new PageGenerator($label);
    if (!empty($item)) {
        $sidemenu->forceActiveItem($item->action);
    } else {
        if ($group->type == 0) {
            /* Highlight the "All groups" menu item on the left if the group is
               not displayed on the menu bar */
            $sidemenu->forceActiveItem('list');
        } else {
            $sidemenu->forceActiveItem('list_profiles');
        }
    }
    $p->setSideMenu($sidemenu);
    $p->display();
    return $p;
}

?>

<style>
li.remove_machine a {
        padding: 1px 3px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("img/common/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>

