<?php
/**
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

function xmlrpc_isProfileRegistered($profile_uuid) {
    # we call as long as it's not registered, but once it is,
    # we can store that information in the session.
    if (!isset($_SESSION["imaging.isProfileRegistered_".$profile_uuid])) {
        $ret = xmlCall("imaging.isProfileRegistered", array($profile_uuid));
        if ($ret) {
            $_SESSION["imaging.isProfileRegistered_".$profile_uuid] = $ret;
        }
        return $ret;
    }
    return ($_SESSION["imaging.isProfileRegistered_".$profile_uuid] == 1);
}

function xmlrpc_getMyMenuProfile($target_uuid) {
    return xmlCall("imaging.getMyMenuProfile", array($target_uuid));
}
function xmlrpc_setMyMenuProfile($target_uuid, $params) {
    return xmlCall("imaging.setMyMenuProfile", array($target_uuid, $params));
}

function xmlrpc_isComputerRegistered($machine_uuid) {
    if (isset($_SESSION["imaging.isComputerInProfileRegistered_".$machine_uuid])) {
        # we check because if we pass to computer_in_profile, there is chances we are no more in computer
        unset($_SESSION["imaging.isComputerRegistered_".$machine_uuid]);
    }
    # we call as long as it's not registered, but once it is,
    # we can store that information in the session.
    if (!isset($_SESSION["imaging.isComputerRegistered_".$machine_uuid])) {
        $ret = xmlCall("imaging.isComputerRegistered", array($machine_uuid));
        if ($ret) {
            $_SESSION["imaging.isComputerRegistered_".$machine_uuid] = $ret;
        }
        return $ret;
    }
    return ($_SESSION["imaging.isComputerRegistered_".$machine_uuid] == 1);
}

function xmlrpc_isComputerInProfileRegistered($machine_uuid) {
    if (isset($_SESSION["imaging.isComputerRegistered_".$machine_uuid])) {
        # we check because if we pass to computer, there is chances that we are no more in computer_in_profile!
        unset($_SESSION["imaging.isComputerInProfileRegistered_".$machine_uuid]);
    }

    if (!isset($_SESSION["imaging.isComputerInProfileRegistered_".$machine_uuid])) {
        $ret = xmlCall("imaging.isComputerInProfileRegistered", array($machine_uuid));
        if ($ret) {
            $_SESSION["imaging.isComputerInProfileRegistered_".$machine_uuid] = $ret;
        }
        return $ret;
    }
    return ($_SESSION["imaging.isComputerInProfileRegistered_".$machine_uuid] == 1);
}

function xmlrpc_canIRegisterThisComputer($target_uuid) {
    return xmlCall("imaging.canIRegisterThisComputer", array($target_uuid));
}

function xmlrpc_checkComputerForImaging($computer_uuid) {
    return xmlCall("imaging.checkComputerForImaging", $computer_uuid);
}

function xmlrpc_checkProfileForImaging($computer_uuid) {
    return xmlCall("imaging.checkProfileForImaging", $computer_uuid);
}

function xmlrpc_delComputersImaging($computers_UUID, $backup) {
    return xmlCall("imaging.delComputersImaging", array($computers_UUID, $backup));
}

function xmlrpc_getMyMenuComputer($target_uuid) {
    return xmlCall("imaging.getMyMenuComputer", array($target_uuid));
}
function xmlrpc_setMyMenuComputer($target_uuid, $params) {
    return xmlCall("imaging.setMyMenuComputer", array($target_uuid, $params));
}

function xmlrpc_getComputerBootMenu($id) {
    return xmlCall("imaging.getComputerBootMenu", array($id));
}

function xmlrpc_getProfileBootMenu($id) {
    return xmlCall("imaging.getProfileBootMenu", array($id));
}

function xmlrpc_getLocationBootMenu($id) {
    return xmlCall("imaging.getLocationBootMenu", array($id));
}


function xmlrpc_resetSynchroState($tid, $type) {
    return xmlCall("imaging.resetSynchroState", array($tid, $type));
}

function xmlrpc_getComputerSynchroState($id) {
    return xmlCall("imaging.getComputerSynchroState", array($id));
}
function xmlrpc_getProfileSynchroState($id) {
    return xmlCall("imaging.getProfileSynchroState", array($id));
}
function xmlrpc_getLocationSynchroState($id) {
    return xmlCall("imaging.getLocationSynchroState", array($id));
}

function xmlrpc_synchroComputer($id) {
    return xmlCall("imaging.synchroComputer", array($id));
}
function xmlrpc_synchroProfile($id) {
    return xmlCall("imaging.synchroProfile", array($id));
}
function xmlrpc_synchroLocation($id) {
    return xmlCall("imaging.synchroLocation", array($id));
}

//Actions
function xmlrpc_moveItemDownInMenu($target_uuid, $type, $item_uuid) {
    return xmlCall("imaging.moveItemDownInMenu", array($target_uuid, $type, $item_uuid));
}

function xmlrpc_moveItemUpInMenu($target_uuid, $type, $item_uuid) {
    return xmlCall("imaging.moveItemUpInMenu", array($target_uuid, $type, $item_uuid));
}

function xmlrpc_moveItemDownInMenu4Location($loc_id, $item_uuid) {
    return xmlCall("imaging.moveItemDownInMenu4Location", array($loc_id, $item_uuid));
}

function xmlrpc_moveItemUpInMenu4Location($loc_id, $item_uuid) {
    return xmlCall("imaging.moveItemUpInMenu4Location", array($loc_id, $item_uuid));
}

/* Images */
function xmlrpc_imagingServerISOCreate($image_uuid, $size, $title) {
    return xmlCall("imaging.imagingServerISOCreate", array($image_uuid, $size, $title));
}

