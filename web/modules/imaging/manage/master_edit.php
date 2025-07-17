<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/post_install_script.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");

$id = $_GET['itemid'];
$location = getCurrentLocation();
$masters = xmlrpc_getLocationMastersByUUID($location, array($id));

if(safeCount($_POST) == 0) {

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

    $post_installs = "";
    $f = get_post_install_scripts($f, array(), $post_installs);

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
        if (preg_match('/order_/', $post_key)) {
            $post_key = str_replace("order_", "", $post_key);
            $p_order[$post_key] = $post_value;
        }
    }
    $params['post_install_scripts'] = $p_order;

    $ret = xmlrpc_editImageLocation($item_uuid, $loc_uuid, $params);

    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Master <strong>%s</strong> modified with success", "imaging"), $label);
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                        "IMG",
                                        '',
                                        0,
                                        $label ,
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Imaging | Master | Menu | Edit | Iso |Start | Manual');

        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } else {
        $str = sprintf(_T("Master %s modified with error", "imaging"), $label);
        $str .= "Error : ".$ret[1];
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                        "IMG",
                                        '',
                                        0,
                                        $label ,
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'Imaging | Master | Menu | Edit | Iso |Start | Manual');
        new NotifyWidgetFailure($ret[1]);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    }
}

?>
