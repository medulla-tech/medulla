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
$submod->setImg('modules/mobile/graph/navbar/mobile');
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
$pageDeleteDevice->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageDeleteDevice);

################################
# detailed info page
################################
$pageDetailedInfo = new Page("detailedInfo", _T('Detailed Information', 'mobile'));
$pageDetailedInfo->setFile("modules/mobile/mobile/detailedInfo.php");
$pageDetailedInfo->setOptions(array("visible" => false));
$submod->addPage($pageDetailedInfo);

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
# GLPI Phones page
################################
$pageGlpiPhones = new Page("glpiPhonesList", _T('Phones (GLPI inventory)', 'mobile'));
$pageGlpiPhones->setFile("modules/mobile/mobile/glpiPhonesList.php");
$submod->addPage($pageGlpiPhones);

################################
# GLPI Phone inventory tabs (keeps user in mobile module)
################################
$pageGlpiPhoneTabs = new Page("glpiPhoneTabs", _T('Phone inventory (GLPI)', 'mobile'));
$pageGlpiPhoneTabs->setFile("modules/mobile/mobile/glpiPhoneTabs.php");
$pageGlpiPhoneTabs->setOptions(array("visible" => false));
$tab = new Tab("tab0", _T("Summary tab (GLPI)",        'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab1", _T("Hardware tab (GLPI)",        'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab2", _T("Connections tab (GLPI)",    'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab3", _T("Storage tab (GLPI)",        'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab4", _T("Network tab (GLPI)",        'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab5", _T("Softwares tab (GLPI)",      'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab6", _T("Administrative tab (GLPI)", 'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab7", _T("History tab (GLPI)",        'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab8", _T("Antivirus tab (GLPI)",      'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$tab = new Tab("tab9", _T("Registry tab (GLPI)",       'glpi')); $pageGlpiPhoneTabs->addTab($tab);
$submod->addPage($pageGlpiPhoneTabs);

################################
# Files page
################################
$pageFiles = new Page("files", _T('Files', 'mobile'));
$pageFiles->setFile("modules/mobile/mobile/filesList.php");
$submod->addPage($pageFiles);

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
$pageDeleteApplication->setOptions(array("AJAX" => false, "visible" => false, "noHeader" => true));

$submod->addPage($pageDeleteApplication);

$pageDeleteGlpiDevice = new Page("deleteGlpiDevice", _T('Delete GLPI Device', 'mobile'));
$pageDeleteGlpiDevice->setFile("modules/mobile/mobile/deleteGlpiDevice.php");
$pageDeleteGlpiDevice->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteGlpiDevice);

$pageDeleteFile = new Page("deleteFile", _T('Delete file', 'mobile'));
$pageDeleteFile->setFile("modules/mobile/mobile/deleteFile.php");
$pageDeleteFile->setOptions(array("AJAX" => false, "visible" => false, "noHeader" => true));
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
$pageDeleteConfiguration->setOptions(array("AJAX" => false, "visible" => false, "noHeader" => true));
$submod->addPage($pageDeleteConfiguration);

$pageDuplicateConfiguration = new Page("duplicateConfiguration", _T('Duplicate configuration', 'mobile'));
$pageDuplicateConfiguration->setFile("modules/mobile/mobile/duplicateConfiguration.php");
$pageDuplicateConfiguration->setOptions(array("visible" => false));
$submod->addPage($pageDuplicateConfiguration);

################################
# Groups pages
################################

$pageGroups = new Page("groups", _T('All groups', 'mobile'));
$pageGroups->setFile("modules/mobile/mobile/groups.php");
$submod->addPage($pageGroups);

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
$pageDeleteGroup->setOptions(array("AJAX" => false, "visible" => false, "noHeader" => true));
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
# Configuration Quick Actions page
################################
$pageConfigQuickAction = new Page("configQuickAction", _T('Configuration Quick Action', 'mobile'));
$pageConfigQuickAction->setFile("modules/mobile/mobile/configQuickAction.php");
$pageConfigQuickAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageConfigQuickAction);

$pageConfigQuickActionExec = new Page("configQuickActionExec", _T('Configuration Quick Action Exec', 'mobile'));
$pageConfigQuickActionExec->setFile("modules/mobile/mobile/configQuickActionExec.php");
$pageConfigQuickActionExec->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageConfigQuickActionExec);

# messaging pages
$pageMessaging = new Page("messaging", _T('Messages', 'mobile'));
$pageMessaging->setFile("modules/mobile/mobile/messaging.php");
$submod->addPage($pageMessaging);

$pagePushMessages = new Page("pushMessages", _T('Push messages', 'mobile'));
$pagePushMessages->setFile("modules/mobile/mobile/pushMessages.php");
$submod->addPage($pagePushMessages);

################################
# Contacts sync pages
################################

$pageContactsList = new Page("contactsList", _T('Device Contacts Sync', 'mobile'));
$pageContactsList->setFile("modules/mobile/mobile/contactsList.php");
$submod->addPage($pageContactsList);

$pageAjaxContactsList = new Page("ajaxContactsList", _T('Contacts list view', 'mobile'));
$pageAjaxContactsList->setFile("modules/mobile/mobile/ajaxContactsList.php");
$pageAjaxContactsList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxContactsList);

