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
if (!$save_type && $group) { $save_type = ($group->isRequest() ? 1 : 2); }
$name = quickGet('name');
$visible = quickGet('visible'); # TODO check all this!
if (!$visible && $group) { $visible = $group->show; }
$bool = quickGet('equ_bool');
if (!$bool && $group) { $bool = $group->getBool(); }

if ($name == '' || xmlrpc_group_name_exists($name, $group->id)) {
    if ($id) { $name = $group->getName(); $visible = $group->canShow(); }
    $r = new Request();
    $r->parse($request);
    $r->displayReqListInfos();
    // TODO : put in class
    print "<hr/><table><form method='POST' action='".urlStr("base/computers/save", array('request'=>$request, 'id'=>$id)).  "' >".
        "<tr><td>"._T('Name :', 'dyngroup')." <input name='name' type='text' value='$name'/></td>".
        "<td>"._T('save as', 'dyngroup')." <select name='save_type'><option value='1' ".($save_type == 1 ? 'selected' : '').">"._T("query", "dyngroup")."</option><option value='2' ".($save_type == 2 ? 'selected' : '').">"._T('result', 'dyngroup')."</option></select></td>".
        "<td>"._T("it should be", "dyngroup")." <select name='visible'><option value='2' ".($visible == 2 ? 'selected' : '').">"._T("hidden", "dyngroup")."</option><option value='1' ".($visible == 1 ? 'selected' : '').">"._T("visible", "dyngroup")."</option></select></td>";
    if ($r->countPart() > 0) {
        drawBoolEquation($bool);
    }
    print "<td><input name='btnPrimary' value='"._T('Save', 'dyngroup')."' class='btnPrimary' type='submit'/></td></tr>".
        "</form></table>";
    if (xmlrpc_group_name_exists($name, $group->id)) {
        new NotifyWidgetFailure(sprintf(_T("A group already exists with name '%s'", "dyngroup"), $name));
    } elseif (isset($_POST['btnPrimary'])) {
        new NotifyWidgetFailure(_T("You must specify a group name", "dyngroup"));
    }
} else {
    if ($id) {
        $group = new Group($id, true);
        $group->setVisibility($visible);
        $group->setName($name);
        $gid = $id;
    } else {
        $group = new Group();
        $gid = $group->create($name, $visible);
    }

    if ($save_type == 1) { // request save
        $group->setRequest($request);
        $group->setBool($bool);
    } else { // result save
        $group->setRequest($request);
        $group->setBool($bool);
        $group->reload();
    }
    if ($visible == 1) { $group->show(); }
    header("Location: " . urlStrRedirect("base/computers/save_detail", array('id'=>$gid)));
}


function drawBoolEquation($equ_bool) {
        print "</tr><tr><td colspan='2'>"._T("Enter boolean operator between groups", "dyngroup")." <input value='$equ_bool' name='equ_bool' type='input'/></td>";
}

?>
