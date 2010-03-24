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

function getTargetImage($type, $gid, $uuid) {
    if ($type == 'group') {
        $all = xmlrpc_getProfileImages($gid);
    } else {
        $all = xmlrpc_getComputerImages($uuid);
    }
    return $all;
}
if (($type == '' && xmlrpc_isComputerRegistered($target_uuid)) || ($type == 'group' && xmlrpc_isProfileRegistered($target_uuid)))  {


    if(isset($_GET['mod']))
        $mod = $_GET['mod'];
    else
        $mod = "none";

    switch($mod) {
        case 'edit':
            $all = getTargetImage($type, $_GET['gid'], $_GET['uuid']);
            $images = $all['images'];
            $masters = $all['masters'];
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
                image_list($type, "Available images");
            }
            image_list($type, "Available masters", false);
            break;
    }
} else {
    /* register the target (computer or profile) */
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
            $f->addButton("bconvert_image", _T("Validate and convert to image", "imaging"));
        } else {
            $f->addButton("bconvert_master", _T("Validate and convert to master", "imaging"));
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
            if (count($post_installs) == 0) {
                $params['name'] = $_POST['image_label'];
                $params['desc'] = $_POST['image_description'];
                new NotifyWidgetFailure(_T("You must have a post install script to convert an image into a master.", "imaging"));
                header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
            }

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

function image_list($type, $title, $actions=true) {
    $params = getParams();
    if (!$actions) {
        $params['master'] = True;
    }

    // show title
    if($title) {
        $t = new TitleElement(_T($title, "imaging"));
        $t->display();
    }

    $ajax = new AjaxFilter("modules/imaging/imaging/ajaxImages.php", "container".($actions?'image':'master'), $params, "form".($actions?'image':'master'));
    //$ajax->setRefresh(10000);
    $ajax->display();
    echo '<br/><br/><br/>';
    $ajax->displayDivToUpdate();
}


?>

<!-- inject styles -->
<link rel="stylesheet" href="modules/imaging/graph/css/imaging.css" type="text/css" media="screen" />


