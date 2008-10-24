<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Hardware'; }

$uuid = '';
$hostname = '';
if (isset($_GET['uuid'])) { $uuid = $_GET['uuid']; }
if (isset($_GET['hostname'])) { $hostname = $_GET['hostname']; }

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (GLPI)", "glpi"), $hostname), "modules/glpi/glpi/header.php");
$p->addTab("tab0", _T("Hardware", "glpi"), "", "modules/glpi/glpi/view_hardware.php", array('hostname'=>$hostname, 'uuid'=>$uuid));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network'=>_T('Network', "glpi"), 'Controller'=>_T('Controller', "glpi")) as $tab=>$str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('hostname'=>$hostname, 'uuid'=>$uuid, 'part' => $tab));
    $i++;
}

$p->display();

?>
