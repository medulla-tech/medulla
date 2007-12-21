<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("Group creation"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
$p->addTab("tabdyn", "Dynamic group creation", "", "modules/dyngroup/dyngroup/creator.php", array());
$p->addTab("tabsta", "Static group creation", "", "modules/dyngroup/dyngroup/add_groups.php", array());
$p->display();

?>

