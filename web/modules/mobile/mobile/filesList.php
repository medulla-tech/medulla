<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Page header and filters
$p = new PageGenerator(_T("Files", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxFilesList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>