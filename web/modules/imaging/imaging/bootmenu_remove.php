<?php
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

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
include('modules/imaging/includes/includes.php');
include('modules/imaging/includes/xmlrpc.inc.php');
$params = getParams();
$params['from'] = $_GET['from'];
$item_uuid = $_GET['itemid'];

if ($params['from'] == 'tabimages') {
    $item_uuid = $_GET['mi_itemid'];
    $params['mi_itemid'] = $_GET['mi_itemid'];
} elseif ($params['from'] == 'tabservices') {
    $item_uuid = $_GET['mi_itemid'];
    $params['mi_itemid'] = $_GET['mi_itemid'];
} elseif ($params['from'] == 'tabbootmenu') {

}

$label = urldecode($_GET['itemlabel']);
$item = xmlrpc_getMenuItemByUUID($item_uuid);

$bs_uuid = $item['boot_service']['imaging_uuid'];
$im_uuid = $item['image']['imaging_uuid'];

if (isset($_GET['gid'])) {
    $type = 'group';
    $target_uuid = $_GET['gid'];
} else {
    $type = '';
    $target_uuid = $_GET['uuid'];
}

if (quickGet('valid')) {
    if (isset($bs_uuid)) {
        $ret = xmlrpc_delServiceToTarget($bs_uuid, $target_uuid, $type);
    } else {
        $ret = xmlrpc_delImageToTarget($im_uuid, $target_uuid, $type);
    }
    if ($ret[0] and !isXMLRPCError()) {
        /* insert notification code here if needed */

        // Synchronize boot menu
        if ($type == 'group') {
            $location = getCurrentLocation();
            if ($location == "UUID1")
                $location_name = _T("root", "pulse2");
            else
                $location_name = xmlrpc_getLocationName($location);
            // jfk    
            $objprocess=array();
            $scriptmulticast = 'multicast.sh';
            $path="/tmp/";
            $objprocess['location']=$location;
            $objprocess['process'] = $path.$scriptmulticast;
          
            if (xmlrpc_check_process_multicast($objprocess)){
                $msg = _T("The bootmenus cannot be generated as a multicast deployment is currently running.", "imaging");
                new NotifyWidgetFailure($msg);
                header("Location: " . urlStrRedirect("imaging/manage/index"));
                exit;  
            }
            else{
                $ret = xmlrpc_synchroProfile($target_uuid);
                xmlrpc_clear_script_multicast($objprocess);
            }
        } else {
            $ret = xmlrpc_synchroComputer($target_uuid);
        }
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for computer: %s", "imaging"), implode(', ', $ret[1])));
        }
    } elseif (!$ret[0]) {
        new NotifyWidgetFailure($ret[1]);
    }
    $params['mod'] = 'remove_success';
    $params['tab'] = $type . $params['from'];
    $urlRedirect = ($type == 'group') ? 'imaging/manage/' : 'base/computers/';
    header("Location: " . urlStrRedirect($urlRedirect . $type . "imgtabs", $params));
    exit;
}

// show popup
$params['itemid'] = $item_uuid;
$params['mod'] = 'remove';
$params['bs_uuid'] = $bs_uuid;
?>
<h2><?php echo _T("Remove from boot menu", "imaging") ?></h2>

<form action="<?php echo urlStr("base/computers/bootmenu_remove", $params) ?>" method="post">
    <p><?php printf(_T("Are you sure you want to remove <b>%s</b> from the boot menu ?", "imaging"), $label); ?></p>
    <input name='valid' type="submit" class="btnPrimary" value="<?php echo _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo _T("Cancel", "imaging"); ?>" onClick="closePopup();
            return false;"/>
</form>