function xmlrpc_getTargetImage($id, $type, $itemid) {
    return xmlCall("imaging.getTargetImage", array($id, $type, $itemid));
}

function xmlrpc_getComputerImages($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getComputerImages", array($id, $start, $end, $filter));
}

function xmlrpc_getProfileImages($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getProfileImages", array($id, $start, $end, $filter));
}

function xmlrpc_getLocationImages($location_id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getLocationImages", array($location_id, $start, $end, $filter));
}

function xmlrpc_getLocationMastersByUUID($location_id, $masters_uuid) {
    return xmlCall("imaging.getLocationMastersByUUID", array($location_id, $masters_uuid));
}

function xmlrpc_areImagesUsed($images) {
    return xmlCall("imaging.areImagesUsed", array($images));
}

function xmlrpc_imagingServerImageDelete($image_uuid) {
    return xmlCall("imaging.imagingServerImageDelete", array($image_uuid));
}
//Actions
function xmlrpc_addImageToTarget($item_uuid, $target_uuid, $params, $type_target) {
    return xmlCall("imaging.addImageToTarget", array($item_uuid, $target_uuid, $params, $type_target));
}

function xmlrpc_editImageToTarget($item_uuid, $target_uuid, $params, $type_target) {
    return xmlCall("imaging.editImageToTarget", array($item_uuid, $target_uuid, $params, $type_target));
}

function xmlrpc_delImageToTarget($item_uuid, $target_uuid, $type_target) {
    return xmlCall("imaging.delImageToTarget", array($item_uuid, $target_uuid, $type_target));
}

function xmlrpc_addImageToLocation($item_uuid, $loc_id, $params) {
    return xmlCall("imaging.addImageToLocation", array($item_uuid, $loc_id, $params));
}

function xmlrpc_editImageToLocation($item_uuid, $loc_id, $params) {
    return xmlCall("imaging.editImageToLocation", array($item_uuid, $loc_id, $params));
}

function xmlrpc_delImageToLocation($item_uuid, $loc_id) {
    return xmlCall("imaging.delImageToLocation", array($item_uuid, $loc_id));
}

function xmlrpc_editImage($item_uuid, $target_uuid, $params, $type_target) {
    return xmlCall("imaging.editImage", array($item_uuid, $target_uuid, $params, $type_target));
}

function xmlrpc_editImageLocation($item_uuid, $loc_uuid, $params) {
    return xmlCall("imaging.editImageLocation", array($item_uuid, $loc_uuid, $params));
}

/* BootServices */
function xmlrpc_getPossibleBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getPossibleBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getLocationBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getLocationBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getComputerBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getComputerBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getProfileBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getProfileBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getMenuItemByUUID($id) {
    return xmlCall("imaging.getMenuItemByUUID", array($id));
}

// actions
function xmlrpc_addServiceToTarget($item_uuid, $target_uuid, $params, $type) {
    return xmlCall("imaging.addServiceToTarget", array($item_uuid, $target_uuid, $params, $type));
}

function xmlrpc_delServiceToTarget($item_uuid, $target_uuid, $type) {
    return xmlCall("imaging.delServiceToTarget", array($item_uuid, $target_uuid, $type));
}

