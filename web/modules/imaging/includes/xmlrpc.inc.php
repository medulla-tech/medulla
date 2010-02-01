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
  
function xmlrpc_getMachineBootMenu($id) {
    return xmlCall("imaging.getMachineBootMenu", array($id));
}

function xmlrpc_getProfileBootMenu($id) {
    return xmlCall("imaging.getProfileBootMenu", array($id));
}

//Actions
function xmlrpc_moveItemDownInMenu($target_uuid, $type, $item_uuid) {
    return xmlCall("imaging.moveItemDownInMenu", array($target_uuid, $type, $item_uuid));
}

function xmlrpc_moveItemUpInMenu($target_uuid, $type, $item_uuid) {
    return xmlCall("imaging.moveItemUpInMenu", array($target_uuid, $type, $item_uuid));
}

/**/
function xmlrpc_getMachineImages($id) {
    return xmlCall("imaging.getMachineImages", array($id));
}

function xmlrpc_getProfileImages($id) {
    return xmlCall("imaging.getProfileImages", array($id));
}

/* BootServices */
function xmlrpc_getPossibleBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getPossibleBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getMachineBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getMachineBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getProfileBootServices($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getProfileBootServices", array($id, $start, $end, $filter));
}

function xmlrpc_getMenuItemByUUID($id) {
    return xmlCall("imaging.getMenuItemByUUID", array($id));
}

// actions
function xmlrpc_addServiceToTarget($item_uuid, $target_uuid, $params) {
    return xmlCall("imaging.addServiceToTarget", array($item_uuid, $target_uuid, $params));
}

function xmlrpc_delServiceToTarget($item_uuid, $target_uuid) {
    return xmlCall("imaging.delServiceToTarget", array($item_uuid, $target_uuid));
}

function xmlrpc_editServiceToTarget($item_uuid, $target_uuid, $params) {
    return xmlCall("imaging.editServiceToTarget", array($item_uuid, $target_uuid, $params));
}

/* Logs */
function xmlrpc_getMachineLogs($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getMachineLogs", array($id, $start, $end, $filter));
}

function xmlrpc_getProfileLogs($id, $start = 0, $end = -1, $filter = '') {
    return xmlCall("imaging.getProfileLogs", array($id, $start, $end, $filter));
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

?>
