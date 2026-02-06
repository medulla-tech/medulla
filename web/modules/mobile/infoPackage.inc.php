<?php
require_once("modules/medulla_server/version.php");

$mod = new Module("mobile");
$mod->setVersion("1.0");
$mod->setDescription(_T("Mobiles", "mobile"));
$mod->setAPIVersion("1:0:0");
$mod->setPriority(10);
$submod = new SubModule("mobile");
$submod->setDescription(_T("Mobiles", "mobile"));
$submod->setVisibility(true);
$submod->setImg('img/mobiles/mobile_down');
$submod->setDefaultPage("mobile/mobile/index");
$submod->setPriority(10);
$mod->addSubmod($submod);


################################
# main mobile page
################################

$page = new Page("index", _T('Get all available phones', 'mobile'));
$page->setFile("modules/mobile/mobile/index.php");
$submod->addPage($page);


################################
# add device page
################################

$pageAddDevice = new Page("addDevice", _T('Add a device', 'mobile'));
$pageAddDevice->setFile("modules/mobile/mobile/addDevice.php");
$submod->addPage($pageAddDevice);

################################
# manage applications page
################################

$pageAddAppliations = new Page("applications", _T('Applications', 'mobile'));
$pageAddAppliations->setFile("modules/mobile/mobile/applicationsList.php");
$submod->addPage($pageAddAppliations);

################################
# application versions page
################################
$pageApplicationVersions = new Page("applicationVersions", _T('Application Versions', 'mobile'));
$pageApplicationVersions->setFile("modules/mobile/mobile/applicationVersions.php");
$pageApplicationVersions->setOptions(array("visible" => false));
$submod->addPage($pageApplicationVersions);

################################
# modify file page
################################
$pageModifyFile = new Page("modifyFile", _T('Modify File', 'mobile'));
$pageModifyFile->setFile("modules/mobile/mobile/modifyFile.php");
$pageModifyFile->setOptions(array("visible" => false));
$submod->addPage($pageModifyFile);

################################
# edit device page
################################
$pageEditDevice = new Page("editDevice", _T('Edit Device', 'mobile'));
$pageEditDevice->setFile("modules/mobile/mobile/editDevice.php");
$pageEditDevice->setOptions(array("visible" => false));
$submod->addPage($pageEditDevice);

################################
# delete device page
################################
$pageDeleteDevice = new Page("deleteDevice", _T('Delete Device', 'mobile'));
$pageDeleteDevice->setFile("modules/mobile/mobile/deleteDevice.php");
$pageDeleteDevice->setOptions(array("visible" => false));
$submod->addPage($pageDeleteDevice);

################################
# assign configurations to file page
################################
$pageFileConfigurations = new Page("fileConfigurations", _T('File Configurations', 'mobile'));
$pageFileConfigurations->setFile("modules/mobile/mobile/fileConfigurations.php");
$pageFileConfigurations->setOptions(array("visible" => false));
$submod->addPage($pageFileConfigurations);

################################
# application configuration page
################################
$pageApplicationConfiguration = new Page("applicationConfiguration", _T('Application Configuration', 'mobile'));
$pageApplicationConfiguration->setFile("modules/mobile/mobile/applicationConfiguration.php");
$pageApplicationConfiguration->setOptions(array("visible" => false));
$submod->addPage($pageApplicationConfiguration);

################################
# add application page
################################

$pageAddApplication = new Page("addApplication", _T('Add an application', 'mobile'));
$pageAddApplication->setFile("modules/mobile/mobile/addApplication.php");
$submod->addPage($pageAddApplication);

###############################
# edit application page
###############################
$pageEditApplication = new Page("editApplication", _T('Edit an application', 'mobile'));
$pageEditApplication->setFile("modules/mobile/mobile/editApplication.php");
$pageEditApplication->setOptions(array("visible" => false));
$submod->addPage($pageEditApplication);

###############################
# create icon page (ajax)
################################
// $pageAjaxCreateIcon = new Page("createIcon", _T('Create an icon', 'mobile'));
// $pageAjaxCreateIcon->setFile("modules/mobile/mobile/ajaxCreateIcon.php");
// $pageAjaxCreateIcon->setOptions(array("AJAX" => true, "visible" => false));
// $submod->addPage($pageAjaxCreateIcon);

################################
# get icons page (ajax)
################################
// $pageAjaxGetIcons = new Page("getIcons", _T('Get icons', 'mobile'));
// $pageAjaxGetIcons->setFile("modules/mobile/mobile/ajaxGetIcons.php");
// $pageAjaxGetIcons->setOptions(array("AJAX" => true, "visible" => false));
// $submod->addPage($pageAjaxGetIcons);