$pageContactsConfig = new Page("contactsConfig", _T('Edit contacts sync config', 'mobile'));
$pageContactsConfig->setFile("modules/mobile/mobile/contactsConfig.php");
$pageContactsConfig->setOptions(array("visible" => false));
$submod->addPage($pageContactsConfig);

$pageDeviceExport = new Page("deviceExport", _T('Device Export/Import', 'mobile'));
$pageDeviceExport->setFile("modules/mobile/mobile/deviceExport.php");
$submod->addPage($pageDeviceExport);

$pageDeviceExportAction = new Page("deviceExportAction", _T('Export devices action', 'mobile'));
$pageDeviceExportAction->setFile("modules/mobile/mobile/deviceExportAction.php");
$pageDeviceExportAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageDeviceExportAction);

$pageDeviceImportAction = new Page("deviceImportAction", _T('Import devices action', 'mobile'));
$pageDeviceImportAction->setFile("modules/mobile/mobile/deviceImportAction.php");
$pageDeviceImportAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageDeviceImportAction);

$pagePhotosList = new Page("photosList", _T('Device Photos', 'mobile'));
$pagePhotosList->setFile("modules/mobile/mobile/photosList.php");
$submod->addPage($pagePhotosList);

$pageAjaxPhotosList = new Page("ajaxPhotosList", _T('Photos list AJAX', 'mobile'));
$pageAjaxPhotosList->setFile("modules/mobile/mobile/ajaxPhotosList.php");
$pageAjaxPhotosList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxPhotosList);

$pageDeletePhoto = new Page("deletePhoto", _T('Delete photo', 'mobile'));
$pageDeletePhoto->setFile("modules/mobile/mobile/deletePhoto.php");
$pageDeletePhoto->setOptions(array("AJAX" => false, "visible" => false, "noHeader" => true));
$submod->addPage($pageDeletePhoto);

$pagePhotoFile = new Page("photoFile", _T('Photo file', 'mobile'));
$pagePhotoFile->setFile("modules/mobile/mobile/photoFile.php");
$pagePhotoFile->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pagePhotoFile);

# send message forms (hidden pages)
$pageNewMessage = new Page("newMessage", _T('Send new message', 'mobile'));
$pageNewMessage->setFile("modules/mobile/mobile/newMessage.php");
$pageNewMessage->setOptions(array("visible" => false));
$submod->addPage($pageNewMessage);

