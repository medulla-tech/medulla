<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require('modules/msc/includes/machines.inc.php'); // TODO machines should be given by base, not by glpi !

$uuid = '';
if (isset($_GET['uuid'])) {
    $uuid = $_GET['uuid'];
} elseif (isset($_GET['objectUUID'])) {
    $uuid = $_GET['objectUUID'];
}
$machine = getMachine(array('uuid'=>$uuid), $ping = False);

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (GLPI)", "glpi"), $machine->hostname), "modules/glpi/glpi/header.php");
$p->addTab("tab0", _T("Hardware", "glpi"), "", "modules/glpi/glpi/view_hardware.php", array('hostname'=>$machine->hostname, 'uuid'=>$uuid));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network'=>_T('Network', "glpi"), 'Controller'=>_T('Controller', "glpi")) as $tab=>$str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('hostname'=>$machine->hostname, 'uuid'=>$uuid, 'part' => $tab));
    $i++;
}

$p->display();

?>
