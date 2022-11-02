<?php

/* Build log sidebar that aggregates all log viewers from all available modules */

$sidemenu= new SideMenu();
$sidemenu->setClass("logview");

$MMCApp =& MMCApp::getInstance();

$mod = $MMCApp->getModule("base");
$submod = $mod->getSubmod("logview");
 foreach ($submod->getPages() as $page) {
    if ($page->isVisible()){
       $sidemenu->addSideMenuItem(new SideMenuItem($page->getDescription(),      "base", "logview", $page->getAction()));
    }
}
    $p = new PageGenerator();
    $p->setSideMenu($sidemenu);
    $p->displaySideMenu();
?>
