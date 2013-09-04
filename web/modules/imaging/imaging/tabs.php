<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

if ($_GET['module'] == 'base' && $_GET['submod'] == 'computers') {
    require("modules/base/computers/localSidebar.php");
}
else {
    require("modules/imaging/manage/localSidebar.php");
}
require_once('graph/navbar.inc.php');
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once("modules/pulse2/includes/utilities.php");

$params = getParams();
$hostname = $params['hostname'];

global $SYNCHROSTATE_UNKNOWN;
global $SYNCHROSTATE_TODO;
global $SYNCHROSTATE_SYNCHRO;
global $SYNCHROSTATE_RUNNING;
global $SYNCHROSTATE_INIT_ERROR;

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

if (isset($_POST['bsync'])) {
    if (isset($params['uuid'])) {
        $ret = xmlrpc_synchroComputer($params['uuid']);
    } else {
        $ret = xmlrpc_synchroProfile($params['gid']);
    }
    // goto images list
    if ($ret[0] and !isXMLRPCError()) {
        /* insert notification code here if needed */
    } elseif (!$ret[0] and !isXMLRPCError()) {
         unset($_SESSION["imaging.isComputerInProfileRegistered_".$params['uuid']]);
         unset($_SESSION["imaging.isComputerRegistered_".$params['uuid']]);
         if (!xmlrpc_isComputerInProfileRegistered($params['uuid']) && !xmlrpc_isComputerRegistered($params['uuid'])) {
            new NotifyWidgetFailure(sprintf(_T("This computer is no longer registered : %s", "imaging"), $params['uuid']));
            header("Location: ".urlStrRedirect("base/computers/index", $params));
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
        if (count($canReg) == 2 and $canReg[1] != '') {
            $group = new Group($canReg[1], true);
            $params = array("id"=>$canReg[1], "gid"=>$canReg[1], "groupname"=>$group->getName());
            $url = urlStr("imaging/manage/groupimgtabs", $params);
            $msg = sprintf(_T("Please declare the imaging group first %shere%s.", "imaging"), "<a href='$url'>", "</a>");
            $t2 = new TitleElement($msg, 3);
            $t2->display();
        }
    } else {
        $ret = xmlrpc_getComputerSynchroState($params['target_uuid']);
        if (isset($_POST["bresetsynchrostate"])) {
            if (xmlrpc_resetSynchroState($params['uuid'], '')) {
                new NotifyWidgetSuccess(sprintf(_T("Reset synchronisation state for %s (%s) succeed", "imaging"), $params['target_name'], $params['uuid']));
                header("Location: ".urlStrRedirect("base/computers/imgtabs", $params));
                exit;
            } else {
                new NotifyWidgetFailure(sprintf(_T("Failed to reset synchronise state.", "imaging")));
            }
        }

        if ($ret['id'] == $SYNCHROSTATE_RUNNING) {
            $p = new PageGenerator(sprintf(_T("%s's computer imaging", 'imaging'), $hostname));
            $sidemenu->forceActiveItem("index");
            $p->setSideMenu($sidemenu);
            $p->display();
            $a_href_open = "<a href=''>";

            $msg = sprintf(_T("Generating boot menu... Please wait or reload the page %shere%s.<br/>", "imaging"), $a_href_open, '</a>');
            $t1 = new TitleElement($msg, 3);
            $t1->display();
            $msg = sprintf(_T("If the processing exceeds 5 minutes, please reset the synchro state of this computer.", "imaging"));
            $t2 = new TitleElement($msg, 3);
            $t2->display();

            $f = new ValidatingForm();
            $f->add(new HiddenTpl("target_uuid"),                    array("value" => $target_uuid,            "hide" => True));
            $f->add(new HiddenTpl("target_name"),                    array("value" => $target_name,            "hide" => True));
            $f->add(new HiddenTpl("type"),                           array("value" => $type,                   "hide" => True));
            $f->addButton("bresetsynchrostate", _T("Reset Synchro state", "imaging"));
            $f->display();

        } elseif ($ret['id'] == $SYNCHROSTATE_INIT_ERROR) {
            $p = new PageGenerator(sprintf(_T("%s's computer imaging", 'imaging'), $hostname));
            $sidemenu->forceActiveItem("index");
            $p->setSideMenu($sidemenu);
            $p->display();
            print _T("The registering in the imaging server has failed.", "imaging");
        } else {
            # do nothing special if $SYNCHROSTATE_DONE
            $p = new TabbedPageGenerator();
            $sidemenu->forceActiveItem("index");
            $p->setSideMenu($sidemenu);
            global $stateid;
            $stateid = $ret['id'];

            # check if we are in a profile
            $in_profile = xmlrpc_isComputerInProfileRegistered($params['target_uuid']);
            if ($in_profile) {
                $p->addTop(sprintf(_T("%s's computer imaging (in group)", 'imaging'), $hostname),
                    "modules/imaging/imaging/header.php");
            } else {
                $p->addTop(sprintf(_T("%s's computer imaging", 'imaging'), $hostname),
                    "modules/imaging/imaging/header.php");
            }

            $p->addTab("tabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"),
                "modules/imaging/imaging/bootmenu.php", $params);
            $p->addTab("tabimages", _T("Images and Masters", 'imaging'), "",
                "modules/imaging/imaging/images.php", $params);
            $p->addTab("tabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"),
                "modules/imaging/imaging/services.php", $params);
            $p->addTab("tabimlogs", _T("Imaging log", 'imaging'), "",
                "modules/imaging/imaging/logs.php", $params);
            $p->addTab("tabconfigure", _T("Menu configuration", 'imaging'), "",
                "modules/imaging/imaging/configure.php", $params);
            $p->display();
        }
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

    if ($group->exists == False) {
        require("modules/msc/includes/widgets.inc.php");
        # TODO need to use a generic widget!

        $msc_host = new RenderedMSCGroupDontExists($_GET['gid']);
        $msc_host->headerDisplay();
    } else {
        $ret = xmlrpc_getProfileSynchroState($params['target_uuid']);

        if (isset($_POST["bresetsynchrostate"])) {
            if (xmlrpc_resetSynchroState($params['target_uuid'], $params['type'])) {
                new NotifyWidgetSuccess(sprintf(_T("Reset synchronisation state for %s (%s) succeed", "imaging"), $params['target_name'], $params['target_uuid']));
                header("Location: ".urlStrRedirect("base/computers/imgtabs", $params));
                exit;
            } else {
                new NotifyWidgetFailure(sprintf(_T("Failed to reset synchronise state.", "imaging")));
            }
        }

        if ($ret['id'] == $SYNCHROSTATE_RUNNING) {
            $p = new PageGenerator(sprintf(_T("%s's profile imaging", 'imaging'), $group->getName()));
            $sidemenu->forceActiveItem("index");
            $p->setSideMenu($sidemenu);
            $p->display();
            $a_href_open = "<a href=''>";

            $msg = sprintf(_T("Generating boot menu... Please wait or reload the page %shere%s.<br/>", "imaging"), $a_href_open, '</a>');
            $t1 = new TitleElement($msg, 3);
            $t1->display();
            $msg = sprintf(_T("If the processing exceeds 5 minutes, please reset the synchro state of this computer.", "imaging"));
            $t2 = new TitleElement($msg, 3);
            $t2->display();

            $f = new ValidatingForm();
            $f->add(new HiddenTpl("gid"),                    array("value" => $params['target_uuid'],            "hide" => True));
            $f->add(new HiddenTpl("groupname"),                    array("value" => $params['target_name'],            "hide" => True));
            $f->add(new HiddenTpl("type"),                           array("value" => $params['type'],                   "hide" => True));
            $f->addButton("bresetsynchrostate", _T("Reset Synchro state", "imaging"));
            $f->display();

        } else {
            # do nothing special if $SYNCHROSTATE_DONE
            $p = new TabbedPageGenerator();
            $sidemenu->forceActiveItem("list_profiles");
            $p->setSideMenu($sidemenu);
            global $stateid;
            $stateid = $ret['id'];

            $params['groupname'] = $group->getName();
            $params['target_name'] = $params['groupname'];
            $p->addTop(sprintf(_T("%s's imaging group", 'imaging'), $group->getName()),
                "modules/imaging/imaging/header.php");
            $p->addTab("grouptabbootmenu", _T("Boot menu", 'imaging'), _T("Current boot menu", "imaging"),
                "modules/imaging/imaging/bootmenu.php", $params);
            $p->addTab("grouptabimages", _T("Masters", 'imaging'), "",
                "modules/imaging/imaging/images.php", $params);
            $p->addTab("grouptabservices", _T("Boot services", 'imaging'), _T("Available boot menu services", "imaging"),
                "modules/imaging/imaging/services.php", $params);
            $p->addTab("grouptabimlogs", _T("Imaging log", 'imaging'), "",
                "modules/imaging/imaging/logs.php", $params);
            $p->addTab("grouptabconfigure", _T("Menu configuration", 'imaging'), "",
                "modules/imaging/imaging/configure.php", $params);
            $p->display();
        }
    }
} else {
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->display();
    print _T("Not enough informations", "imaging");
}

?>
