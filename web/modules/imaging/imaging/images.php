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
require_once('modules/imaging/includes/post_install_script.php');

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
$itemid = $_GET['itemid'];

if (($type == '' && xmlrpc_isComputerRegistered($target_uuid)) || ($type == 'group' && xmlrpc_isProfileRegistered($target_uuid)))  {


    if(isset($_GET['mod']))
        $mod = $_GET['mod'];
    else
        $mod = "none";

    switch($mod) {
        case 'edit':
            image_edit($target_uuid, $type, $itemid);
            break;
        case 'add':
            image_add($type, $target_uuid);
            break;
        case 'convert':
            image_convert();
            break;
        default:
            if (empty($type)) {
                image_list($type, _T("Available images", "imaging"));
            }
            image_list($type, _T("Available masters", "imaging"), false);
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

function image_edit($target_uuid, $type, $item_uuid) {
    $params = getParams();
    $target_uuid = $_GET['target_uuid'];
    $label = urldecode($_GET['itemlabel']);

    list($succed, $image) = xmlrpc_getTargetImage($target_uuid, $type, $item_uuid);

    function create_form($is_image, $image, $target_uuid, $label, $desc) {
        if ($is_image) {
            printf("<h3>"._T("Edition of image", "imaging")." : <em>%s</em></h3>", $label);
        } else {
            printf("<h3>"._T("Edition of master", "imaging")." : <em>%s</em></h3>", $label);
        }

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
        if (!$is_image) {
            list($a, $post_installs) = xmlrpc_getAllTargetPostInstallScript($target_uuid);
            $f = get_post_install_scripts($f, $image['post_install_scripts'], $post_installs);
        }
        return $f;
    }

    if (count($_POST) == 0) {
        $is_master = $image['is_master'];
        $f = create_form(!$is_master, $image, $target_uuid, $label, $image["desc"]);

        $f->addButton("bvalid", _T("Save", "imaging"));
        if ($image['is_master']) {
            $f->addButton("bconvert_image", _T("Save (converting to image)", "imaging"));
        } else {
            $f->addButton("bconvert_master", _T("Convert to master", "imaging"));
        }
        $f->pop();
        $f->display();
    } else {
        $p_order = array();
        foreach ($_POST as $post_key => $post_value) {
            if (ereg('order_', $post_key)) {
                $post_key = str_replace("order_", "", $post_key);
                $p_order[$post_key] = $post_value;
            }
        }
        $params['name'] = stripslashes($_POST['image_label']);
        $params['desc'] = stripslashes($_POST['image_description']);
        if (isset($_POST['bvalid'])) {
            $params['post_install_scripts'] = $p_order;
            $params['is_master'] = $image['is_master'];
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params, $type);
            // goto images list
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        } elseif (isset($_POST['bconvert_master'])) {
            $f = create_form(False, $image, $target_uuid, $_POST['image_label'], $_POST['image_description']);
            $f->addButton("bvalid_master", _T("Save"));
            $f->display();
        } elseif (isset($_POST['bvalid_master'])) {
            $params['post_install_scripts'] = $p_order;
            $params['is_master'] = True;
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params, $type);
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        } elseif (isset($_POST['bconvert_image'])) {
            $params['is_master'] = False;
            $ret = xmlrpc_editImage($item_uuid, $target_uuid, $params, $type);
            header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
        }
    }
}

function image_list($type, $title, $actions=true) {
    $params = getParams();
    $params['target_uuid'] = $_GET['target_uuid'];
    if (!$actions) {
        $params['master'] = True;
    }

    // show title
    if($title) {
        $t = new TitleElement($title);
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


