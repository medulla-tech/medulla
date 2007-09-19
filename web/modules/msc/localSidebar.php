<?

$sidemenu= new SideMenu();
$sidemenu->setClass("msc");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("General"), "msc", "msc", "general"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Repository"), "msc", "msc", "repository"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Explorer"), "msc", "msc", "explorer"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Commands states"), "msc", "msc", "cmd_state"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All commands states"), "msc", "msc", "all_cmd_state"));

?>
