<?php
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Synthèse CVE", 'security'));
$p->setSideMenu($sidemenu);
$p = new PageGenerator(_T("Synthèse CVE", 'security'));
$p->setSideMenu($sidemenu);

/* ajoute la feuille de style */
echo "<link rel='stylesheet' href='modules/security/graph/index.css?v=1'>";
$p->display();

// Liste Ajax (barre de recherche + pagination identiques à kiosk)
$ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxSecurityList"));
$ajax->display();
$ajax->displayDivToUpdate();
