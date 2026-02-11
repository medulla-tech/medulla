<?php
function xmlrpc_add_hmdm_device($name, $configuration_id, $description="", $groups=null, $imei="", $phone="", $device_id=null){
    return xmlCall("mobile.addHmdmDevice", array($name, $configuration_id, $description, $groups, $imei, $phone, $device_id));
}
function xmlrpc_update_hmdm_device($device_data){
    return xmlCall("mobile.updateHmdmDevice", array($device_data));
}
function xmlrpc_get_hmdm_devices(){
    return xmlCall("mobile.getHmdmDevices", array());
}
function xmlrpc_get_hmdm_applications(){
    return xmlCall("mobile.getHmdmApplications", array());
}
function xmlrpc_get_hmdm_configuration_applications($config_id){
    return xmlCall("mobile.getHmdmConfigurationApplications", array($config_id));
}
function xmlrpc_get_hmdm_icons(){
    return xmlCall("mobile.getHmdmIcons", array());
}
function xmlrpc_add_hmdm_icon($icon_data){
    return xmlCall("mobile.addHmdmIcon", array($icon_data));
}
function xmlrpc_delete_hmdm_icons_by_id($id){
    return xmlCall("mobile.deleteHmdmIconsById", array($id));
}
function xmlrpc_add_hmdm_application($app_data){
    return xmlCall("mobile.addHmdmApplication", array($app_data));
}
function xmlrpc_delete_application_by_id($id){
    return xmlCall("mobile.deleteApplicationById", array($id));
}
function xmlrpc_get_application_versions($app_id){
    return xmlCall("mobile.getApplicationVersions", array($app_id));
}
function xmlrpc_get_configuration_names(){
    return xmlCall("mobile.getConfigurationNames", array());
}
function xmlrpc_update_application_configurations($app_id, $configuration_id, $configuration_name = null){
    return xmlCall("mobile.updateApplicationConfigurations", array($app_id, $configuration_id, $configuration_name));
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
function xmlrpc_update_hmdm_file($file_data){
    return xmlCall("mobile.updateHmdmFile", array($file_data));
}
function xmlrpc_delete_file_by_id($file_data = null, $file_id = null, $filePath = null){
    return xmlCall("mobile.deleteFileById", array($file_data, $file_id, $filePath));
}
function xmlrpc_assign_file_to_configurations($file_id, $configuration_ids){
    return xmlCall("mobile.assignFileToConfigurations", array($file_id, $configuration_ids));
}
function xmlrpc_delete_configuration_by_id($id){
    return xmlCall("mobile.deleteConfigurationById", array($id));
}
function xmlrpc_get_hmdm_configuration_by_id($id){
    return xmlCall("mobile.getHmdmConfigurationById", array($id));
}
function xmlrpc_update_hmdm_configuration($config_data){
    return xmlCall("mobile.updateHmdmConfiguration", array($config_data));
}
function xmlrpc_copy_hmdm_configuration($id, $name, $description){
    return xmlCall("mobile.copyHmdmConfiguration", array($id, $name, $description));
}
function xmlrpc_delete_hmdm_device_by_id($id){
    return xmlCall("mobile.deleteHmdmDeviceById", array($id));
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
function xmlrpc_add_hmdm_group($name, $group_id=null, $customer_id=null, $common=null){
    return xmlCall("mobile.addHmdmGroup", array($name, $group_id, $customer_id, $common));
}
function xmlrpc_delete_hmdm_group_by_id($id){
    return xmlCall("mobile.deleteHmdmGroupById", array($id));
}
function xmlrpc_send_hmdm_message($scope, $device_number="", $group_id="", $configuration_id="", $message=""){
    return xmlCall("mobile.sendHmdmMessage", array($scope, $device_number, $group_id, $configuration_id, $message));
}
function xmlrpc_send_hmdm_push_message($scope, $message_type="", $payload="", $device_number="", $group_id="", $configuration_id=""){
    return xmlCall("mobile.sendHmdmPushMessage", array($scope, $message_type, $payload, $device_number, $group_id, $configuration_id));
}
function xmlrpc_get_hmdm_device_logs($device_number="", $package_filter="", $severity="-1", $page_size=50, $page_num=1){
    return xmlCall("mobile.getHmdmDeviceLogs", array($device_number, $package_filter, $severity, $page_size, $page_num));
}
function xmlrpc_export_hmdm_device_logs($device_number="", $app="", $severity="-1"){ 
    return xmlCall("mobile.exportHmdmDeviceLogs", array($device_number, $app, $severity));
}
function xmlrpc_search_hmdm_app_packages($filter_text=""){
    return xmlCall("mobile.searchHmdmAppPackages", array($filter_text));
}
function xmlrpc_upload_web_ui_files($uploadedFilePath = null, $uploadedFileName = null, $mimeType = null){
    return xmlCall("mobile.uploadWebUiFiles", array($uploadedFilePath, $uploadedFileName, $mimeType));
}
?>
