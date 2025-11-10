<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;
$entityuuid = (isset($_GET['entity'])) ? htmlentities($_GET['entity']) : "UUID0";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$params = ["source" => "xmppmaster"];

$p = new PageGenerator(_T("Entity Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

$refresh = new RefreshButton();
print "<br/>";
$refresh->display();

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesList"), "container", array('source' => 'xmppmaster'), 'formRunning');

$ajax->setRefresh($refresh->refreshtime());
$ajax->display();
$ajax->displayDivToUpdate();

?>
