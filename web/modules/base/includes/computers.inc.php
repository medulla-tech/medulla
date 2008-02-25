<?

function addComputer($params) {
    return xmlCall("base.addComputer", $params);
}

function delComputer($params) {
    return xmlCall("base.delComputer", $params);
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

function getRestrictedComputersList($min = 0, $max = -1, $filt = null) {
    return xmlCall("base.getRestrictedComputersList", array($min, $max, $filt));
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

function canAddComputer() {
    return xmlCall("base.canAddComputer");
}

function canDelComputer() {
    return xmlCall("base.canDelComputer");
}

?>
