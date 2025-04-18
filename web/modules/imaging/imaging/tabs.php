<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com/
 * (c) 2023-2025 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Medulla Management Console (MMC).
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
if ($_GET['module'] == 'base' && $_GET['submod'] == 'computers') {
    require("modules/base/computers/localSidebar.php");
} else {
    require("modules/imaging/manage/localSidebar.php");
}
require_once('graph/navbar.inc.php');
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once("modules/medulla_server/includes/utilities.php");

$params = getParams();
$hostname = $params['hostname'];

global $CUSTOM_MENU;
global $IN_GROUP;

$CUSTOM_MENU = -1;
$IN_GROUP = -1;

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

//  ===============================================================
// Restore default location boot menu
//  ===============================================================

function resetDefaultMenu($uuid)
{
    $ret = xmlrpc_resetComputerBootMenu($uuid);
    if (!isXMLRPCError() && $ret) {
        new NotifyWidgetSuccess(sprintf(_T("Default menu has been successfully restored.", "imaging")));
    }
}

function resetDefaultMenus($uuids)
{
    $ret = xmlrpc_resetComputerBootMenus($uuids);
    if (!isXMLRPCError() && $ret) {
        new NotifyWidgetSuccess(sprintf(_T("Default menu has been successfully restored.", "imaging")));
    }
}

if (isset($_GET['reset_defaultMenu']) && $_GET['reset_defaultMenu'] == 1) {
    if(isset($_GET['target']) && $_GET['target'] == "all") {
        $location = htmlentities($_GET['location']);
        $menusIds = xmlrpc_getMenusbylocation($location);
        resetDefaultMenus($menusIds);
        header("Location: " . urlStrRedirect("imaging/manage/index"));
        exit;
    } else {
        resetDefaultMenu($params['uuid']);
    }
}


//  ===============================================================
// Leave a group and reset default bootmenu
//  ===============================================================

if (isset($_GET['leave_group'], $_GET['group_uuid'], $params['uuid'])) {
    // Leave the group
    $uuid = $params['uuid'];
    $ret = __xmlrpc_delmembers_to_group($_GET['group_uuid'], array($uuid => array('uuid' => $uuid)));
    if (!isXMLRPCError() && $ret) {
        resetDefaultMenu($params['uuid']);
    }
}

if (isset($_POST['bsync'])) {
    if (!isset($params['uuid'])){
        $location = getCurrentLocation();
        if ($location == "UUID1") {
            $location_name = _T("root", "pulse2");
        } else {
            $location_name = xmlrpc_getLocationName($location);
        }
        $objprocess = array();
        $scriptmulticast = 'multicast.sh';
        $path = "/tmp/";
        $objprocess['location'] = $location;
        $objprocess['process'] = $path.$scriptmulticast;
        //if (xmlrpc_muticast_script_exist($objprocess)){

        if (xmlrpc_check_process_multicast($objprocess)) {
            $msg = _T("The bootmenus cannot be generated as a multicast deployment is currently running.", "imaging");
            new NotifyWidgetFailure($msg);
            header("Location: " . urlStrRedirect("imaging/manage/index"));
            exit;
        } else {
            xmlrpc_clear_script_multicast($objprocess);
        }
    }
    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        /* insert notification code here if needed */
    } elseif (!$ret[0] and !isXMLRPCError()) {
        unset($_SESSION["imaging.isComputerInProfileRegistered_" . $params['uuid']]);
        unset($_SESSION["imaging.isComputerRegistered_" . $params['uuid']]);
        if (!xmlrpc_isComputerInProfileRegistered($params['uuid']) && !xmlrpc_isComputerRegistered($params['uuid'])) {
            new NotifyWidgetFailure(sprintf(_T("This computer is no longer registered : %s", "imaging"), $params['uuid']));
            header("Location: " . urlStrRedirect("base/computers/index", $params));
            exit;
        } else {
            new NotifyWidgetFailure(sprintf(_T("Boot Menu Generation failed for : %s", "imaging"), implode(', ', $ret[1])));
        }
    }
}

