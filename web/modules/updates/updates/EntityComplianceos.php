<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

// require_once("modules/updates/includes/xmlrpc.php");
// require_once("modules/admin/includes/xmlrpc.php");
// require_once("modules/xmppmaster/includes/xmlrpc.php");
// require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;

$p = new PageGenerator(_T("Entity Compliance Operating Systems", "updates"));
$p->setSideMenu($sidemenu);
$p->display();


$p = new TabbedPageGenerator();
$p->addTab("tabwin", _T("Os Windows", "updates"), "",
           "modules/updates/updates/entity/ajaxEntityCompliance.php", array());

$p->addTab("tablinux", _T("OS Linux", "updates"), "",
     "modules/updates/updates/entity/ajaxEntityComplianceLinux.php", array());

$p->display();
?>
