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

if(isset($_GET['gid'])) {
    $type = 'group';
    list($count, $menu) = xmlrpc_getProfileBootMenu($_GET['gid']);
} else {
    $type = '';
    list($count, $menu) = xmlrpc_getMachineBootMenu($_GET['uuid']);
}

if(isset($_GET['mod']))
    $mod = $_GET['mod'];
else 
    $mod = "none";

switch($mod) {
    case 'up':
        item_up($type, $menu);
        break;
    case 'down':
        item_down($type, $menu);
        break;
    case 'edit':
        item_edit();
        break;  
    default:
        item_list($type, $menu, $count);
        break;
}

function item_up($type, $menu) {
    $params = getParams();
    header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));    
}

function item_down() {
    $params = getParams();
    header("Location: " . urlStrRedirect("base/computers/imgtabs", $params));    
}

function item_edit() {
    
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);
    
    $item = xmlrpc_getMenuItemByUUID($item_uuid);

    if(count($_POST) == 0) {
    
        printf("<h3>"._T("Edition of item", "imaging")." : <em>%s</em></h3>", $item['desc']);
                
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
                        
        $input = new TrFormElement(_T('Default menu item label', 'imaging'),        new InputTpl("default_name"));
        $f->add($input,                                         array("value" => $item['default_name']));
                
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
        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    } else {
        // set new values
        foreach($_POST as $key => $value) {
        
        }
        if(isset($_GET['gid'])) {
            $type = 'group';
            $target_uuid = $_GET['gid'];
        } else {
            $type = '';
            $target_uuid = $_GET['uuid'];
        }
                        
        $bs_uuid = $item['boot_service']['imaging_uuid'];
        
        $params['default'] = ($_POST['default'] == 'on'?True:False);
        $params['default_WOL'] = ($_POST['default_WOL'] == 'on'?True:False);
        $params['hidden'] = ($_POST['displayed'] == 'on'?False:True);
        $params['hidden_WOL'] = ($_POST['displayed_WOL'] == 'on'?False:True);
        $params['default_name'] = $_POST['default_name'];

        $ret = xmlrpc_editServiceToTarget($bs_uuid, $target_uuid, $params);
        
        // goto menu boot list
        header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs", $params));
    }    
}

function item_list($type, $menu, $count) {

    $params = getParams();

    // forge params   
    $upAction = new ActionItem(_T("Move Up"), "imgtabs", "up", "item", "base", 
    "computers", $type."tabbootmenu", "up");
    $downAction = new ActionItem(_T("Move down"), "imgtabs", "down", "item", 
    "base", "computers", $type."tabbootmenu", "down");
    $emptyAction = new EmptyActionItem();
    $actionUp = array();
    $actionDown = array();

    $nbItems = $count;
    
    $a_label = array();
    $a_desc = array();
    $a_default = array();
    $a_display = array();
    $a_defaultWOL = array();
    $a_displayWOL = array();
    
//    for($i=0;$i<$nbItems;$i++) {
    $i = -1;
    foreach ($menu as $entry) {
        $i = $i + 1;
//        $entry = $menu[$i];
        $is_image = False;
        if (isset($entry['image'])) {
            $is_image = True;
        }
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $entry['imaging_uuid'];
        $list_params[$i]["itemlabel"] = urlencode($entry['default_name']);
        
        if($i==0) {
            $actionsDown[] = $downAction;
            $actionsUp[] = $emptyAction;
        } else if($i==$nbItems-1) {
            $actionsDown[] = $emptyAction;
            $actionsUp[] = $upAction;
        } else {
            $actionsDown[] = $downAction;
            $actionsUp[] = $upAction;
        }

        $a_label[] = $entry['default_name']; # should be replaced by the label in the good language
        if ($is_image) { # TODO $entry has now a cache for desc.
            $a_desc[] = $entry['image']['desc'];
        } else {
            $a_desc[] = $entry['boot_service']['desc'];
        }
        $a_default[] = $entry['default'];
        $a_display[] = ($entry['hidden'] ? False:True);
        $a_defaultWOL[] = $entry['default_WOL'];
        $a_displayWOL[] = ($entry['hidden_WOL'] ? False:True);
        
    }
    $l = new ListInfos($a_label, _T("Label"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
    $l->addExtraInfo($a_default, _T("Default", "imaging"));
    $l->addExtraInfo($a_display, _T("Displayed", "imaging"));
    $l->addExtraInfo($a_defaultWOL, _T("Default on WOL", "imaging"));
    $l->addExtraInfo($a_displayWOL, _T("Displayed on WOL", "imaging"));
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
