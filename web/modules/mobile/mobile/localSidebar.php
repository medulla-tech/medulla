<?php
/**

*/
$sidemenu = new SideMenu();
$sidemenu->setClass("mobile");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All devices", 'mobile'), "mobile", "mobile", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups", 'mobile'), "mobile", "mobile", "groups"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Configurations", 'mobile'), "mobile", "mobile", "configurations"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Applications", 'mobile'), "mobile", "mobile", "applications"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Files", 'mobile'), "mobile", "mobile", "files"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Push messages", 'mobile'), "mobile", "mobile", "pushMessages"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Messages", 'mobile'), "mobile", "mobile", "messaging"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Network Filtering", 'mobile'), "mobile", "mobile", "netfilterSettings"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Contacts sync", 'mobile'), "mobile", "mobile", "contactsList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Photos", 'mobile'), "mobile", "mobile", "photosList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Device Export/Import", 'mobile'), "mobile", "mobile", "deviceExport"));
 ?>
