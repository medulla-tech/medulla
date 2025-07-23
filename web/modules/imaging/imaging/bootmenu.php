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

require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");

$params = getParams();

if (isset($_GET['gid']) && $_GET['gid'] != '') {
    $type = 'group';
    $target_uuid = isset($_GET['gid']) ? $_GET['gid'] : "";
    $target_name = isset($_GET['groupname']) ? $_GET['groupname'] : "";
} else {
    $type = '';
    $target_uuid = isset($_GET['uuid']) ? $_GET['uuid'] : "";
    if (isset($_GET['hostname'])) {
        $target_name = $_GET['hostname'];
    } elseif (isset($_GET['target_name'])) {
        $target_name = $_GET['target_name'];
    } else {
        $target_name = '';
    }
}
if (isset($params['hostname']) && !isset($target_name)) {
    $target_name = $params['hostname'];
}
function item_up() {
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = $_GET['itemlabel'];
    if (isset($_GET['hostname'])) {
        $target_name = $_GET['hostname'];
    } elseif (isset($_GET['target_name'])) {
        $target_name = $_GET['target_name'];
    } else {
        $target_name = '';
    }
    if (isset($_GET['gid'])) {
        $type = 'group';
        $gid = $params['gid'];
        $ret = xmlrpc_moveItemUpInMenu($gid, $type, $item_uuid);
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("Item Menu %s for group up %s", "imaging"), urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
    } else {
        $type = '';
        $uuid = $params['uuid'];
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("Item Menu %s for machine up %s", "imaging"),urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        $ret = xmlrpc_moveItemUpInMenu($uuid, $type, $item_uuid);
    }
    if ($ret) {
        if (isset($_GET['gid'])) {
            if (xmlrpc_isProfileRegistered($_GET['gid'])) {
                // Get Current Location
                $location = xmlrpc_getProfileLocation($_GET['gid']);
                xmlrpc_synchroLocation($location);
            }
        } else {
            $ret = xmlrpc_synchroComputer($params['uuid']);
        }
        $str = sprintf(_T("Success to up item <strong>%s</strong> in the boot menu [ %s ]", "imaging"), urldecode($label), $target_name);
        new NotifyWidgetSuccess($str);
    } else {
        $str = sprintf(_T("Failed to move item <strong>%s</strong> in the boot menu", "imaging"), urldecode($label));
        new NotifyWidgetFailure($str);
    }

    if ($type == '') {
        header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs", $params));
    }
    else {
        header("Location: " . urlStrRedirect("imaging/manage/".$type."imgtabs", $params));
    }
    exit;
}