################################
# delete icon page (ajax)
################################
// $pageAjaxDeleteIcon = new Page("deleteIcon", _T('Delete icon', 'mobile'));
// $pageAjaxDeleteIcon->setFile("modules/mobile/mobile/ajaxDeleteIcon.php");
// $pageAjaxDeleteIcon->setOptions(array("AJAX" => true, "visible" => false));
// $submod->addPage($pageAjaxDeleteIcon);

################################
# icon settings page
################################
// $pageIconSettings = new Page("iconSettings", _T('Icon settings', 'mobile'));
// $pageIconSettings->setFile("modules/mobile/mobile/iconSettings.php");
// $submod->addPage($pageIconSettings);

###############################
#upload apk page (ajax)
###############################
$pageAjaxUploadApk = new Page("ajaxUploadApk", _T('Upload APK', 'mobile'));
$pageAjaxUploadApk->setFile("modules/mobile/mobile/ajaxUploadApk.php");
$pageAjaxUploadApk->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxUploadApk);

################################
# GLPI devices page
################################
// $pageGlpiDevices = new Page("glpiDevices", _T('All devices glpi', 'mobile'));
// $pageGlpiDevices->setFile("modules/mobile/mobile/glpiDevicesList.php");
// $submod->addPage($pageGlpiDevices);

################################
# Files page
################################
$pageFiles = new Page("files", _T('Files', 'mobile'));
$pageFiles->setFile("modules/mobile/mobile/filesList.php");
$submod->addPage($pageFiles);

$pageAddFile = new Page("addFile", _T('Add a file', 'mobile'));
$pageAddFile->setFile("modules/mobile/mobile/addFile.php");
$submod->addPage($pageAddFile);

################################
# ListMobile - ajax
################################
$pageajaxDeviceList = new Page("ajaxDeviceList", _T('Device list view', 'mobile'));
$pageajaxDeviceList->setFile("modules/mobile/mobile/ajaxDeviceList.php");
$pageajaxDeviceList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageajaxDeviceList);

$pageajaxDeviceList = new Page("ajaxAddDevice", _T('Add device', 'mobile'));
$pageajaxDeviceList->setFile("modules/mobile/mobile/ajaxAddDevice.php");
$pageajaxDeviceList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageajaxDeviceList);

################################
# Applications - ajax
################################

$pageAjaxApplicationsList = new Page("ajaxApplicationsList", _T('Applications list view', 'mobile'));
$pageAjaxApplicationsList->setFile("modules/mobile/mobile/ajaxApplicationsList.php");
$pageAjaxApplicationsList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxApplicationsList);

$pageAjaxGlpiDevices = new Page("ajaxGlpiDevicesList", _T('GLPI devices list view', 'mobile'));
$pageAjaxGlpiDevices->setFile("modules/mobile/mobile/ajaxGlpiDevicesList.php");
$pageAjaxGlpiDevices->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxGlpiDevices);

$pageAjaxGlpiPhones = new Page("ajaxGlpiPhonesList", _T('GLPI phones list view', 'mobile'));
$pageAjaxGlpiPhones->setFile("modules/mobile/mobile/ajaxGlpiPhonesList.php");
$pageAjaxGlpiPhones->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxGlpiPhones);

$pageAjaxFilesList = new Page("ajaxFilesList", _T('Files list view', 'mobile'));
$pageAjaxFilesList->setFile("modules/mobile/mobile/ajaxFilesList.php");
$pageAjaxFilesList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxFilesList);

$pageAjaxDeviceSearch = new Page("ajaxDeviceSearch", _T('Device search', 'mobile'));
$pageAjaxDeviceSearch->setFile("modules/mobile/mobile/ajaxDeviceSearch.php");
$pageAjaxDeviceSearch->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxDeviceSearch);


################################
# Applications - delete handler
################################

$pageDeleteApplication = new Page("deleteApplication", _T('Delete application', 'mobile'));
$pageDeleteApplication->setFile("modules/mobile/mobile/deleteApplication.php");
$pageDeleteApplication->setOptions(array("AJAX" => false, "visible" => false));

$submod->addPage($pageDeleteApplication);

$pageDeleteGlpiDevice = new Page("deleteGlpiDevice", _T('Delete GLPI Device', 'mobile'));
$pageDeleteGlpiDevice->setFile("modules/mobile/mobile/deleteGlpiDevice.php");
$pageDeleteGlpiDevice->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteGlpiDevice);

$pageDeleteFile = new Page("deleteFile", _T('Delete file', 'mobile'));
$pageDeleteFile->setFile("modules/mobile/mobile/deleteFile.php");
$pageDeleteFile->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteFile);

################################
# Configurations pages
################################

$pageConfigurations = new Page("configurations", _T('Configurations', 'mobile'));
$pageConfigurations->setFile("modules/mobile/mobile/configurationsList.php");
$submod->addPage($pageConfigurations);

