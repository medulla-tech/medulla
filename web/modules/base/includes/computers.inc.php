<?php

function addComputer($params) {
    return xmlCall("base.addComputer", $params);
}

function checkComputerName($name) {
    return xmlCall("base.checkComputerName", array($name));
}

function isComputerNameAvailable($locationUUID, $name) {
    return xmlCall("base.isComputerNameAvailable", array($locationUUID, $name));
}

function delComputer($params, $backup) {
    return xmlCall("base.delComputer", array($params, $backup));
}

function neededParamsAddComputer() {
    return xmlCall("base.neededParamsAddComputer");
}

function getComputer($filter = '') {
    return xmlCall("base.getComputer", array($filter));
}

function getComputersList($filter = '') {
    return xmlCall("base.getComputersList", array($filter));
}

function getRestrictedComputersListLen($filt = null) {
    return xmlCall("base.getRestrictedComputersListLen", array($filt));
}


function getRestrictedComputersList($min = 0, $max = -1, $filt = null, $adv = True , $justId=False) {
    return xmlCall("base.getRestrictedComputersList", array($min, $max, $filt, $adv, $justId));
}

function getRestrictedComputersListuuid($min = 0, $max = -1, $filt = null, $adv = True , $justId=False) {
    return xmlCall("base.getRestrictedComputersList", array($min, $max, $filt, $adv, $justId));
}

function getComputerCount($filter = null) {
    return xmlCall("base.getComputerCount", array($filter));
}

function getSimpleComputerCount() {
    return xmlCall("base.simple_computer_count", array());
}

function getComputersName($filter = '') {
    return xmlCall("base.getComputersName", array($filter));
}

/*
 * Get Operating system name for a given uuid or uuids' list
 * @param $uuids: One UUID or a list of UUIDS
 * @type $uuids: str or list
 *
 * @return: array of (uuid => UUIDXX, OSName => 'OS Name')
 * @rtype: array
 */
function getComputersOS($uuids) {
    return xmlCall("base.getComputersOS", array($uuids));
}

function getComputersCountByOS($osname) {
    return xmlCall("base.getComputersCountByOS", array($osname));
}

function getRestrictedComputersName($min = 0, $max = -1, $filt = null) {
    return xmlCall("base.getRestrictedComputersName", array($min, $max, $filt));
}

function getComputersListHeaders() {
    if (!isset($_SESSION["getComputersListHeaders"])) {
        $_SESSION["getComputersListHeaders"] = xmlCall("base.getComputersListHeaders");
    }
    return $_SESSION["getComputersListHeaders"];
}

function canAddComputer() {
    return xmlCall("base.canAddComputer");
}

function canDelComputer() {
    if (!isset($_SESSION["canDelComputer"])) {
        $_SESSION["canDelComputer"] = xmlCall("base.canDelComputer", null);
    }
    return $_SESSION["canDelComputer"];
}

function canAssociateComputer2Location() {
    if (!isset($_SESSION["canAssociateComputer2Location"])) {
        $_SESSION["canAssociateComputer2Location"] = xmlCall("base.canAssociateComputer2Location");
    }
    return $_SESSION["canAssociateComputer2Location"];
}

function hasComputerManagerWorking() {
    if (!isset($_SESSION["hasComputerManagerWorking"])) {
        $_SESSION["hasComputerManagerWorking"] = xmlCall("base.hasComputerManagerWorking");
    }
    return $_SESSION["hasComputerManagerWorking"];
}

?>
