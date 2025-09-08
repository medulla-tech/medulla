<?php
function xmlrpc_tests(){
    return xmlCall("mobile.tests", array());
}
function xmlrpc_nano_devices(){
    return xmlCall("mobile.nano_devices", array());
}

function xmlrpc_to_back($name, $desc, $conf, $grp){
    return xmlCall("mobile.to_back", array($name, $desc));
}
function xmlrpc_getDevice(){
    return xmlCall("mobile.getDevice", array());
}


?>