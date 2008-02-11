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
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require("modules/base/graph/computers/index.css");

$p = new PageGenerator(_T("Request saver", "dyngroup"));
$p->setSideMenu($sidemenu);
$p->display();

$id = idGet();
$group = null; 
if ($id) { $group = new Group($id, true); }
$request = quickGet('request');
if (!$request) { $request = $group->getRequest(); }
if (!$request) { exit(0); }

$save_type = quickGet('save_type');
if (!$save_type && $group) { $save_type = ($group->isRequest() && 1 || 2); }
$name = quickGet('name');
$visible = quickGet('visible'); # TODO check all this!
if (!$visible && $group) { $visible = $group->show; }
$bool = quickGet('equ_bool');
if (!$bool && $group) { $bool = $group->getBool(); }

if ($name == '') {
    if ($id) { $name = $group->getName(); $visible = $group->canShow(); }
    $r = new Request();
    $r->parse($request);
    $r->displayReqListInfos();
    // TODO : put in class
    print "<hr/><table><form method='POST' action='".urlStr("base/computers/save", array('request'=>$request, 'id'=>$id)).  "' >".
        "<tr><td>Name : <input name='name' type='text' value='$name'/></td>".
        "<td>save as <select name='save_type'><option value='2' ".($save_type == 2 ? 'selected' : '').">group</option><option value='1' ".($save_type == 1 ? 'selected' : '').">query</option></select></td>".
        "<td>it should be <select name='visible'><option value='2'".($visible == 2 ? 'selected' : '').">hiden</option><option value='1' ".($visible == 1 ? 'selected' : '').">visible</option></select></td>";
    if ($r->countPart() > 1) {
        drawBoolEquation($bool);
    }
    print "<td><input value='"._T('Save', 'dyngroup')."' class='btnPrimary' type='submit'/></td></tr>".
        "</form></table>";
} else {
    if ($id) {
        $group = new Group($id, true);
        $group->setVisibility($visibility);
        $group->setName($name);
        $gid = $id;
    } else {
        $group = new Group();
        $gid = $group->create($name, $visible);
    }
    
    if ($save_type == 1) { // request save
        $r = new Request();
        $r->parse($request);
        $r->displayReqListInfos();
        print sprintf(_T("This request has been saved as %s (id=%s)", "dyngroup"), $name, $gid);
        $group->setRequest($request);
        $group->setBool($bool);
    } else { // result save
        $group->setRequest($request);
        $group->setBool($bool);
        $group->reload();
        print sprintf(_T("This result has been saved as %s (id=%s)", "dyngroup"), $name, $gid);
        displayStatic($group, 0, 10, '', $gid);
    }
    if ($visible == 1) { $group->show(); }
}


function drawBoolEquation($equ_bool) {
        print "</tr><tr><td colspan='2'>"._T("Enter Boolean operator bewteen groups", "dyngroup")." <input value='$equ_bool' name='equ_bool' type='input'/></td>";
}

function displayStatic($group, $start, $end, $filter, $gid) {
    $res = $group->getResult($start, $end, $filter);
    $len = $group->countResult($filter);

    foreach ($res as $host) {
        $hostname = $host['hostname'];
        $uuid = $host['uuid'];
        $p = $default_params;
        $p['delete'] = $hostname;
        $p['hostname'] = $hostname;
        $p['uuid'] = $uuid;
        $p['inventaire'] = $hostname;
        $comp = getComputer(array('uuid'=>$uuid));
        if ($comp) {
            $p['comment'] = $comp[1]['displayName'][0];
        }
        $parameters[$hostname] = $p;
    }
    
    list_computers($parameters, $filter, $len, false, $canbedeleted);
    print "<br/>";
}

?>
