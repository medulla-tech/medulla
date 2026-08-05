<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

// require_once("modules/updates/includes/xmlrpc.php");
// require_once("modules/admin/includes/xmlrpc.php");
// require_once("modules/xmppmaster/includes/xmlrpc.php");
// require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;

// Cette page est atteinte via une redirection depuis l'action "index" : sans ce
// forcage, aucune entree du menu lateral ne correspond a l'action courante.
$sidemenu->forceActiveItem("index");

$p = new PageGenerator(_T("Entity Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();


$p = new TabbedPageGenerator();
$p->addTab("tabwin", _T("Windows", "updates"), "",
           "modules/updates/updates/entity/ajaxEntityCompliance.php", array());

$p->addTab("tablinux", _T("Linux", "updates"), "",
     "modules/updates/updates/entity/ajaxEntityComplianceLinux.php", array());

$p->display();
?>