function xmlrpc_editServiceToTarget($item_uuid, $target_uuid, $params, $type) {
    return xmlCall("imaging.editServiceToTarget", array($item_uuid, $target_uuid, $params, $type));
}

function xmlrpc_addServiceToLocation($item_uuid, $location_id, $params) {
    return xmlCall("imaging.addServiceToLocation", array($item_uuid, $location_id, $params));
}

function xmlrpc_delServiceToLocation($item_uuid, $location_id) {
    return xmlCall("imaging.delServiceToLocation", array($item_uuid, $location_id));
}

function xmlrpc_editServiceToLocation($item_uuid, $location_id, $params) {
    return xmlCall("imaging.editServiceToLocation", array($item_uuid, $location_id, $params));
}



/* Logs */
function xmlrpc_getComputerLogs($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getComputerLogs", array($id, $start, $end, $filter));
}

function xmlrpc_getProfileLogs($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getProfileLogs", array($id, $start, $end, $filter));
}

function xmlrpc_imageGetLogs($itemid) {
    return xmlCall("imaging.imageGetLogs", $itemid);
}

// server informations

function xmlrpc_getGlobalStatus($location) {
    return xmlCall("imaging.getGlobalStatus", array($location));
}

function xmlrpc_getDiskInfo($location) {
    return xmlCall("imaging.getDiskInfo", array($location)); //TODO?
}

function xmlrpc_getHealth($location) {
    return xmlCall("imaging.getHealth", array($location)); //TODO?
}

function xmlrpc_getShortStatus($location) {
    return xmlCall("imaging.getShortStatus", array($location)); //TODO?
}

function xmlrpc_getLogs4Location($location, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getLogs4Location", array($location, $start, $end, $filter));
}

/* entity and imaging server */
function xmlrpc_getAllNonLinkedImagingServer($start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getAllNonLinkedImagingServer", array($start, $end, $filter));
}

function xmlrpc_linkImagingServerToLocation($is_uuid, $loc_id, $loc_name) {
    return xmlCall("imaging.linkImagingServerToLocation", array($is_uuid, $loc_id, $loc_name));
}

function xmlrpc_doesLocationHasImagingServer($location) {
    # we call as long as it's not registered, but once it is,
    # we can store that information in the session.
    if (!isset($_SESSION["imaging.doesLocationHasImagingServer_".$location])) {
        $ret = xmlCall("imaging.doesLocationHasImagingServer", array($location));
        if ($ret) {
            $_SESSION["imaging.doesLocationHasImagingServer_".$location] = $ret;
        }
        return $ret;
    }
    return ($_SESSION["imaging.doesLocationHasImagingServer_".$location] == 1);
}

function xmlrpc_getImagingServerConfig($location) {
    return xmlCall("imaging.getImagingServerConfig", array($location));
}

function xmlrpc_setImagingServerConfig($location, $config) {
    return xmlCall("imaging.setImagingServerConfig", array($location, $config));
}

/* postinstall scripts */
function xmlrpc_getAllTargetPostInstallScript($target_uuid, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getAllTargetPostInstallScript", array($target_uuid, $start, $end, $filter));
}

function xmlrpc_getAllPostInstallScripts($location, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getAllPostInstallScripts", array($location, $start, $end, $filter));
}

function xmlrpc_getPostInstallScript($script_id, $loc_id) {
    return xmlCall("imaging.getPostInstallScript", array($script_id, $loc_id));
}

function xmlrpc_delPostInstallScript($script_id) {
    return xmlCall("imaging.delPostInstallScript", array($script_id));
}

function xmlrpc_editPostInstallScript($script_id, $params) {
    return xmlCall("imaging.editPostInstallScript", array($script_id, $params));
}

function xmlrpc_addPostInstallScript($location, $params) {
    return xmlCall("imaging.addPostInstallScript", array($location, $params));
}

function xmlrpc_getAllKnownLanguages() {
    return xmlCall("imaging.get_all_known_languages");
}

function xmlrpc_getPartitionsToBackupRestore($target_uuid) {
    return xmlCall("imaging.getPartitionsToBackupRestore", array($target_uuid));
}

/* computers */
function xmlrpc_getComputerByMac($mac) {
    return xmlCall("imaging.getComputerByMac", array($mac));
}

function xmlrpc_getComputerByUUID($uuid) {
    return xmlCall("imaging.getComputerByUUID", array($uuid));
}

?>
