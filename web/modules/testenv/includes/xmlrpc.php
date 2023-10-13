<?php
function xmlrpc_tests(){
    // Return the element of the testenv.tests table.
    return xmlCall("testenv.tests", []);
}

function getLastBuildOutput($name){
    return xmlCall("testenv.getLastBuildOutput",[$name]);
}

function xmlrpc_getAllVMList(){
    return xmlCall("testenv.getAllVMList",[]);
}

function xmlrpc_getVMInfo($vm_name){
    return xmlCall("testenv.getVMInfo",[$vm_name]);
}

function xmlrpc_editNameVM($vm_name, $new_name){
    return xmlCall("testenv.editNameVM",[$vm_name, $new_name]);
}

function xmlrpc_create_vm($name, $desc, $ram, $cpu, $disk_size, $os){
    return xmlCall("testenv.create_vm",[$name, $desc, $ram, $cpu, $disk_size, $os]);
}

function xmlrpc_delete_vm($name){
    return xmlCall("testenv.delete_vm",[$name]);
}

function xmlrpc_start_vm($url){
    return xmlCall("testenv.start_vm",[$url]);
}

function xmlrpc_forceshutdown_vm($url){
    return xmlCall("testenv.forceshutdown_vm",[$url]);
}

function xmlrpc_shutdown_vm($url){
    return xmlCall("testenv.shutdown_vm",[$url]);
}

function xmlrpc_createConnectionGuac($name){
    return xmlCall("testenv.createConnectionGuac",[$name]);
}

function xmlrpc_urlGuac($name){
    return xmlCall("testenv.urlGuac",[$name]);
}

function xmlrpc_deleteGuac($name){
    return xmlCall("testenv.deleteGuac",[$name]);
}

function xmlrpc_editGuacName($name, $new_name){
    return xmlCall("testenv.editGuacName",[$name, $new_name]);
}

function xmlrpc_getVMs(){
    return xmlCall("testenv.getVMs",[]);
}

function xmlrpc_getVMByName($name){
    return xmlCall("testenv.getVMByName",[$name]);
}

function xmlrpc_checkExistVM($name){
    return xmlCall("testenv.checkExistVM",[$name]);
}

function xmlrpc_dictGuac($name){
    return xmlCall("testenv.dictGuac",[$name]);
}

function xmlrpc_updateVMResources($name, $ram, $cpu){
    return xmlCall("testenv.updateVMResources",[$name, $ram, $cpu]);
}
?>
