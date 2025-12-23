<?php
require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

$p->addTab("tabaudit", _T("Audit", "mobile"), "", "modules/mobile/mobile/audit.php", array());
$p->addTab("tabdetailed", _T("Detailed information", "mobile"), "", "modules/mobile/mobile/detailedInfo.php", array());
$p->addTab("tabmessaging", _T("Messaging", "mobile"), "", "modules/mobile/mobile/messaging.php", array());
$p->addTab("tabpush", _T("Push messages", "mobile"), "", "modules/mobile/mobile/pushMessages.php", array());
$p->addTab("taglogs", _T("Logs", "mobile"), "", "modules/mobile/mobile/logs.php", array());

$p->display();

?>
