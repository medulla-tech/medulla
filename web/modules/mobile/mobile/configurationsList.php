<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Affichage formulaire
$p = new PageGenerator(_T("Configurations", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

// Display notification if redirected from save
if (isset($_GET['saved']) && $_GET['saved'] == '1') {
    new NotifyWidgetSuccess(_T("Configuration saved successfully", "mobile"));
}
if (isset($_GET['error']) && $_GET['error'] == '1') {
    new NotifyWidgetFailure(_T("Failed to save configuration", "mobile"));
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxConfigurationsList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
