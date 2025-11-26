<?php
require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

$p->addTab("tabaudit", _T("Audit", "mobile"), "", "modules/mobile/mobile/audit.php", array());

$p->display();

?>
