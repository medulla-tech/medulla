<?php

/*
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/*
 * Edit/Duplicate page for post-imaging script
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

// id of the script
$script_id = $_GET['itemid'];
$location = getCurrentLocation();
$script = xmlrpc_getPostInstallScript($script_id, $location);

// if task is not defined, we are in edit mode
if (!isset($task)) {
    $task = "edit";
}

if ($task == "edit") {
    $name = $script["default_name"];
    $desc = $script["default_desc"];
    $id = $script["id"];
    $title = "Edit post-imaging script";
    $action = "updated";
} elseif ($task == "duplicate") {
    $name = "";
    $desc = $script["default_desc"];
    $id = "";
    $title = "Duplicate post-imaging script";
    $action = "created";
}

// create page
$p = new PageGenerator(_T($title, "imaging"));
$sidemenu->setBackgroundImage("modules/imaging/graph/images/section_large.png");
$sidemenu->forceActiveItem("postinstall");
$p->setSideMenu($sidemenu);
$p->display();

// form has been posted
if (count($_POST) > 0) {
    // get the script values
    $script_id = $_GET["itemid"];
    $script_name = trim($_POST["postinstall_name"]);
    $script_value = $_POST["postinstall_value"];
    $script_desc = $_POST["postinstall_desc"];

    if ($task == "edit"){
        /*
         * First step, we edit postinstall script on database
         * Second step, we must edit postinstall script on /var/lib/pulse2/imaging/master/postinst.d/
         * To do this, we have to check if a machine have a linked master with this postinstall script
         * If True, synchronize bootmenu of this computer will update postinstall script
         */
        // store new values for script
        $ret = xmlrpc_editPostInstallScript($script_id, array('default_name'=>$script_name, 'default_desc'=>$script_desc, 'value'=>$script_value));
        if ($ret) {
            // If this postinstall script is used, try to update it
            $computer_uuid = xmlrpc_getAComputerWithThisPostInstallScript($script_id);
            if ($computer_uuid)
                $ret = xmlrpc_synchroComputer($computer_uuid);
        }
    } elseif ($task == "duplicate") {
        // create new script
        $ret = xmlrpc_addPostInstallScript($location, array('default_name'=>$script_name, 'default_desc'=>$script_desc, 'value'=>$script_value));
    }
    // check result
    if ((is_array($ret) && $ret[0]) || $ret) {
        $str = sprintf(_T("<strong>%s</strong> script %s", "imaging"), $script_name, $action);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/postinstall"));
        exit;
    } elseif (count($ret) > 1) {
        new NotifyWidgetFailure($ret[1]);
    } else {
        $str = sprintf(_T("<strong>%s</strong> script wasn't %s", "imaging"), $script_name, $action);
        new NotifyWidgetFailure($str);
    }
}

// Display the script edit form
$f = new ValidatingForm();
$textareadesc = new TextareaTpl("postinstall_desc");
$textareadesc->setRows(2);
$textareadesc->setCols(50);

$textarea = new TextareaTpl("postinstall_value");
$textarea->setRows(15);
$textarea->setCols(50);
$f->push(new Table());
$disabled = (!$script['is_local'] && $task == 'edit');
$f->add(
    new TrFormElement("Script name", new InputTpl("postinstall_name")),
    array("value" => $name, "required" => True, 'disabled' => ($disabled?'disabled':''))
);
$f->add(
    new TrFormElement("Script description", $textareadesc),
    array("value" => $desc, "required" => True, 'disabled' => ($disabled?'disabled':''))
);
$f->add(
    new TrFormElement(_T("Script value"), $textarea),
    array("value" => $script['value'], "required" => True, 'disabled' => ($disabled?'disabled':''))
);
$f->pop();
$f->addButton("bvalid", _T("Validate"));
$f->display();

?>
