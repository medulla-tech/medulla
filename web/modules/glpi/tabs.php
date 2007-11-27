<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (GLPI)"), $_GET['name']), "modules/glpi/glpi/header.php");
$p->addTab("tab0", "Hardware", "", "modules/glpi/glpi/view_hardware.php", array('name'=>$_GET['name']));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network', 'Controller') as $tab) {
    $p->addTab("tab$i", $tab, "", "modules/glpi/glpi/view_part.php", array('name'=>$_GET['name'], 'part' => $tab));
    $i++;
}

$p->display();

?>
