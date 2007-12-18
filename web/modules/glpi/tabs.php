<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (GLPI)", "glpi"), $_GET['name']), "modules/glpi/glpi/header.php");
$p->addTab("tab0", _T("Hardware", "glpi"), "", "modules/glpi/glpi/view_hardware.php", array('name'=>$_GET['name']));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network'=>_T('Network', "glpi"), 'Controller'=>_T('Controller', "glpi")) as $tab=>$str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('name'=>$_GET['name'], 'part' => $tab));
    $i++;
}

$p->display();

?>
