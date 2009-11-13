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

if(isset($_GET['gid']))
    $type = 'group';
else
    $type = '';

if(isset($_GET['mod']))
    $mod = $_GET['mod'];
else 
    $mod = "none";

// images
$images = array(
    array('MDV 2008.0', 'Mandriva 2008 Backup', '2009-02-25 17:38', '1GB', true)
);

// masters
$masters = array(
    array('MDV 2008.0', 'Mandriva 2008 Master', '2009-02-25 17:38', '1GB', false)
);

switch($mod) {
    case 'edit':
        image_edit($type, $images);
        break;
    case 'add':
        image_add($type);
        break;
    default:
        if(empty($type))
            image_list($type, "Available images", $images);
        image_list($type, "Available masters", $masters, false);
        break;
}

function image_add($type) {
    
    $params = getParams();
    // add to menu
    $id = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    $result = true;
    if($result == true) {
        // goto images list   
        $str = sprintf(_T("Image <strong>%s</strong> added to boot menu", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
    }
}

function image_edit($type, $menu) {

    $params = getParams();
    $id = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    if(count($_POST) == 0) {
    
        printf("<h3>"._T("Edition of image", "imaging")." : <em>%s</em></h3>", $label);
                
        // get current values
        $desc = $menu[$id][1];
        
        $f = new ValidatingForm();
        $f->push(new Table());
        $f->add(
            new TrFormElement(_T("Label", "imaging"), new InputTpl("image_label")),
            array("value" => $label)
        );
        $f->add(
            new TrFormElement(_T("Description", "imaging"), new InputTpl("image_description")),
            array("value" => $desc)
        );
        $postInstall = new SelectItem("post_install");
        $postInstall->setElements(array("none" => "No post-installation script", "sysprep1" => "Sysprep sur la première partition"));
        $postInstall->setElementsVal(array("none" => "none", "sysprep1" => "sysprep1"));
        // set selected
        // ...
        $f->add(
            new TrFormElement(_T("Post-installation script", "imaging"), $postInstall)
        );
        $f->pop();
        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    }
    else {
        // set new values
        foreach($_POST as $key => $value) {
            // ...
        }
        // goto images list
        header("Location: " . urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params));
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
    $addAction = new ActionItem(_T("Add image to boot menu", "imaging"), "imgtabs", 
        "addbootmenu", "image", "base", "computers", $type."tabimages", "add");
    $emptyAction = new EmptyActionItem();
    
    // forge params
    $nbItems = count($images);
    $nbInfos = count($images[0]);
    for($i=0;$i<$nbItems;$i++) {
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $i;
        $list_params[$i]["itemlabel"] = urlencode($images[$i][0]);
        
        // don't show action if image is in bootmenu
        if(!$images[$i][4])
            $addActions[] = $addAction;
        else
            $addActions[] = $emptyAction;    
        
        for ($j = 0; $j < $nbInfos; $j++) {
            $list[$j][] = $images[$i][$j];
        }
    }
    // show images list
    $l = new ListInfos($list[0], _T("Label"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($list[1], _T("Description", "imaging"));
    $l->addExtraInfo($list[2], _T("Created", "imaging"));
    $l->addExtraInfo($list[3], _T("Size (compressed)", "imaging"));
    $l->addExtraInfo($list[4], _T("In boot menu", "imaging"));    
    $l->addActionItemArray($addActions);
    $l->addActionItem(
        new ActionPopupItem(_T("Create bootable iso", "imaging"), 
        "images_iso", "backup", "image", "base", "computers")
    );
    // if not in boot menu
    if($actions) {
        $l->addActionItem(
            new ActionItem(_T("Edit image", "imaging"), 
            "imgtabs", "edit", "image", "base", "computers", $type."tabimages", "edit")
        );
        $l->addActionItem(
            new ActionPopupItem(_T("Delete", "imaging"), 
            "images_delete", "delete", "image", "base", "computers", $type."tabimages", 300, "delete")
        );
    }
    $l->disableFirstColumnActionLink();
    $l->display();
}


?>
