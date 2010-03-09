<?

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

require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

if (isset($_GET['gid']) && $_GET['gid'] != '') {
    $type = 'group';
    $target_uuid = $_GET['gid'];
    $target_name = $_GET['groupname'];
} else {
    $type = '';
    $target_uuid = $_GET['uuid'];
    $target_name = $_GET['hostname'];
}

if (($type == '' && xmlrpc_isComputerRegistered($target_uuid)) || ($type == 'group' && xmlrpc_isProfileRegistered($target_uuid)))  {

    if ($type == 'group') {
        $all = xmlrpc_getProfileImages($_GET['gid']);
    } else {
        $all = xmlrpc_getComputerImages($_GET['uuid']);
    }

    $images = $all['images'];
    $masters = $all['masters'];

    if(isset($_GET['mod']))
        $mod = $_GET['mod'];
    else
        $mod = "none";

    switch($mod) {
        case 'edit':
            image_edit($type, $images, $masters);
            break;
        case 'add':
            image_add($type, $target_uuid);
            break;
        case 'convert':
            image_convert();
            break;
        default:
            if (empty($type)) {
                image_list($type, "Available images", $images);
            }
            image_list($type, "Available masters", $masters, false);
            break;
    }
} else {
    # register the target (computer or profile)
    $params = array('target_uuid'=>$target_uuid, 'type'=>$type, 'from'=>"services", "target_name"=>$target_name);
    header("Location: " . urlStrRedirect("base/computers/".$type."register_target", $params));
}


function image_add($type, $target_uuid) {

    $params = getParams();
    // add to menu
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $ret = xmlrpc_addImageToTarget($item_uuid, $target_uuid);

    if($ret[0]) {
        // goto images list
        $str = sprintf(_T("Image <strong>%s</strong> added to boot menu", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
    } else {
        new NotifyWidgetFailure($ret[1]);
    }
}

function image_edit($type, $images, $masters) {

    $params = getParams();
    $id = $_GET['itemid'];
    $target_uuid = $_GET['target_uuid'];
    $label = urldecode($_GET['itemlabel']);
    $all = array_merge($images[1], $masters[1]);
    foreach ($all as $m) {
        if ($m['imaging_uuid'] == $id) {
            $image = $m;
            continue;
        }
    }


    if (count($_POST) == 0) {
        printf("<h3>"._T("Edition of image", "imaging")." : <em>%s</em></h3>", $label);

        // get current values
        $desc = $image["desc"];

        $f = new ValidatingForm();
        $f->add(new HiddenTpl('target_uuid'),                   array("value" => $target_uuid,                   "hide" => True));
        $f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
        $f->add(new HiddenTpl('target_uuid'),                   array("value" => $target_uuid,                   "hide" => True));
        $f->push(new Table());
        $f->add(
            new TrFormElement(_T("Label", "imaging"), new InputTpl("image_label")),
            array("value" => $label)
        );
        $f->add(
            new TrFormElement(_T("Description", "imaging"), new InputTpl("image_description")),
            array("value" => $desc)
        );

        $f->pop();
        $f->addButton("bvalid", _T("Validate"));
        if ($image['is_master']) {
            $f->addButton("bconvert_image", _T("Validate and convert to image"));
        } else {
            $f->addButton("bconvert_master", _T("Validate and convert to master"));
        }
        $f->pop();
        $f->display();
    } else {
        if (isset($_POST['bvalid'])) {
            $item_uuid = $id;
            $params['name'] = $_POST['image_label'];
            $params['desc'] = $_POST['image_description'];
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params, $type);
            // goto images list
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        } elseif (isset($_POST['bconvert_master'])) {
            $f = new ValidatingForm();
            $f->push(new Table());

            $f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
            $f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
            $f->add(new HiddenTpl('target_uuid'),                   array("value" => $target_uuid,                   "hide" => True));
            $f->add(new HiddenTpl('image_label'),                   array("value" => $_POST['image_label'],          "hide" => True));
            $f->add(new HiddenTpl('image_description'),             array("value" => $_POST['image_description'],    "hide" => True));

            $post_installs = xmlrpc_getAllTargetPostInstallScript($target_uuid);
            $post_installs = $post_installs[1];

            $elements = array();
            $elementsVal = array();
            foreach ($post_installs as $ps) {
                $elements[$ps['imaging_uuid']] = $ps['default_name'].' / '.$ps['default_desc'];
                $elementsVal[$ps['imaging_uuid']] = $ps['imaging_uuid'];
            }

            $postInstall = new SelectItem("post_install");
            $postInstall->setElements($elements);
            $postInstall->setElementsVal($elementsVal);
            $f->add(
                new TrFormElement(_T("Post-installation script", "imaging"), $postInstall)
            );
            $f->pop();
            $f->addButton("bvalid_master", _T("Validate"));
            $f->display();

        } elseif (isset($_POST['bvalid_master'])) {
            $item_uuid = $id;
            $params['name'] = $_POST['image_label'];
            $params['desc'] = $_POST['image_description'];
            $params['post_install_script'] = $_POST['post_install'];
            $params['is_master'] = True;
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params, $type);
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        } elseif (isset($_POST['bconvert_image'])) {
            $item_uuid = $id;
            $params['name'] = $_POST['image_label'];
            $params['desc'] = $_POST['image_description'];
            $params['is_master'] = False;
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params);
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        }
    }
}

