<?

$sidemenu= new SideMenu();
$sidemenu->setClass("logs");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Show all logs", 'msc'), "msc", "logs", "all"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Show all pending task's logs", 'msc'), "msc", "logs", "pending"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Show all running task's logs", 'msc'), "msc", "logs", "running"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Show all finished task's logs", 'msc'), "msc", "logs", "finished"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Show custom state task's logs", 'msc'), "msc", "logs", "custom"));

?>
