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

$menu = array(
    array('Start computer', 'Boot on system hard drive', true, true, true, true),
    array('Create rescue image', 'Backup system hard drive', "", true, "", true),
    array('Create master', 'Backup system hard drive as a master', "", true, "", true)
);

switch($mod) {
    case 'up':
        item_up($type, $menu);
        break;
    case 'down':
        item_down($type, $menu);
        break;
    case 'edit':
        item_edit($type, $menu);
        break;  
    default:
        item_list($type, $menu);
        break;
}

function item_up($type, $menu) {
    $params = getParams();
    header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));    
}

function item_down($type, $menu) {
    $params = getParams();
    header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));    
}

function item_edit($type, $menu) {
    
    $params = getParams();
    $id = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);

    if(count($_POST) == 0) {
    
        printf("<h3>"._T("Edition of item", "imaging")." : <em>%s</em></h3>", $label);
                
        $is_selected = false;
        $is_displayed = false;
        $is_wol_selected = false;
        $is_wol_displayed = false;
        // get current values
        if($menu[$id][2] == true)
            $is_selected = 'CHECKED';
        if($menu[$id][3] == true)
            $is_displayed = 'CHECKED';
        if($menu[$id][4] == true)
            $is_wol_selected = 'CHECKED';
        if($menu[$id][5] == true)
            $is_wol_displayed = 'CHECKED';
        
        $f = new ValidatingForm();
        $f->push(new Table());
        $f->add(
            new TrFormElement(_T("Selected by default", "imaging"), 
            new CheckboxTpl("selected")),
            array("value" => $is_selected)
        );
        $f->add(
            new TrFormElement(_T("Displayed", "imaging"), 
            new CheckboxTpl("displayed")),
            array("value" => $is_displayed)
        );
        $f->add(
            new TrFormElement(_T("Selected by default on WOL", "imaging"), 
            new CheckboxTpl("wol_selected")),
            array("value" => $is_wol_selected)
        );
        $f->add(
            new TrFormElement(_T("Displayed on WOL", "imaging"), 
            new CheckboxTpl("wol_displayed")),
            array("value" => $is_wol_displayed)
        );    
        $f->pop();
        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    }
    else {
        // set new values
        foreach($_POST as $key => $value) {
        
        }
        // goto menu boot list
        header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));
    }    
}

function item_list($type, $menu) {

    $params = getParams();

    // forge params   
    $upAction = new ActionItem(_T("Move Up"), "imgtabs", "up", "item", "base", 
    "computers", $type."tabbootmenu", "up");
    $downAction = new ActionItem(_T("Move down"), "imgtabs", "down", "item", 
    "base", "computers", $type."tabbootmenu", "down");
    $emptyAction = new EmptyActionItem();
    $actionUp = array();
    $actionDown = array();

    $nbItems = count($menu);
    $nbInfos = count($menu[0]);
    
    for($i=0;$i<$nbItems;$i++) {
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $i;
        $list_params[$i]["itemlabel"] = urlencode($menu[$i][0]);
        
        if($i==0) {
            $actionsDown[] = $downAction;
            $actionsUp[] = $emptyAction;
        }
        else if($i==$nbItems-1) {
            $actionsDown[] = $emptyAction;
            $actionsUp[] = $upAction;
        }
        else {
            $actionsDown[] = $downAction;
            $actionsUp[] = $upAction;
        }
        
        for ($j = 0; $j < $nbInfos; $j++) {
            $list[$j][] = $menu[$i][$j];
        }
    }
    $l = new ListInfos($list[0], _T("Label"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($list[1], _T("Description", "imaging"));
    $l->addExtraInfo($list[2], _T("Default", "imaging"));
    $l->addExtraInfo($list[3], _T("Displayed", "imaging"));
    $l->addExtraInfo($list[4], _T("Default on WOL", "imaging"));
    $l->addExtraInfo($list[5], _T("Displayed on WOL", "imaging"));
    $l->addActionItemArray($actionsUp);
    $l->addActionItemArray($actionsDown);
    $l->addActionItem(new ActionItem(_T("Edit"), "imgtabs", "edit", "item", 
    "base", "computers", $type."tabbootmenu", "edit"));
    $l->addActionItem(new ActionPopupItem(_T("Delete"), "bootmenu_remove", 
    "delete", "item", "base", "computers", $type."tabbootmenu", 300, "delete"));
    $l->disableFirstColumnActionLink();
    $l->display();
}



?>