function image_list($type, $title, $images, $actions=true) {

    $params = getParams();


    // show title
    if($title) {
        $t = new TitleElement(_T($title, "imaging"));
        $t->display();
    }

    $addActions = array();
    $addAction = new ActionPopupItem(_T("Add image to boot menu", "imaging"), "addimage", "addbootmenu", "image", "base", "computers", null, 300, "add");
    $delAction = new ActionPopupItem(_T("Remove from boot menu", "imaging"), "bootmenu_remove", "delbootmenu", "item", "base", "computers", $type."tabbootmenu", 300, "delete");
    $emptyAction = new EmptyActionItem();
    $destroyAction = new ActionPopupItem(_T("Delete the image", "imaging"), "images_delete", "delete", "image", "base", "computers", $type."tabimages", 300, "delete");
    $showImAction = new ActionPopupItem(_T("Show target using that image", "imaging"), "showtarget", "showtarget", "image", "base", "computers");

    $editActions = array();
    $editAction = new ActionItem(_T("Edit image", "imaging"), "imgtabs", "edit", "image", "base", "computers", $type."tabimages", "edit");

    // forge params
    list($count, $images) = $images;

    $i = -1;

    $params['from'] = 'tabimages';
    $a_desc = array();
    $a_desc = array();
    $a_date = array();
    $a_size = array();
    $a_inbootmenu = array();
    $a_destroy = array();
    $l_im = array();
    foreach ($images as $image) {
        $i += 1;

        $name = $image['name'];
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $image['imaging_uuid'];
        $list_params[$i]["itemlabel"] = urlencode($name);
        $list_params[$i]["target_uuid"] = $_GET['target_uuid'];

        // don't show action if image is in bootmenu
        if(!isset($image['menu_item'])) {
            $addActions[] = $addAction;
        } else {
            $addActions[] = $delAction;
            $list_params[$i]['mi_itemid'] = $image['menu_item']['imaging_uuid'];
        }

        if ($_GET['target_uuid'] == $image['mastered_on_target_uuid']) {
            $editActions[] = $editAction;
        } else {
            $editActions[] = $emptyAction;
        }

        # TODO no label in image!
        $a_label[] = $name;
        $a_desc[] = $image['desc'];
        $a_date[] = _toDate($image['creation_date']);
        $a_size[] = humanReadable($image['size']);
        $a_inbootmenu[] = (isset($image['menu_item'])?True:False);
        $l_im[] = array($image['imaging_uuid'], $_GET['target_uuid'], $type);
    }

    if (!$actions) {
        $ret = xmlrpc_areImagesUsed($l_im);
        foreach ($images as $image) {
            if ($ret[$image['imaging_uuid']]) {
                $a_destroy[] = $showImAction;
            } else {
                $a_destroy[] = $destroyAction;
            }
        }
    }

    // show images list
    $l = new ListInfos($a_label, _T("Label"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
    $l->addExtraInfo($a_date, _T("Created", "imaging"));
    $l->addExtraInfo($a_size, _T("Size (compressed)", "imaging"));
    $l->addExtraInfo($a_inbootmenu, _T("In boot menu", "imaging"));
    $l->addActionItemArray($addActions);
/* TODO!    $l->addActionItem(
        new ActionPopupItem(_T("Create bootable iso", "imaging"),
        "images_iso", "backup", "image", "base", "computers")
    );*/
    // if not in boot menu
    if ($actions) {
        $l->addActionItem(
            new ActionItem(_T("Edit image", "imaging"),
            "imgtabs", "edit", "image", "base", "computers", $type."tabimages", "edit")
        );
        $l->addActionItem($destroyAction);
    } else {
        $l->addActionItemArray($editActions);
        $l->addActionItemArray($a_destroy);
    }
    $l->disableFirstColumnActionLink();
    $l->display();
}


?>

<!-- inject styles -->
<link rel="stylesheet" href="modules/imaging/graph/css/imaging.css" type="text/css" media="screen" />


