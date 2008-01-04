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

require("modules/base/computers/localSidebar.php");
require("modules/base/graph/computers/index.css");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once("modules/glpi/includes/xmlrpc.php");

$gid = quickGet('gid');
if (!$gid) {
    $request = quickGet('request');
    $r = new Request();
    $r->parse($request);
    $result = new Result($r, $group->getBool());
    $result->replyToRequest();
    $result->displayResListInfos();
} else {
    $group = new Stagroup($gid);
    
    $p = new PageGenerator(sprintf(_T("Display '%s' result list", "dyngroup"), $group->getName()));
    $item = $items[$gid];
    $sidemenu->forceActiveItem($item->action);
    $p->setSideMenu($sidemenu);
    $p->display();
    
    if ($group->isDyn()) {
        $group = $group->toDyn();
        $r = new Request();
        $r->parse($group->getRequest());
        $res = new Result($r, $group->getBool());
    
        if ($group->isGroup()) {
            $res->parse($group->getResult());
            $res->displayResListInfos(true, array('gid'=>$gid), 'display');
        } else {
            $res->replyToRequest();
            $res->displayResListInfos();
        }
    } else {
        $group->prettyDisplay();
    }
}

?>

<style>
li.remove_machine a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/delete.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>

