<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Hardware'; }

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$prefix = '';
if ($_GET['hostname'] != '') {
    $p->addTop(sprintf(_T("%s's inventory", 'inventory'), $_GET['hostname']), "modules/inventory/inventory/header.php");
} else {
    $p->addTop(sprintf(_T("%s's content inventory", 'inventory'), $_GET['groupname']), "modules/inventory/inventory/header.php");
    $prefix = 'group';
}

// TODO get the list with trads from agent (conf file...)
$tab = 'Hardware';
$i = 0;
$p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$_GET['gid'], 'groupname'=>$_GET['groupname']));
$tab = 'Bios';
$i = 5;
$p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$_GET['gid'], 'groupname'=>$_GET['groupname']));

$i = 1;
foreach (array('Software', 'Network', 'Controller', 'Registry') as $tab) {
    $p->addTab($prefix."tab$i", _T($tab, 'inventory'), "", "modules/inventory/inventory/view_part.php", array('uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'part' => $tab, 'gid'=>$_GET['gid'], 'groupname'=>$_GET['groupname']));
    $i++;
}

$p->display();

?>
