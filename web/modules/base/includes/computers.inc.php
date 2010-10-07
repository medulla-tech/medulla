<?

function addComputer($params) {
    return xmlCall("base.addComputer", $params);
}

function checkComputerName($name) {
    return xmlCall("base.checkComputerName", array($name));
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

function getRestrictedComputersList($min = 0, $max = -1, $filt = null, $adv = True) {
    return xmlCall("base.getRestrictedComputersList", array($min, $max, $filt, $adv));
}

function getComputerCount($filter = null) {
    return xmlCall("base.getComputerCount", array($filter));
}

function getComputersName($filter = '') {
    return xmlCall("base.getComputersName", array($filter));
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
    if (!isset($_SESSION["canAddComputer"])) {
        $_SESSION["canAddComputer"] = xmlCall("base.canAddComputer", null);
    }
    return $_SESSION["canAddComputer"];
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
