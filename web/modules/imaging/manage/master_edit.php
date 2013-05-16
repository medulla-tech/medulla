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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/post_install_script.php');

$id = $_GET['itemid'];
$location = getCurrentLocation();
$masters = xmlrpc_getLocationMastersByUUID($location, array($id));

if(count($_POST) == 0) {

    // get current values
    $master = $masters[$id];
    $label = $master['name'];
    $desc = $master['desc'];

    $p = new PageGenerator(_T("Edit master : ", "imaging").$label);
    $sidemenu->forceActiveItem("master");
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm();
    $f->push(new Table());
    $f->add(new HiddenTpl("itemid"),                        array("value" => $id,                     "hide" => True));

    $f->add(
        new TrFormElement(_T("Label", "imaging"), new InputTpl("image_label")),
        array("value" => $label)
    );
    $f->add(
        new TrFormElement(_T("Description", "imaging"), new InputTpl("image_description")),
        array("value" => $desc)
    );

    $f->pop();

    list($count, $post_installs) = xmlrpc_getAllPostInstallScripts($location);
    if (isset($master['post_install_scripts'])) {
        $f = get_post_install_scripts($f, $master['post_install_scripts'], $post_installs);
    } else {
        $f = get_post_install_scripts($f, array(), $post_installs);
    }

    $f->addButton("bvalid", _T("Validate"));
    $f->display();
} else {
    $item_uuid = $_POST['itemid'];
    $loc_uuid = getCurrentLocation();

    $params = array();
    $params['name'] = $_POST['image_label'];
    $params['desc'] = $_POST['image_description'];
    $params['post_install_script'] = $_POST['post_install'];
    $params['is_master'] = True;

    $p_order = array();
    foreach ($_POST as $post_key => $post_value) {
        if (ereg('order_', $post_key)) {
            $post_key = str_replace("order_", "", $post_key);
            $p_order[$post_key] = $post_value;
        }
    }
    $params['post_install_scripts'] = $p_order;

    $ret = xmlrpc_editImageLocation($item_uuid, $loc_uuid, $params);

    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Master <strong>%s</strong> modified with success", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } else {
        new NotifyWidgetFailure($ret[1]);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    }
}

?>
