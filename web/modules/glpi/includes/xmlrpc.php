<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: glpi/includes/xmlrpc.php
 */

 function xmlrpc_get_machines_list($start, $end, $ctx){
     return xmlCall("glpi.get_machines_list", [$start, $end, $ctx]);
 }

 function xmlrpc_get_machines_list1($start, $end, $ctx){
     return xmlCall("glpi.get_machines_list1", [$start, $end, $ctx]);
 }

function xmlrpc_get_devices_list($start, $end, $ctx){
    // [HMDM]
    return xmlCall("glpi.get_devices_list", [$start, $end, $ctx]);
}

// $array_list_user_for_entity = explode(",", entitiesListseach['data']['userIds'][$i]);
//     if (in_array($loginglpi['id'], $array_list_user_for_entity))
function glpiExists($uuid) {
    return xmlCall("glpi.inventoryExists", array($uuid));
}

function getLastMachineGlpiFull($uuid) {
    return xmlCall("glpi.getLastMachineInventoryFull", array($uuid));
}

function getdbreadonly() {
    return xmlCall("glpi.getdbreadonly", array());
}

function getGlpiEM($part) {
    return xmlCall("glpi.getInventoryEM", array($part));
}

function getLastMachineGlpiPart($uuid, $part, $start, $end, $filter, $options) {
    return xmlCall("glpi.getLastMachineInventoryPart", array($uuid, $part, $start, $end, $filter, $options));
}

function  getMachineInfoImaging($uuid) {
    return xmlCall("glpi.getMachineInfoImaging", array($uuid));
}

function countLastMachineGlpiPart($uuid, $part, $filter, $options) {
    return xmlCall("glpi.countLastMachineInventoryPart", array($uuid, $part, $filter, $options));
}

function getGlpiMachineUri() {
    if (!isset($_SESSION["glpi.getGlpiMachineUri"])) {
        $_SESSION["glpi.getGlpiMachineUri"] = xmlCall("glpi.getGlpiMachineUri");
    }
    return $_SESSION["glpi.getGlpiMachineUri"];
}

function getMachineNumberByState() {
    return xmlCall("glpi.getMachineNumberByState");
}

function getMachineListByState($groupName) {
    return xmlCall("glpi.getMachineListByState", array($groupName));
}

function setGlpiEditableValue($uuid, $name, $value) {
    return xmlCall("glpi.setGlpiEditableValue", array($uuid, $name, $value));
}

function getAntivirusStatus() {
    return xmlCall("glpi.getAntivirusStatus");
}

function getMachineListByAntivirusState($groupName) {
    return xmlCall("glpi.getMachineListByAntivirusState", array($groupName));
}

function getMachineByOsLike($osname,$count = 1){
    return xmlCall("glpi.getMachineByOsLike", array($osname,$count));
}

function getLocationsForUser($username){
    return xmlCall("glpi.getLocationsForUser", array($username));
}


function getLocationsForUsersName($username){
    return xmlCall("glpi.getLocationsForUsersName", array($username));
}

function setLocationsForUser($username, $attr){
    return xmlCall("glpi.setLocationsForUser", array($username, $attr));
}

function getAllUserProfiles(){
    return xmlCall("glpi.getAllUserProfiles", array());
}

function addGlpiUser($username, $password, $entity_rights){
    return xmlCall("glpi.addUser", array($username, $password, $entity_rights));
}

function setGlpiUserPassword($username, $password){
    return xmlCall("glpi.setUserPassword", array($username, $password));
}

function getAllEntitiesPowered($params){
    return xmlCall("glpi.getAllEntitiesPowered", array($params));
}

function addEntity($entity_name, $parent_id, $comment){
    return xmlCall("glpi.addEntity", array($entity_name, $parent_id, $comment));
}

function editEntity($id, $entity_name, $parent_id, $comment){
    return xmlCall("glpi.editEntity", array($id, $entity_name, $parent_id, $comment));
}

function getAllEntityRules($params){
    return xmlCall("glpi.getAllEntityRules", array($params));
}

function getAllLocationsPowered($params){
    return xmlCall("glpi.getAllLocationsPowered", array($params));
}

function addLocation($location_name, $parent_id, $comment){
    return xmlCall("glpi.addLocation", array($location_name, $parent_id, $comment));
}

function editLocation($id, $location_name, $parent_id, $comment){
    return xmlCall("glpi.editLocation", array($id, $location_name, $parent_id, $comment));
}

function getEntityRule($params){
    return xmlCall("glpi.getEntityRule", array($params));
}

function addEntityRule($params){
    return xmlCall("glpi.addEntityRule", array($params));
}

function editEntityRule($id, $rule_data){
    return xmlCall("glpi.editEntityRule", array($id, $rule_data));
}

function deleteEntityRule($id){
    return xmlCall("glpi.deleteEntityRule", array($id));
}

function moveEntityRuleUp($id){
    return xmlCall("glpi.moveEntityRuleUp", array($id));
}

function moveEntityRuleDown($id){
    return xmlCall("glpi.moveEntityRuleDown", array($id));
}

function getReport($uuid,$lang){
    return xmlCall("glpi.getReport", array($uuid,$lang));
}
function xmlrpc_setfromglpilogxmpp(   $text,
                                            $type = "infouser",
                                            $sessionname = '' ,
                                            $priority = 0,
                                            $who = '',
                                            $how = '',
                                            $why = '',
                                            $action = '',
                                            $touser =  '',
                                            $fromuser = "",
                                            $module = 'glpi'){
    return xmlCall("xmppmaster.setlogxmpp", array(  $text,
                                                    $type ,
                                                    $sessionname,
                                                    $priority,
                                                    $who,
                                                    $how,
                                                    $why,
                                                    $module,
                                                    $action,
                                                    $touser,
                                                    $fromuser));
}

function xmlrpc_get_all_uuids_and_hostnames(){
  return xmlCall("glpi.get_all_uuids_and_hostnames", array());
}

function xmlrpc_get_os_for_dashboard(){
  return xmlCall("glpi.get_os_for_dashboard", []);
}

function xmlrpc_get_machines_with_os_and_version($os, $version){
  return xmlCall("glpi.get_machines_with_os_and_version", [$os, $version]);
}

function getMachinesMac($uuid){
  return xmlCall("glpi.getMachinesMac", [$uuid]);
}

function glpi_version(){
  return xmlCall("glpi.glpi_version", []);
}

function xmlrpc_check_saas(){
    return xmlCall("glpi.check_saas", []);
}

function  xmlrpc_get_machine_for_hostname($str_list_hostname, $filter="", $start=0, $end=0){
  return xmlCall("glpi.get_machine_for_hostname", [$str_list_hostname, $filter, $start, $end]);
}
function  xmlrpc_get_machine_for_id($str_list_uuid, $filter, $start, $end){
  return xmlCall("glpi.get_machine_for_id", [$str_list_uuid, $filter, $start, $end]);
}
?>
