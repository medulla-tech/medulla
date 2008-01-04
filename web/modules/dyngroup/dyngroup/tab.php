<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("Group creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
$p->addTab("tabdyn", _T("Dynamic group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", array());
$p->addTab("tabsta", _T("Static group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", array());
$p->display();

?>

