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
require("modules/base/graph/computers/index.css");

function quickGet1($s) { return quickGet($s, false, false); }
$name = quickGet1('name');
if ($name) {
    $p = new PageGenerator(sprintf(_T("Temporary result display for '%s'", "dyngroup"), $name));
} else {
    $p = new PageGenerator(_T("Temporary result display", "dyngroup"));
}
$p->setSideMenu($sidemenu);
$p->display();

$get = '';
$bool = quickGet1('equ_bool', true);
if (strlen($_GET['id']) && !strlen($bool)) {
    $group = new Group($_GET['id'], true);
    $bool = $group->getBool();
}
if (strlen($bool)) { $get = "&equ_bool=".urlencode($bool); }

$get .= "&request=".urlencode($_GET['request']);
$get .= "&name=".urlencode($name);
$get .= "&save_type=".quickGet('save_type', true);
$get .= "&visible=".quickGet('visible', true);
$get .= "&is_group=".quickGet('is_group', true);
if (strlen($_GET['id'])) {
    $get .= "&id=".urlencode($_GET['id']);
}
print "<a href='main.php?module=base&submod=computers&action=creator_step2$get'>"._T('back', 'dyngroup')."</a>";

include("modules/pulse2/pulse2/computers_list.php");
# TODO put bool in the first page whereas it is actualy in the second

?>
