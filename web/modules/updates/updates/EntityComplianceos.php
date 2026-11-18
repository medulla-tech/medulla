<?php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/updates/includes/html.inc.php");

// Page reached by redirection from "index": forces the active menu entry.
$sidemenu->forceActiveItem("index");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Update status", "updates"), $sidemenu);
    return;
}

$p = new PageGenerator(_T("Update status", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
updatesStaleNotice();

$visibleTabs = updatesVisibleTabs(updatesStatusTabs());
if (empty($visibleTabs)) {
    return;
}

$entity = updatesSelectedEntity();
$tabParams = $entity ? array('location' => $entity['uuid']) : array();

updatesTabbedPage($visibleTabs, $tabParams);
?>