$pageConfigurationDetails = new Page("configurationDetails", _T('Configuration details', 'mobile'));
$pageConfigurationDetails->setFile("modules/mobile/mobile/configurationDetails.php");
$submod->addPage($pageConfigurationDetails);

$pageAjaxConfigurationsList = new Page("ajaxConfigurationsList", _T('Configurations list view', 'mobile'));
$pageAjaxConfigurationsList->setFile("modules/mobile/mobile/ajaxConfigurationsList.php");
$pageAjaxConfigurationsList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxConfigurationsList);

$pageDeleteConfiguration = new Page("deleteConfiguration", _T('Delete configuration', 'mobile'));
$pageDeleteConfiguration->setFile("modules/mobile/mobile/deleteConfiguration.php");
$pageDeleteConfiguration->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteConfiguration);

################################
# Groups pages
################################

$pageGroups = new Page("groups", _T('All groups', 'mobile'));
$pageGroups->setFile("modules/mobile/mobile/groups.php");
$submod->addPage($pageGroups);

$pageAddGroup = new Page("addGroup", _T('Add a group', 'mobile'));
$pageAddGroup->setFile("modules/mobile/mobile/addGroup.php");
$submod->addPage($pageAddGroup);

$pageEditGroup = new Page("editGroup", _T('Edit group', 'mobile'));
$pageEditGroup->setFile("modules/mobile/mobile/editGroup.php");
$pageEditGroup->setOptions(array("visible" => false));
$submod->addPage($pageEditGroup);

$pageAjaxGroupList = new Page("ajaxGroupList", _T('Groups list view', 'mobile'));
$pageAjaxGroupList->setFile("modules/mobile/mobile/ajaxGroupList.php");
$pageAjaxGroupList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxGroupList);

$pageDeleteGroup = new Page("deleteGroup", _T('Delete group', 'mobile'));
$pageDeleteGroup->setFile("modules/mobile/mobile/deleteGroup.php");
$pageDeleteGroup->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteGroup);

################################
# Group Quick Actions page
################################
$pageGroupQuickAction = new Page("groupQuickAction", _T('Group Quick Action', 'mobile'));
$pageGroupQuickAction->setFile("modules/mobile/mobile/groupQuickAction.php");
$pageGroupQuickAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageGroupQuickAction);

$pageGroupQuickActionExec = new Page("groupQuickActionExec", _T('Group Quick Action Exec', 'mobile'));
$pageGroupQuickActionExec->setFile("modules/mobile/mobile/groupQuickActionExec.php");
$pageGroupQuickActionExec->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageGroupQuickActionExec);

################################
# Functions page (HMDM features)
################################

$pageFunctions = new Page("functions", _T('Functions', 'mobile'));
$pageFunctions->setFile("modules/mobile/mobile/functions.php");
$submod->addPage($pageFunctions);

# messages
$pageNewMessage = new Page("newMessage", _T('Send new message', 'mobile'));
$pageNewMessage->setFile("modules/mobile/mobile/newMessage.php");
$submod->addPage($pageNewMessage);

#quick actions (push message)
$pageNewPushMessage = new Page("newPushMessage", _T('Send new push message', 'mobile'));
$pageNewPushMessage->setFile("modules/mobile/mobile/newPushMessage.php");
$submod->addPage($pageNewPushMessage);

#app package autocomplete
$pageAjaxAppSearch = new Page("ajaxAppSearch", _T('App package search', 'mobile'));
$pageAjaxAppSearch->setFile("modules/mobile/mobile/ajaxAppSearch.php");
$pageAjaxAppSearch->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxAppSearch);

#export logs page
$pageExportLogs = new Page("exportLogs", _T('Export logs', 'mobile'));
$pageExportLogs->setFile("modules/mobile/mobile/exportLogs.php");
$pageExportLogs->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageExportLogs);

################################
# QR Code page
################################
$pageQrCode = new Page("qrCode", _T('QR Code', 'mobile'));
$pageQrCode->setFile("modules/mobile/mobile/qrCode.php");
$pageQrCode->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageQrCode);

################################
# Device Quick Actions page
################################
$pageDeviceQuickAction = new Page("deviceQuickAction", _T('Device Quick Action', 'mobile'));
$pageDeviceQuickAction->setFile("modules/mobile/mobile/deviceQuickAction.php");
$pageDeviceQuickAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageDeviceQuickAction);

$pageDeviceQuickActionExec = new Page("deviceQuickActionExec", _T('Device Quick Action Exec', 'mobile'));
$pageDeviceQuickActionExec->setFile("modules/mobile/mobile/deviceQuickActionExec.php");
$pageDeviceQuickActionExec->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeviceQuickActionExec);

################################
# End
################################

$MMCApp = &MMCApp::getInstance();
$MMCApp->addModule($mod);
