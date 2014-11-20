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

$is_group = quickGet('is_group');

$p = new PageGenerator(sprintf(_T("Request saver (%s)", "dyngroup"), ($is_group?_T('group', 'dyngroup'):_T('profile', 'dyngroup'))));
$p->setSideMenu($sidemenu);
$p->display();

$id = idGet();
$group = null;
if ($id) { $group = getPGobject($id, true); }
$imaging_server = quickGet('imaging_server');
$request = quickGet('request');
if ($request == 'stored_in_session') {
    $request = $_SESSION['request'];
    unset($_SESSION['request']);
}
if (!$request) { $request = $group->getRequest(); }
if (!$request) { exit(0); }

$save_type = quickGet('save_type', true);
if (!$save_type && $group) { $save_type = ($group->isRequest() ? 1 : 2); }
$name = quickGet('name', true, False);
$visible = quickGet('visible', true); # TODO check all this!
if (!$visible && $group) { $visible = $group->show; }
$bool = quickGet('equ_bool', true);
if (!$bool && $group) {
    if (isset($_POST['checkBool']) || isset($_POST['btnPrimary'])) {
        $bool = '';
    } else {
        $bool = $group->getBool();
    }
}
$r = new Request();
$r->parse($request);

$check = checkBoolEquation($bool, $r, isset($_POST['checkBool']));
if ($check && isset($_POST['displayTmp'])) {
    $_SESSION['request'] = $r->toS();
    header("Location: " . urlStrRedirect("base/computers/tmpdisplay", array('id'=>$id, 'request'=>'stored_in_session', 'is_group'=>$is_group, 'equ_bool'=>$bool, 'name'=>urlencode($name), 'save_type'=>$save_type, 'visible'=>$visible, 'imaging_server'=>$imaging_server)));
    exit;
}

$name_exists = xmlrpc_group_name_exists($name, $group->id);
if (!isset($_POST['btnPrimary']) || $name_exists || !$check || isset($_POST['checkBool']) || isset($_POST['displayTmp']) || $name == '') {
    if ($id) { $name = $group->getName(); $visible = $group->canShow(); }
    $r->displayReqListInfos(false, array('gid'=>$id));
    // TODO : put in class
    print "<hr/><table><tr>";
    if (hasCorrectAcl("base", "computers", "save")) {
        $_SESSION['request'] = $request;
        print "<form method='POST' action='".urlStr("base/computers/save", array('request'=>'stored_in_session', 'id'=>$id, 'is_group'=>$is_group, 'imaging_server'=>$imaging_server)).  "' >".
            "<td>"._T('Name :', 'dyngroup')." <input name='name' type='text' value=\"" . htmlspecialchars($name) . "\" /></td>";
            if ($is_group) {
                print "<td>"._T('save as', 'dyngroup')." <select name='save_type'><option value='1' ".($save_type == 1 ? 'selected' : '').">"._T("query", "dyngroup")."</option><option value='2' ".($save_type == 2 ? 'selected' : '').">"._T('result', 'dyngroup')."</option></select></td>";
            } else {
                print "<td><input name='save_type' type='hidden' value='2'/></td>";
            }
            print "<td colspan='2'>"._T("Make favourite", "dyngroup")." <select name='visible'><option value='2' ".($visible == 2 ? 'selected' : '').">"._T("No", "dyngroup")."</option><option value='1' ".($visible == 1 ? 'selected' : '').">"._T("Yes", "dyngroup")."</option></select></td>";
    }
    if ($r->countPart() > 0) {
        drawBoolEquation($bool);
    }
    if (hasCorrectAcl("base", "computers", "tmpdisplay")) {
        drawTemporaryButton();
    }
    
    if (hasCorrectAcl("base", "computers", "save")) {
        print "<td><input name='btnPrimary' value='"._T('Save', 'dyngroup')."' class='btnPrimary' type='submit'/></td>";
    }
    print "</tr></form></table>";
    if ($name_exists && !isset($_POST['displayTmp'])) { 
        new NotifyWidgetFailure(sprintf(_T("A group already exists with name '%s'", "dyngroup"), $name));
    } elseif ($name == '' && $check && $id) {
        new NotifyWidgetFailure(_T("You must specify a group name", "dyngroup"));
    } elseif (isset($_POST['btnPrimary']) && $check) {
        new NotifyWidgetFailure(_T("You must specify a group name", "dyngroup"));
    }
} else {
    if ($id) {
        $group = getPGobject($id, true);
        $group->setVisibility($visible);
        $group->setName($name);
        $gid = $id;
    } else {
        if ($is_group) {
            $group = new Group();
        } else {
            $group = new Profile();
        }
        $gid = $group->create($name, $visible);
        if (!$is_group) {
            $group->setImagingServer($imaging_server);
        }
    }

    $request = $r->toS();
    if ($save_type == 1) { // request save
        $group->setRequest($request);
        $group->setBool($bool);
    } else { // result save
        $group->setRequest($request);
        $group->setBool($bool);
        $group->reload();
        if ($group->type == 1) { /* if it's a profile, we remove the request part */
            $group->removeRequest();
        }
    }
    if ($visible == 1) { $group->show(); }
    if ($group->type == 0) {
        header("Location: " . urlStrRedirect("base/computers/save_detail", array('id'=>$gid, 'is_group'=>$is_group)));
        exit;
    } else {
        header("Location: " . urlStrRedirect("base/computers/display", array('id'=>$gid, 'gid'=>$gid, 'is_group'=>$is_group, 'groupname'=>$group->name)));
        exit;
    }
}


function drawBoolEquation($equ_bool) {
    print "</tr><tr><td colspan='2'>"._T("Specify a boolean operator between sub-requests", "dyngroup")." <input value='$equ_bool' name='equ_bool' type='input'/><input name='checkBool' value='"._T('Check', 'dyngroup')."' type='submit'/></td>";
}

function checkBoolEquation($bool, $r, $display_success) {
    $chk = checkBoolean($bool);
    if (!$chk[0]) {
        new NotifyWidgetFailure(sprintf(_T("The boolean equation '%s' is not valid", "dyngroup"), $bool));
        return False;
    } elseif ($chk[1] != -1 and $chk[1] != count($r->subs)) {
        new NotifyWidgetFailure(sprintf(_T("The boolean equation '%s' is not valid.<br/>Not the same number of sub-requests", "dyngroup"), $bool));
        return False;
    } elseif ($display_success) {
        new NotifyWidgetSuccess(sprintf(_T("The boolean equation is valid", "dyngroup")));
        return True;
    }
    return True;
}

function drawTemporaryButton() {
     print "<td><input name='displayTmp' value='"._T("Display content", "dyngroup")."' type='submit'/></td>";
}
?>
