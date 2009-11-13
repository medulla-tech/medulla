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
    array('Local hard disk', true),
    array('Create image', true),
    array('Create master', true),
    array('Memtest', false),
    array('MBR Fix', false)
);

switch($mod) {
    case 'add':
        service_add($type, $menu);
        break;
    default:
        service_list($type, $menu);
        break;
}

function service_add($type, $menu) {
    $params = getParams();
    $id = $_GET['itemid'];
    $label = urldecode($_GET['itemlabel']);
    
    // goto images list 
    $str = sprintf(_T("Service <strong>%s</strong> added to boot menu", "imaging"), $label);
    new NotifyWidgetSuccess($str);
    header("Location: ".urlStrRedirect("base/computers/imgtabs/".$type."tabservices", $params));
}

function service_list($type, $menu) {
    $params = getParams();

    $addActions = array();
    $addAction = new ActionItem(_T("Add service to boot menu", "imaging"), "imgtabs", 
        "addbootmenu", "image", "base", "computers", $type."tabservices", "add");
    $emptyAction = new EmptyActionItem();

    // show services list    
    $nbItems = count($menu);
    $nbInfos = count($menu[0]);
    for($i=0;$i<$nbItems;$i++) {
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $i;
        $list_params[$i]["itemlabel"] = $menu[$i][0];
        // don't show action if service is in bootmenu
        if(!$menu[$i][1])
            $addActions[] = $addAction;
        else
            $addActions[] = $emptyAction;
        
        // get array for lisinfos
        for ($j = 0; $j < $nbInfos; $j++) {
            $list[$j][] = $menu[$i][$j];
        }
    }
    $l = new ListInfos($list[0], _T("Label", "imaging"));
    $l->addExtraInfo($list[1], _T("In bootmenu", "imaging"));
    $l->setParamInfo($list_params);
    $l->addActionItemArray($addActions);
    $l->disableFirstColumnActionLink();
    $l->display();
    
}

?>
