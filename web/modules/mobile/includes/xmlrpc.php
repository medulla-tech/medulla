<?php
// IOS Nano devices commented out for the moment
// function xmlrpc_nano_devices(){
//     return xmlCall("mobile.nano_devices", array());
// }
function xmlrpc_to_back($name, $desc, $conf, $grp){
    return xmlCall("mobile.to_back", array($name, $desc));
}
function xmlrpc_get_hmdm_devices(){
    return xmlCall("mobile.getHmdmDevices", array());
}
function xmlrpc_get_hmdm_applications(){
    return xmlCall("mobile.getHmdmApplications", array());
}
function xmlrpc_delete_application_by_id($id){
    return xmlCall("mobile.deleteApplicationById", array($id));
}
function xmlrpc_get_hmdm_configurations(){
    return xmlCall("mobile.getHmdmConfigurations", array());
}
function xmlrpc_get_hmdm_files(){
    return xmlCall("mobile.getHmdmFiles", array());
}
function xmlrpc_add_hmdm_file($uploadedFilePath = null, $uploadedFileName = null, $externalUrl = null, $fileName = null, $pathOnDevice = null, $description = null, $variableContent = null, $configurationIds = null){
    return xmlCall("mobile.addHmdmFile", array($uploadedFilePath, $uploadedFileName, $externalUrl, $fileName, $pathOnDevice, $description, $variableContent, $configurationIds));
}
function xmlrpc_delete_file_by_id($id = null, $filePath = null){
    return xmlCall("mobile.deleteFileById", array($id, $filePath));
}
function xmlrpc_delete_configuration_by_id($id){
    return xmlCall("mobile.deleteConfigurationById", array($id));
}
function xmlrpc_get_hmdm_configuration_by_id($id){
    return xmlCall("mobile.getHmdmConfigurationById", array($id));
}
function xmlrpc_delete_hmdm_device_by_id($id){
    return xmlCall("mobile.deleteDeviceById", array($id));
}
function xmlrpc_get_hmdm_audit_logs($page_size=50, $page_num=1, $message_filter="", $user_filter=""){
    return xmlCall("mobile.getHmdmAuditLogs", array($page_size, $page_num, $message_filter, $user_filter));
}
function xmlrpc_get_hmdm_detailed_info($device_number){
    return xmlCall("mobile.getHmdmDetailedInfo", array($device_number));
}
function xmlrpc_search_hmdm_devices($filter_text=""){
    return xmlCall("mobile.searchHmdmDevices", array($filter_text));
}
function xmlrpc_get_hmdm_messages($device_number="", $message_filter="", $status_filter="",
                                 $date_from_millis=null, $date_to_millis=null, $page_size=50, $page_num=1){
    return xmlCall("mobile.getHmdmMessages", array($device_number, $message_filter, $status_filter,
                                                  $date_from_millis, $date_to_millis, $page_size, $page_num));
}
function xmlrpc_get_hmdm_push_messages($device_number="", $message_filter="", $status_filter="",
                                      $date_from_millis=null, $date_to_millis=null, $page_size=50, $page_num=1){
    return xmlCall("mobile.getHmdmPushMessages", array($device_number, $message_filter, $status_filter,
                                                      $date_from_millis, $date_to_millis, $page_size, $page_num));
}
function xmlrpc_get_hmdm_groups(){
    return xmlCall("mobile.getHmdmGroups", array());
}
function xmlrpc_send_hmdm_message($scope, $device_number="", $group_id="", $configuration_id="", $message=""){
    return xmlCall("mobile.sendHmdmMessage", array($scope, $device_number, $group_id, $configuration_id, $message));
}
?>