if (isset($params['uuid'])) {
    $_GET['type'] = '';
    $_GET['target_uuid'] = $params['uuid'];
    $_GET['target_name'] = $params['hostname'];
    unset($_GET['gid']);
    $params['type'] = '';
    $params['target_uuid'] = $params['uuid'];
    $params['target_name'] = $params['hostname'];
    if (!isset($_GET['uuid']) || $_GET['uuid'] == '') {
        $_GET['uuid'] = $params['uuid'];
    }

    $params['hostname'] = $hostname;

    $canReg = xmlrpc_canIRegisterThisComputer($params['target_uuid']);
    if (!$canReg[0] && $canReg[1]) {
        $p = new PageGenerator(sprintf(_T("%s's computer imaging", 'imaging'), $hostname));
        $sidemenu->forceActiveItem("index");
        $p->setSideMenu($sidemenu);
        $p->display();
        # when the computer is in a profile, but the profile is not registered
        # display an information message
        $msg = _T("This computer can't be declared in the imaging module: it's already part of a broken imaging group.", "imaging");
        $t1 = new TitleElement($msg, 3);
        $t1->display();
        # give a link to the profile registering
        if (safeCount($canReg) == 2 and $canReg[1] != '') {
            $group = new Group($canReg[1], true);
            $params = array("id" => $canReg[1], "gid" => $canReg[1], "groupname" => $group->getName());
            $url = urlStr("imaging/manage/groupimgtabs", $params);
            $msg = sprintf(_T("Please declare the imaging group first %shere%s.", "imaging"), "<a href='$url'>", "</a>");
            $t2 = new TitleElement($msg, 3);
            $t2->display();
        }
    } else {
        $p = new TabbedPageGenerator();
        $sidemenu->forceActiveItem("index");
        $p->setSideMenu($sidemenu);

        # check if we are in a profile
        $in_profile = xmlrpc_isComputerInProfileRegistered($params['target_uuid']);
        if ($in_profile) {
            $p->addTop(sprintf(_T("%s's computer imaging (in group)", 'imaging'), $hostname), "modules/imaging/imaging/header.php");
            $IN_GROUP = 1;
        } else {
            $CUSTOM_MENU = xmlrpc_getComputerCustomMenuFlag($params['target_uuid']);
            $p->addTop(sprintf(_T("%s's computer imaging", 'imaging'), $hostname), "modules/imaging/imaging/header.php");
            $IN_GROUP = 0;
        }

        $p->addTab("tabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"), "modules/imaging/imaging/bootmenu.php", $params);
        $ddd = $params;
        // $ddd['namee'] = "llllllllll";
        $p->addTab("tabimages", _T("Images and Masters", 'imaging'), "", "modules/imaging/imaging/images.php", $ddd);
        $p->addTab("tabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"), "modules/imaging/imaging/services.php", $params);
        $p->addTab("tabimlogs", _T("Imaging log", 'imaging'), "", "modules/imaging/imaging/logs.php", $params);
        $p->addTab("tabconfigure", _T("Menu configuration", 'imaging'), "", "modules/imaging/imaging/configure.php", $params);
        $p->display();
    }
} elseif (isset($params['gid'])) {
    $_GET['type'] = 'group';
    $params['groupname'] = $_GET['groupname'];
    $_GET['target_uuid'] = $params['gid'];
    $_GET['target_name'] = $params['groupname'];
    $params['type'] = 'group';
    $params['target_uuid'] = $params['gid'];
    $params['target_name'] = $params['groupname'];

    require("modules/dyngroup/includes/includes.php");
    $group = new Group($_GET['gid'], true);

    if ($group->exists == false) {
        require("modules/msc/includes/widgets.inc.php");
        # TODO need to use a generic widget!

        $msc_host = new RenderedMSCGroupDontExists($_GET['gid']);
        $msc_host->headerDisplay();
    } else {
        $p = new TabbedPageGenerator();
        $sidemenu->forceActiveItem("list_profiles");
        $p->setSideMenu($sidemenu);
        $params['groupname'] = $group->getName();
        $params['target_name'] = $params['groupname'];
        $p->addTop(sprintf(_T("%s's imaging group", 'imaging'), $group->getName()), "modules/imaging/imaging/header.php");
        $p->addTab("grouptabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"), "modules/imaging/imaging/bootmenu.php", $params);
        $p->addTab("grouptabimages", _T("Masters", 'imaging'), "", "modules/imaging/imaging/images.php", $params);
        $p->addTab("grouptabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"), "modules/imaging/imaging/services.php", $params);
        $p->addTab("grouptabimlogs", _T("Imaging log", 'imaging'), "", "modules/imaging/imaging/logs.php", $params);
        $p->addTab("grouptabconfigure", _T("Menu configuration", 'imaging'), "", "modules/imaging/imaging/configure.php", $params);
        $p->display();
    }
} else {
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->display();
    print _T("Not enough information", "imaging");
}
