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
# add configuration page  
################################

$pageConfig = new Page("addConfiguration", _T('Add a configuration', 'mobile'));
$pageConfig->setFile("modules/mobile/mobile/addConfiguration.php");
$submod->addPage($pageConfig);


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

$pageAjaxConfigurationsList = new Page("ajaxConfigurationsList", _T('Configurations list view', 'mobile'));
$pageAjaxConfigurationsList->setFile("modules/mobile/mobile/ajaxConfigurationsList.php");
$pageAjaxConfigurationsList->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($pageAjaxConfigurationsList);

$pageDeleteConfiguration = new Page("deleteConfiguration", _T('Delete configuration', 'mobile'));
$pageDeleteConfiguration->setFile("modules/mobile/mobile/deleteConfiguration.php");
$pageDeleteConfiguration->setOptions(array("AJAX" => false, "visible" => false));
$submod->addPage($pageDeleteConfiguration);


################################
# Functions page (HMDM features)
################################

$pageFunctions = new Page("functions", _T('Functions', 'mobile'));
$pageFunctions->setFile("modules/mobile/mobile/functions.php");
$submod->addPage($pageFunctions);

################################
# End
################################

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>