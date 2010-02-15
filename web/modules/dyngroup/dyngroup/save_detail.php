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

$p = new PageGenerator(_T("Request saver", "dyngroup"));
$p->setSideMenu($sidemenu);
$p->display();

$id = idGet();
$group = null; 
if ($id) { $group = new Group($id, true); } else { exit(-1); }
$name = $group->getName();
$request = $group->getRequest();

if ($group->isRequest()) { // request save
    $r = new Request();
    $r->parse($request);
    $r->displayReqListInfos(false, array('gid'=>$id));
    print sprintf(_T("This request has been saved as %s (id=%s)", "dyngroup"), $name, $id);
} else { // result save
    print sprintf(_T("This result has been saved as %s (id=%s)", "dyngroup"), $name, $id);
    displayStatic($group, 0, 10, '', $id);
}


function displayStatic($group, $start, $end, $filter, $gid) {
    $_GET['gid'] = $gid;
    $_GET['start'] = $start;
    $_GET['end'] = $end;

    $group->prettyDisplay();
}

?>
