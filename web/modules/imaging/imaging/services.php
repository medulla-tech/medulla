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

if (($type == '' && (xmlrpc_isComputerRegistered($target_uuid) || xmlrpc_isComputerInProfileRegistered($target_uuid))) || ($type == 'group' && xmlrpc_isProfileRegistered($target_uuid)))  {
    if (isset($_GET['mod'])) {
        $mod = $_GET['mod'];
    } else {
        $mod = "none";
    }

    function service_add($type, $target_uuid) {
        $params = getParams();
        $item_uuid = $_GET['itemid'];
        $label = urldecode($_GET['itemlabel']);

        $ret = xmlrpc_addServiceToTarget($item_uuid, $target_uuid, $type);

        // goto images list
        if ($ret[0]) {
            $str = sprintf(_T("Service <strong>%s</strong> added to boot menu", "imaging"), $label);
            new NotifyWidgetSuccess($str);
            header("Location: ".urlStrRedirect("base/computers/imgtabs/".$type."tabservices", $params));
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    }

    function service_list($type, $target_uuid, $target_name) {
        $params = getParams();
        $params['target_uuid'] = $target_uuid;
        $params['target_type'] = $type;
        $params['target_name'] = $target_name;

        $ajax = new AjaxFilter("modules/imaging/imaging/ajaxServices.php", "Level2", $params, "Level2");
        //$ajax->setRefresh(10000);
        $ajax->display();
        echo '<br/><br/><br/>';
        $ajax->displayDivToUpdate();
    }

    switch($mod) {
        case 'add':
            service_add($type, $target_uuid);
            break;
        default:
            service_list($type, $target_uuid, $target_name);
            break;
    }
} else {
    # register the target (computer or profile)
    $params = array('target_uuid'=>$target_uuid, 'type'=>$type, 'from'=>"services", "target_name"=>$target_name);
    header("Location: " . urlStrRedirect("base/computers/".$type."register_target", $params));
}

?>
