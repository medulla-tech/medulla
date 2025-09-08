<?php
/**

*/
$sidemenu = new SideMenu();
$sidemenu->setClass("mobile");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Tous les mobiles", 'mobile'), "mobile", "mobile", "index"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Enrôler un téléphone", 'mobile'), "mobile", "mobile", "enrolMobile"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Configuration", 'mobile'), "mobile", "mobile", "addConfiguration"));
?>
