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
    list($count, $menu) = xmlrpc_getPossibleBootServices($_GET['gid']);
    $target_uuid = $_GET['gid'];
} else {
    $type = '';
    list($count, $menu) = xmlrpc_getPossibleBootServices($_GET['uuid']);
    $target_uuid = $_GET['uuid'];
}


if(isset($_GET['mod']))
    $mod = $_GET['mod'];
else 
    $mod = "none";

switch($mod) {
    case 'add':
        service_add($type, $menu, $target_uuid);
        break;
    default:
        service_list($type, $menu, $count, $target_uuid);
        break;
}

function service_add($type, $menu, $target_uuid) {
    $params = getParams();
    $item_uuid = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);
    
    $ret = xmlrpc_addServiceToTarget($item_uuid, $target_uuid);

    // goto images list 
    if ($ret[0]) {
        $str = sprintf(_T("Service <strong>%s</strong> added to boot menu", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: ".urlStrRedirect("base/computers/imgtabs/".$type."tabservices", $params));
    } else {
        new NotifyWidgetError($ret[1]);
    }
}

function service_list($type, $menu, $count, $target_uuid) {
    $params = getParams();

    $addActions = array();
    
    $addAction = new ActionPopupItem(_T("Add service to boot menu", "imaging"), "addservice", "addbootmenu", "image", "base", "computers", null, 300, "add");
    $emptyAction = new EmptyActionItem();

    // show services list    
    $a_label = array();
    $a_in_boot_menu = array();
    $i = -1;
    foreach ($menu as $entry) {
        $i = $i+1;
        $list_params[$i] = $params;
        $list_params[$i]["itemlabel"] = $entry['value'];
        $list_params[$i]["itemid"] = $entry['imaging_uuid'];
        $list_params[$i]['targetid'] = $targetid;
        // don't show action if service is in bootmenu
        if(!isset($entry['menu_item']))
            $addActions[] = $addAction;
        else
            $addActions[] = $emptyAction;

        $a_label[]= $entry['value'];
        $a_in_boot_menu[]= (isset($entry['menu_item'])? True:False);
        
    }
    $l = new ListInfos($a_label, _T("Label", "imaging"));
    $l->addExtraInfo($a_in_boot_menu, _T("In bootmenu", "imaging"));
    $l->setParamInfo($list_params);
    $l->addActionItemArray($addActions);
    $l->disableFirstColumnActionLink();
    $l->display();
    
}

?>