function item_down() {
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = $_GET['itemlabel'];
    $uuid = $params['uuid'];
    if (isset($_GET['hostname'])) {
        $target_name = $_GET['hostname'];
    } elseif (isset($_GET['target_name'])) {
        $target_name = $_GET['target_name'];
    } else {
        $target_name = '';
    }
    if (isset($_GET['gid'])) {
        $type = 'group';
        $gid = $params['gid'];
        $ret = xmlrpc_moveItemDownInMenu($gid, $type, $item_uuid);
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("Item Menu %s%s", "imaging"),urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
    } else {
        $type = '';
        $uuid = $params['uuid'];
        xmlrpc_setfromxmppmasterlogxmpp(sprintf(_T("Item Menu %s for machine down %s", "imaging"), urldecode($label), $target_name),
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        $ret = xmlrpc_moveItemDownInMenu($uuid, $type, $item_uuid);
    }
    if ($ret) {
        $str = sprintf(_T("Success to move item <strong>%s</strong> in the boot menu [ %s ]", "imaging"), urldecode($label), $target_name);
        new NotifyWidgetSuccess($str);
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        if (isset($_GET['gid'])) {
            if (xmlrpc_isProfileRegistered($_GET['gid'])) {
                // Get Current Location
                $location = xmlrpc_getProfileLocation($_GET['gid']);
                xmlrpc_synchroLocation($location);
            }
        } else {
            $ret = xmlrpc_synchroComputer($params['uuid']);
        }
    } else {
        $str = sprintf(_T("Failed to move item <strong>%s</strong> in the boot menu", "imaging"), urldecode($label));
        xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        new NotifyWidgetFailure($str);
    }

    if ($type == '') {
        header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs", $params));
    }
    else {
        header("Location: " . urlStrRedirect("imaging/manage/".$type."imgtabs", $params));
    }
    exit;
}

function item_edit() {

    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $item = xmlrpc_getMenuItemByUUID($item_uuid);

    if(safeCount($_POST) == 0) {

        $name = (isset($item['boot_service']) ? $item['boot_service']['default_name'] : $item['image']['name']);
        printf("<h3>"._T("Edition of item", "imaging")." : <em>%s</em></h3>", $name);

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

        $f = new ValidatingForm();
        $f->push(new Table());
        $f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
        $f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
        $f->add(new HiddenTpl("gid"),                           array("value" => $_GET['gid'],                   "hide" => True));
        $f->add(new HiddenTpl("uuid"),                          array("value" => $_GET['uuid'],                  "hide" => True));
        $f->add(new HiddenTpl("default_name"),                  array("value" => $name,                          "hide" => True));

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

        if(!empty($_GET['kind']) && $_GET['kind'] == "IM"){

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
        }

        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    } else {
        // set new values
        if(isset($_GET['gid'])) {
            $type = 'group';
            $target_uuid = $_GET['gid'];
        } else {
            $type = '';
            $target_uuid = $_GET['uuid'];
        }

        $bs_uuid = $item['boot_service']['imaging_uuid'];
        $im_uuid = $item['image']['imaging_uuid'];

        $params['default'] = ($_POST['default'] == 'on'?True:False);
        $params['default_WOL'] = ($_POST['default_WOL'] == 'on'?True:False);
        $params['hidden'] = ($_POST['displayed'] == 'on'?False:True);
        $params['hidden_WOL'] = ($_POST['displayed_WOL'] == 'on'?False:True);
        $params['default_name'] = $_POST['default_name'];

        if (isset($_GET['hostname'])) {
            $target_name = $_GET['hostname'];
        } elseif (isset($_GET['target_name'])) {
            $target_name = $_GET['target_name'];
        } else {
            $target_name = '';
        }

        if (isset($bs_uuid) && $bs_uuid != '') {
            $str = sprintf(_T("Edit item <strong>%s</strong> in the boot Menu [ %s ]", "imaging"), urldecode($label), $target_name);
            $ret = xmlrpc_editServiceToTarget($bs_uuid, $target_uuid, $params, $type);
            xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        } else {

            $profiles = [];
            $itemid = htmlentities($_POST['itemid']);
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


            $str = sprintf(_T("Edit item <strong>%s</strong> in the boot Menu [ %s ]", "imaging"), urldecode($label), $target_name);
            $ret = xmlrpc_editImageToTarget($im_uuid, $target_uuid, $params, $type);

            $status = xmlrpc_update_profiles_in_menu($itemid, $profiles);
            $status2 = xmlrpc_update_postinstalls_in_menu($itemid, $postinstalls);
            xmlrpc_setfromxmppmasterlogxmpp($str,
                                    "IMG",
                                    '',
                                    0,
                                    $target_name ,
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'Imaging | Image | Menu | server | Manual');
        }
        if ($ret)
        {
            if (isset($_GET['gid'])) {
                if (xmlrpc_isProfileRegistered($_GET['gid'])) {
                    // Get Current Location
                    $location = xmlrpc_getProfileLocation($_GET['gid']);
                    xmlrpc_synchroLocation($location);
                }
            } else {
                $ret = xmlrpc_synchroComputer($params['uuid']);
            }
        }
        // goto menu boot list
        if ($type == '') {
            header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs", $params));
        }
        else {
            header("Location: " . urlStrRedirect("imaging/manage/".$type."imgtabs", $params));
        }
        exit;
    }
}

function item_list() {
    if(isset($_GET['gid'])) {
        $type = 'group';
        list($count, $menu) = xmlrpc_getProfileBootMenu($_GET['gid']);
    } else {
        $type = '';
        list($count, $menu) = xmlrpc_getComputerBootMenu($_GET['uuid']);
    }

    $params = getParams();

    // forge params

    if ($type == 'group') {
        $module = "imaging";
        $submod = "manage";
    }
    else {
        $module = "base";
        $submod = "computers";
    }
    $upAction = new ActionItem(_T("Move Up"), $type."imgtabs", "up", "item", $module, $submod, $type."tabbootmenu", "up");
    $downAction = new ActionItem(_T("Move down"), $type."imgtabs", "down", "item", $module, $submod, $type."tabbootmenu", "down");
    $editAction = new ActionItem(_T("Edit"), $type."imgtabs", "edit", "item", $module, $submod, $type."tabbootmenu", "edit");
    $deleteAction = new ActionPopupItem(_T("Delete"), $type."bootmenu_remove", "delete", "item", $module, $submod, $type."tabbootmenu", 300, "delete");

    $emptyAction = new EmptyActionItem();
    $actionUp = array();
    $actionDown = array();
    $actionEdit = array();
    $actionDelete = array();

    $nbItems = $count;

    $a_label = array();
    $a_desc = array();
    $a_default = array();
    $a_display = array();
    $a_defaultWOL = array();
    $a_displayWOL = array();
    $params['from'] = 'tabbootmenu';

    $i = -1;
    $root_len = 0;
    foreach ($menu as $entry) {
        $i = $i + 1;
        $is_image = False;
        if (isset($entry['image'])) {
            $is_image = True;
        }

        if ($is_image) { # TODO $entry has now a cache for desc.
            $a_desc[] = $entry['image']['desc'];
            $entry['default_name'] = $entry['image']['name'];
            $kind = 'IM';
            if ($entry['read_only']) {
                $url = '<img src="img/other/imagingscript_ro.svg" style="vertical-align: middle" width="25" height="25" alt="'._T('master from the profile', 'imaging').'"/> ';
            } else {
                $url = '<img src="img/other/imagingscript_rw.svg" style="vertical-align: middle" width="25" height="25" alt="'._T('master', 'imaging').'"/> ';
            }
        } else {
            $a_desc[] = $entry['boot_service']['default_desc'];
            $entry['default_name'] = $entry['boot_service']['default_name'];
            $kind = 'BS';
            if (isset($entry['read_only']) && $entry['read_only' ]) {
                $url = '<img src="modules/imaging/graph/images/service-action-ro.png" style="vertical-align: middle" alt="'._T('boot service from profile', 'imaging').'"/> ';
            } else {
                $url = '<img src="img/other/confitem.svg" style="vertical-align: middle" width="25" height="25" alt="'._T('boot service', 'imaging').'"/> ';
            }
        }

        $params["kind"] = $kind;
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $entry['imaging_uuid'];
        $list_params[$i]["itemlabel"] = urlencode($entry['default_name']);

        if ($entry['read_only']) {
            $actionsDown[] = $emptyAction;
            $actionsUp[] = $emptyAction;
            $root_len += 1;
            $actionEdit[] = $emptyAction;
            $actionDelete[] = $emptyAction;
        } else {
            $actionEdit[] = $editAction;
            $actionDelete[] = $deleteAction;
            if ($i == $root_len) {
                if ($count == 1 || $root_len == $count - 1) {
                    $actionsDown[] = $emptyAction;
                    $actionsUp[] = $emptyAction;
                } else {
                    $actionsDown[] = $downAction;
                    $actionsUp[] = $emptyAction;
                }
            } elseif ($i > $root_len && $i == $nbItems-1) {
                $actionsDown[] = $emptyAction;
                $actionsUp[] = $upAction;
            } elseif ($i > $root_len) {
                $actionsDown[] = $downAction;
                $actionsUp[] = $upAction;
            }
        }

        $a_label[] = sprintf("%s%s", $url, $entry['default_name']); # should be replaced by the label in the good language
        $a_default[] = $entry['default'];
        $a_display[] = ($entry['hidden'] ? False:True);
        $a_defaultWOL[] = $entry['default_WOL'];
        $a_displayWOL[] = ($entry['hidden_WOL'] ? False:True);
    }
    $firstp = "<p>" . _T("Use \"Preselected choice\" or \"Preselected choice on WOL\" to define the default boot entry.", "imaging") . "</p>";
    /* Build tooltip text on column name */
    if ($type == "") {
        $text = $firstp . "<p>" . _T("If the default entry is an image creation or restore, the following network boots will fall back to the first menu entry.", "imaging") . "</p>";
    } else {
        $text = $firstp . "<p>" . _T("When changing \"Preselected choice\" or \"Preselected choice on WOL\" entry, this value will be set on all the computers in this group.", "imaging") . "</p>" . "<p>" . _T("If the default entry is an image creation or restore, the following network boots will fall back to the first menu entry.", "imaging") . "</p>";
    }
    $l = new ListInfos($a_label, _T("Label"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
    $l->addExtraInfo($a_default, _T("Preselected choice", "imaging")
                     , "", $text);
    $l->addExtraInfo($a_display, _T("Displayed", "imaging"));
    $l->addExtraInfo($a_defaultWOL, _T("Preselected choice on WOL", "imaging")
                     , "", $text);
    $l->addExtraInfo($a_displayWOL, _T("Displayed on WOL", "imaging"));
    $l->addActionItemArray($actionsUp);
    $l->addActionItemArray($actionsDown);
    $l->addActionItemArray($actionEdit);
    if ($count > 1) {
        $l->addActionItemArray($actionDelete);
    }
    $l->disableFirstColumnActionLink();
    $l->setTableHeaderPadding(19);
    $l->display();
}

if (($type == '' && (xmlrpc_isComputerRegistered($target_uuid) || xmlrpc_isComputerInProfileRegistered($target_uuid))) || ($type == 'group' && xmlrpc_isProfileRegistered($target_uuid)))  {
    if (isset($_GET['mod'])) {
        $mod = $_GET['mod'];
    } else {
        $mod = "none";
    }

    switch($mod) {
        case 'up':
            item_up();
            break;
        case 'down':
            item_down();
            break;
        case 'edit':
            item_edit();
            break;
        default:
            item_list();
            break;
    }
} else {
    # register the target (computer or profile)
    $params = array('target_uuid'=>$target_uuid, 'type'=>$type, 'from'=>"services", "target_name"=>$target_name);
    if ($type == 'group') {
        header("Location: " . urlStrRedirect("imaging/manage/".$type."register_target", $params));
    }
    else {
        header("Location: " . urlStrRedirect("base/computers/".$type."register_target", $params));
    }
    exit;
}

?>
