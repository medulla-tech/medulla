<?php
/**

*/
$sidemenu = new SideMenu();
$sidemenu->setClass("mobile");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All devices", 'mobile'), "mobile", "mobile", "index"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a device", 'mobile'), "mobile", "mobile", "addDevice"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups", 'mobile'), "mobile", "mobile", "groups"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a group", 'mobile'), "mobile", "mobile", "addGroup"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Applications", 'mobile'), "mobile", "mobile", "applications"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add an application", 'mobile'), "mobile", "mobile", "addApplication"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Icon settings", 'mobile'), "mobile", "mobile", "iconSettings"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Configurations", 'mobile'), "mobile", "mobile", "configurations"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Files", 'mobile'), "mobile", "mobile", "files"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a file", 'mobile'), "mobile", "mobile", "addFile"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("All devices glpi", 'mobile'), "mobile", "mobile", "glpiDevices"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Functions", 'mobile'), "mobile", "mobile", "functions"));
 ?>