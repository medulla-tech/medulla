<?php
$sidemenu= new SideMenu();

$sidemenu->setClass("status");

$LMCApp =& LMCApp::getInstance();

$mod = $LMCApp->getModule('base');
$submod = $mod->getSubmod('status');



foreach ($submod->getPages() as $page) {
$sidemenu->addSideMenuItem(new SideMenuItem($page->getDescription(),"base","status",$page->getAction()));
}

$p = new PageGenerator();

/**
 * Affichage du menu
 */
$p->setSideMenu($sidemenu); //$sidemenu inclus dans localSideBar.php
$p->displaySideMenu();

?>