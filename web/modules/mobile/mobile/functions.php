<?php
require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

$p->addTab("tabaudit", _T("Audit", "mobile"), "", "modules/mobile/mobile/audit.php", array());
$p->addTab("tabdetailed", _T("Detailed information", "mobile"), "", "modules/mobile/mobile/detailed_info.php", array());
$p->addTab("tabmessaging", _T("Messaging", "mobile"), "", "modules/mobile/mobile/messaging.php", array());

$p->display();

?>
