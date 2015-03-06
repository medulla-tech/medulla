<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
?>
<?php

function getAllMachinesInventoryColumn($part, $column, $pattern = array()) {
    return xmlCall("inventory.getAllMachinesInventoryColumn", array($part, $column, $pattern));
}

function getLastMachineInventoryPart($part, $params) {
    return xmlCall("inventory.getLastMachineInventoryPart", array($part, $params));
}

function getLastMachineInventoryPart2($part, $params) {
    return xmlCall("inventory.getLastMachineInventoryPart2", array($part, $params));
}

function countLastMachineInventoryPart($part, $params) {
    return xmlCall("inventory.countLastMachineInventoryPart", array($part, $params));
}

function getLastMachineInventoryFull($uuid) {
    return xmlCall("inventory.getLastMachineInventoryFull", array($uuid));
}

function getMachines($pattern = null) {
    return xmlCall("inventory.getMachines", array(array('hostname' => $pattern)));
}

function getInventoryParts() {
    return xmlCall("inventory.getInventoryParts");
}

function getInventoryEM($part) {
    return xmlCall("inventory.getInventoryEM", array($part));
}

function getInventoryGraph($part) {
    return xmlCall("inventory.getInventoryGraph", array($part));
}

function inventoryExists($uuid) {
    return xmlCall("inventory.inventoryExists", array($uuid));
}

function getInventoryHistory($days, $only_new, $pattern, $max, $min) {
    return xmlCall("inventory.getInventoryHistory", array($days, $only_new, $pattern, $max, $min));
}

function countInventoryHistory($days, $only_new, $pattern) {
    return xmlCall("inventory.countInventoryHistory", array($days, $only_new, $pattern));
}

function getMachineInventoryHistory($params) {
    return xmlCall("inventory.getMachineInventoryHistory", array($params));
}

function countMachineInventoryHistory($params) {
    return xmlCall("inventory.countMachineInventoryHistory", array($params));
}

function getMachineInventoryDiff($params) {
    return xmlCall("inventory.getMachineInventoryDiff", array($params));
}

/*
 * Return number of machines inventoried
 * by state
 * Default states values:
 *  * green: less than 10 days
 *  * orange: less than 35 days
 *  * red: more than 35 days
 */

function getMachineNumberByState() {
    return xmlCall("inventory.getMachineNumberByState");
}

function getMachineListByState($groupName) {
    return xmlCall("inventory.getMachineListByState", array($groupName));
}

function getMachineByOwner($user) {
    return xmlCall("inventory.getMachineByOwner", array($user));
}

function getReport($uuid,$lang){
    return xmlCall("inventory.getReport", array($uuid,$lang));
}

function getLocationAll($params) {
    return xmlCall("inventory.getLocationAll",array($params));
}

function updateEntities($id,$name) {
    return xmlCall("inventory.updateEntities",array($id,$name));
}

function createLocation($name, $parent_name){
    return xmlCall("inventory.createLocation",array($name, $parent_name));
}

function deleteEntities($id, $Label, $parentId){
    return xmlCall("inventory.deleteEntities",array($id, $Label, $parentId));
}

function parse_file_rule($params){
    return xmlCall("inventory.parse_file_rule",array($params));
}

// function rewritte_file_rule(){
//     return xmlCall("inventory.rewritte_file_rule",array());
// }

function moveEntityRuleDown($idrule){
    return xmlCall("inventory.moveEntityRuleDown",array($idrule));
}

function moveEntityRuleUp($idrule){
    return xmlCall("inventory.moveEntityRuleUp",array($idrule));
}

function  operatorType(){
    return xmlCall("inventory.operatorType",array());
}

function  operatorTag($MappedObject){
    return xmlCall("inventory.operatorTag",array($MappedObject));
}

function  operatorTagAll(){
    return xmlCall("inventory.operatorTagAll",array());
}

function addEntityRule($ruleobj){
    return xmlCall("inventory.addEntityRule",array($ruleobj));
}

function deleteEntityRule($idrule){
    return xmlCall("inventory.deleteEntityRule",array($idrule));
}
?>
