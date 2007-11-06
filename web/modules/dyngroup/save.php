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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

$p = new PageGenerator(_T("Request saver"));
$p->setSideMenu($sidemenu);
$p->display();

$id = idGet();
$group = new Dyngroup($id);
$request = quickGet('request');
if (!$request) { $request = $group->getRequest(); }
if (!$request) { exit(0); }

$save_type = quickGet('save');
$name = quickGet('name');
$visible = quickGet('visible');
if (!$visible) { $visible = $group->show; }
$equ_bool = quickGet('equ_bool');
if (!$equ_bool) { $equ_bool = $group->getBool(); }

if ($name == '') {
    if ($id) { $name = $group->getName(); $visible = $group->canShow(); }
    $r = new Request();
    $r->parse($request);
    $r->displayReqListInfos();
    // TODO : put in class
    print "<hr/><table><form method='POST' action='".urlStr("dyngroup/dyngroup/save", array('request'=>$request, 'id'=>$id)).  "' >".
        "<tr><td>Name : <input name='name' type='text' value='$name'/></td>".
        "<td>save as <select name='save'><option value='0' ".($save_type == 0 ? 'selected' : '').">group</option><option value='1' ".($save_type == 1 ? 'selected' : '').">query</option></select></td>".
        "<td>it should be <select name='visible'><option value='2'".($visible == 2 ? 'selected' : '').">hiden</option><option value='1' ".($visible == 1 ? 'selected' : '').">visible</option></select></td>";
    if ($r->countPart() > 1) {
        drawBoolEquation($equ_bool);
    }
    print "<td><input value='"._T('Save')."' class='btnPrimary' type='submit'/></td></tr>".
        "</form></table>";
} else {
    if (!$id) { $id = get_next_dyngroup_id(); $group = new Dyngroup($id); }
    if (dyngroup_last_id() < $id) { save_dyngroup_id($id); }
    
    if ($save_type == 1) { // request save
        $r = new Request();
        $r->parse($request);
        $r->displayReqListInfos();
        print sprintf(_T("This request has been saved as %s (id=%s)"), $name, $id);
        $group->save($name, $r, null, $equ_bool);
    } else { // result save
        $r = new Request();
        $r->parse($request);
        $res = new Result($r, $equ_bool);
        $res->replyToRequest();
        if ($res->isEmpty()) {
            $r->displayReqListInfos();
            print _T("This request has no result.");
        } else {
            $res->displayResListInfos();
            print sprintf(_T("This result has been saved as %s (id=%s)"), $name, $id);
            $group->save($name, $r, $res, $equ_bool);
        }
    }
    if ($visible == 1) { $group->show(); }
}


function drawBoolEquation($equ_bool) {
        print "</tr><tr><td colspan='2'>"._T("Enter Boolean operator bewteen groups")." <input value='$equ_bool' name='equ_bool' type='input'/></td>";
}

?>
