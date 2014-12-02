<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

function glpiExists($uuid) {
    return xmlCall("glpi.inventoryExists", array($uuid));
}

function getLastMachineGlpiFull($uuid) {
    return xmlCall("glpi.getLastMachineInventoryFull", array($uuid));
}

function getGlpiEM($part) {
    return xmlCall("glpi.getInventoryEM", array($part));
}

function getLastMachineGlpiPart($uuid, $part, $start, $end, $filter, $options) {
    return xmlCall("glpi.getLastMachineInventoryPart", array($uuid, $part, $start, $end, $filter, $options));
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

function getAllEntities($params){
    return xmlCall("glpi.getAllEntities", array($params));
}

function addEntity($entity_name, $parent_id, $comment){
    return xmlCall("glpi.addEntity", array($entity_name, $parent_id, $comment));
}

function getAllEntityRules($params){
    return xmlCall("glpi.getAllEntityRules", array($params));
}

function getAllLocations($params){
    return xmlCall("glpi.getAllLocations", array($params));
}

function addLocation($location_name, $parent_id, $comment){
    return xmlCall("glpi.addLocation", array($location_name, $parent_id, $comment));
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

function getReport($uuid,$lang){
    return xmlCall("glpi.getReport", array($uuid,$lang));
}

?>
