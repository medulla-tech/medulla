<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's secure control", 'msc'), $_GET['name']), "modules/msc/msc/header.php");
$p->addTab("tablaunch", _T("Launch Actions", 'msc'), "", "modules/msc/msc/launch.php", array('name'=>$_GET['name']));
$p->addTab("tablogs", _T("Logs", 'msc'), "", "modules/msc/msc/logs.php", array('name'=>$_GET['name']));
$p->addTab("tabhistory", _T("History", 'msc'), "", "modules/msc/msc/history.php", array('name'=>$_GET['name']));
$p->display();

?>
