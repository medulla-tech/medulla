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
$submod->setImg('img/other/mobile_down');
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
# add application page
################################

$pageAddApplication = new Page("addApplication", _T('Add an application', 'mobile'));
$pageAddApplication->setFile("modules/mobile/mobile/addApplication.php");
$submod->addPage($pageAddApplication);

###############################
# create icon page (ajax)
################################
$pageAjaxCreateIcon = new Page("createIcon", _T('Create an icon', 'mobile'));
$pageAjaxCreateIcon->setFile("modules/mobile/mobile/ajaxCreateIcon.php");
$pageAjaxCreateIcon->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxCreateIcon);

################################
# get icons page (ajax)
################################
$pageAjaxGetIcons = new Page("getIcons", _T('Get icons', 'mobile'));
$pageAjaxGetIcons->setFile("modules/mobile/mobile/ajaxGetIcons.php");
$pageAjaxGetIcons->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxGetIcons);

################################
# delete icon page (ajax)
################################
$pageAjaxDeleteIcon = new Page("deleteIcon", _T('Delete icon', 'mobile'));
$pageAjaxDeleteIcon->setFile("modules/mobile/mobile/ajaxDeleteIcon.php");
$pageAjaxDeleteIcon->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxDeleteIcon);

################################
# icon settings page
################################
$pageIconSettings = new Page("iconSettings", _T('Icon settings', 'mobile'));
$pageIconSettings->setFile("modules/mobile/mobile/iconSettings.php");
$submod->addPage($pageIconSettings);

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
$pageGlpiDevices = new Page("glpiDevices", _T('All devices glpi', 'mobile'));
$pageGlpiDevices->setFile("modules/mobile/mobile/glpiDevicesList.php");
$submod->addPage($pageGlpiDevices);

# GLPI phones page
$pageGlpiPhones = new Page("glpiPhones", _T('All phones glpi', 'mobile'));
$pageGlpiPhones->setFile("modules/mobile/mobile/glpiPhonesList.php");
$submod->addPage($pageGlpiPhones);

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

$pageAjaxGroupList = new Page("ajaxGroupList", _T('Groups list view', 'mobile'));
$pageAjaxGroupList->setFile("modules/mobile/mobile/ajaxGroupList.php");
$pageAjaxGroupList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxGroupList);

$pageDeleteGroup = new Page("deleteGroup", _T('Delete group', 'mobile'));
$pageDeleteGroup->setFile("modules/mobile/mobile/deleteGroup.php");
$pageDeleteGroup->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteGroup);

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
# End
################################

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>