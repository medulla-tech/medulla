<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Upgrades", "updates"), $sidemenu);
    return;
}

$p = new PageGenerator(_T("Upgrades", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
updatesStaleNotice();

$visibleTabs = updatesVisibleTabs(updatesUpgradeTabs());
if (empty($visibleTabs)) {
    return;
}

$entity = updatesSelectedEntity();
$tabParams = $entity ? array('location' => $entity['uuid']) : array();

updatesTabbedPage($visibleTabs, $tabParams);
?>
