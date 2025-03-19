<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2025 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

$params = getParams();
$location = getCurrentLocation();
$item_uuid = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);

$item = xmlrpc_getMenuItemByUUID($item_uuid);

$is_image = False;
if (isset($item['image'])) {
    $is_image = True;
}

if(safeCount($_POST) == 0) {
    $is_selected = '';
    $is_displayed = 'CHECKED';
    $is_wol_selected = '';
    $is_wol_displayed = 'CHECKED';
    // get current values
    if($item['default'] == true)
        $is_selected = 'CHECKED';
    if($item['hidden'] == true)
        $is_displayed = '';
    if($item['default_WOL'] == true)
        $is_wol_selected = 'CHECKED';
    if($item['hidden_WOL'] == true)
        $is_wol_displayed = '';

    $ro = False;
    if ($is_image) {
        $default_name = $item['image']['default_name'];
    } else {
        $default_name = $item['boot_service']['default_name'];
        if (!isset($item['is_local'])) {
            $ro = True;
        }
    }

    $p = new PageGenerator(sprintf(_T("Edit : %s", "imaging"), $label));
    $sidemenu->forceActiveItem("bootmenu");
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm();
    $f->push(new Table());
    $f->add(new HiddenTpl("location"),                      array("value" => $location,                      "hide" => True));

    $input = new TrFormElement(_T('Default menu item label', 'imaging'),        new InputTpl("default_name"));
    $f->add($input,                                         array("value" => $default_name, "disabled" => ($ro?'disabled':'')));

    $f->add(
        new TrFormElement(_T("Selected by default", "imaging"),
        new CheckboxTpl("default")),
        array("value" => $is_selected)
    );
    $f->add(
        new TrFormElement(_T("Displayed", "imaging"),
        new CheckboxTpl("displayed")),
        array("value" => $is_displayed)
    );
    $f->add(
        new TrFormElement(_T("Selected by default on WOL", "imaging"),
        new CheckboxTpl("default_WOL")),
        array("value" => $is_wol_selected)
    );
    $f->add(
        new TrFormElement(_T("Displayed on WOL", "imaging"),
        new CheckboxTpl("displayed_WOL")),
        array("value" => $is_wol_displayed)
    );
    $f->pop();
    $profiles = xmlrpc_get_profile_in_menu($item_uuid);
    $f->push(new Table());
    $f->push(new TitleElement(_T("Associate profiles to image", "imaging"), 2));

    foreach($profiles as $profile){

        $f->add(
            new TrFormElement(sprintf(_T("Profile <b>%s</b>", "imaging"), $profile['name']),
            new CheckboxTpl("profile_".$profile["id"])),
            array("value" => ($profile["in_menu"] == 1) ? "checked" : "")
        );
    }

    $f->pop();

    $f->push(new Table());
    $f->push(new TitleElement(_T("Associate PostInstalls to image", "imaging"), 2));

    $postinstalls = get_all_postinstall_for_menu($item_uuid);

    foreach($postinstalls as $script){
        $f->add(
            new TrFormElement(sprintf(_T("Post Install Script <b>%s</b>", "imaging"), $script['name']),
            new CheckboxTpl("postinstall_".$script["id"])),
            array("value" => ($script["in_menu"] == 1) ? "checked" : "")
        );
    }
    $f->addButton("bvalid", _T("Validate"));
    $f->pop();
    $f->display();
} else {
    $is_image = True;
    if ($item['boot_service']) {
        $bs_uuid = $item['boot_service']['imaging_uuid'];
        $is_image = False;
    } else {
        $im_uuid = $item['image']['imaging_uuid'];
    }

    $params['default'] = ($_POST['default'] == 'on'?True:False);
    $params['default_WOL'] = ($_POST['default_WOL'] == 'on'?True:False);
    $params['hidden'] = ($_POST['displayed'] == 'on'?False:True);
    $params['hidden_WOL'] = ($_POST['displayed_WOL'] == 'on'?False:True);
    $params['default_name'] = $_POST['default_name'];

    $profiles = [];
    $postinstalls = [];
    foreach($_POST as $key =>$value){
        if(str_starts_with($key, 'profile_')){
            $id = substr($key, 8);
            if($value == 'on')
                $profiles[] = $id;
        }
        if(str_starts_with($key, 'postinstall_')){
            $id = substr($key, 12);
            if($value == 'on')
                $postinstalls[] = $id;
        }
    }

    if ($is_image) {
        $ret = xmlrpc_editImageToLocation($item['imaging_uuid'], $location, $params);
        $status = xmlrpc_update_profiles_in_menu($item_uuid, $profiles);
        $status2 = xmlrpc_update_postinstalls_in_menu($item_uuid, $postinstalls);
    } else {
        $ret = xmlrpc_editServiceToLocation($item['imaging_uuid'], $location, $params);
    }

    header("Location: " . urlStrRedirect("imaging/manage/bootmenu"));
    exit;
}


?>
