<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
if ($_GET['hostname'] != '') {
    $p->addTop(sprintf(_T("%s's inventory"), $_GET['hostname']), "modules/inventory/inventory/header.php");
} else {
    $p->addTop(sprintf(_T("%s's content inventory"), $_GET['groupname']), "modules/inventory/inventory/header.php");
}
$p->addTab("tab0", "Hardware", "", "modules/inventory/inventory/view_hardware.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'gid'=>$_GET['gid'], 'groupname'=>$_GET['groupname']));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network', 'Controller') as $tab) {
    $p->addTab("tab$i", $tab, "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$_GET['gid'], 'groupname'=>$_GET['groupname']));
    $i++;
}

$p->display();

?>
