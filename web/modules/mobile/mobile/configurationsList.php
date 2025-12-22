<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Affichage formulaire
$p = new PageGenerator(_T("Configurations", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxConfigurationsList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