$pageNewPushMessage = new Page("newPushMessage", _T('Send new push message', 'mobile'));
$pageNewPushMessage->setFile("modules/mobile/mobile/newPushMessage.php");
$pageNewPushMessage->setOptions(array("visible" => false));
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
# Remote Control page
################################
$pageRemoteControlAction = new Page("remoteControlAction", _T('Remote Control', 'mobile'));
$pageRemoteControlAction->setFile("modules/mobile/mobile/remoteControlAction.php");
$pageRemoteControlAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageRemoteControlAction);

$pageRemoteControlStop = new Page("remoteControlStop", _T('Remote Control Stop', 'mobile'));
$pageRemoteControlStop->setFile("modules/mobile/mobile/remoteControlStop.php");
$pageRemoteControlStop->setOptions(array("visible" => false, "noHeader" => true, "AJAX" => true));
$submod->addPage($pageRemoteControlStop);


################################
# Network Traffic Filtering
################################

$pageNetfilterSettings = new Page("netfilterSettings", _T('Network Filtering', 'mobile'));
$pageNetfilterSettings->setFile("modules/mobile/mobile/netfilterSettings.php");
$submod->addPage($pageNetfilterSettings);

################################
# MDM User Access Management
################################

$pageMobileUsers = new Page("mobileUsers", _T('MDM User Access', 'mobile'));
$pageMobileUsers->setFile("modules/mobile/mobile/mobileUsers.php");
$submod->addPage($pageMobileUsers);

$pageConfigureMdmUserAjax = new Page("configureMdmUserAjax", _T('Configure MDM User', 'mobile'));
$pageConfigureMdmUserAjax->setFile("modules/mobile/mobile/configureMdmUserAjax.php");
$pageConfigureMdmUserAjax->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageConfigureMdmUserAjax);

################################
# MDM Roles Management
################################

$pageMobileRoles = new Page("mobileRoles", _T('MDM Roles', 'mobile'));
$pageMobileRoles->setFile("modules/mobile/mobile/mobileRoles.php");
$submod->addPage($pageMobileRoles);

$pageConfigureMdmRoleAjax = new Page("configureMdmRoleAjax", _T('Configure MDM Role', 'mobile'));
$pageConfigureMdmRoleAjax->setFile("modules/mobile/mobile/configureMdmRoleAjax.php");
$pageConfigureMdmRoleAjax->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageConfigureMdmRoleAjax);

$pageSendEnrollmentEmailAjax = new Page("sendEnrollmentEmailAjax", _T('Send Enrollment Email', 'mobile'));
$pageSendEnrollmentEmailAjax->setFile("modules/mobile/mobile/sendEnrollmentEmailAjax.php");
$pageSendEnrollmentEmailAjax->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageSendEnrollmentEmailAjax);

$pageNetfilterRules = new Page("netfilterRules", _T('Filter Rules', 'mobile'));
$pageNetfilterRules->setFile("modules/mobile/mobile/netfilterRules.php");
$pageNetfilterRules->setOptions(array("visible" => false));
$submod->addPage($pageNetfilterRules);

$pageNetfilterRuleAction = new Page("netfilterRuleAction", _T('Filter Rule Action', 'mobile'));
$pageNetfilterRuleAction->setFile("modules/mobile/mobile/netfilterRuleAction.php");
$pageNetfilterRuleAction->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageNetfilterRuleAction);

$pageDeleteNetfilterRule = new Page("deleteNetfilterRule", _T('Delete Filter Rule', 'mobile'));
$pageDeleteNetfilterRule->setFile("modules/mobile/mobile/deleteNetfilterRule.php");
$pageDeleteNetfilterRule->setOptions(array("visible" => false, "noHeader" => true));
$submod->addPage($pageDeleteNetfilterRule);

$pageAjaxNetfilterRules = new Page("ajaxNetfilterRules", _T('Ajax Filter Rules', 'mobile'));
$pageAjaxNetfilterRules->setFile("modules/mobile/mobile/ajaxNetfilterRules.php");
$pageAjaxNetfilterRules->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxNetfilterRules);

################################
# End
################################

$MMCApp = &MMCApp::getInstance();
$MMCApp->addModule($mod);
