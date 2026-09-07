<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

// require_once("modules/updates/includes/xmlrpc.php");
// require_once("modules/admin/includes/xmlrpc.php");
// require_once("modules/xmppmaster/includes/xmlrpc.php");
// require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;

// Page atteinte par redirection depuis "index" : force l'entree de menu active.
$sidemenu->forceActiveItem("index");

$p = new PageGenerator(_T("Entities Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();


$p = new TabbedPageGenerator();
$p->addTab("tabwin", _T("Windows", "updates"), "",
           "modules/updates/updates/entity/ajaxEntityCompliance.php", array());

$p->addTab("tablinux", _T("Linux", "updates"), "",
     "modules/updates/updates/entity/ajaxEntityComplianceLinux.php", array());

$p->display();
?>
