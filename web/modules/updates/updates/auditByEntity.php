<?php 

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

$completename = htmlentities($_GET['completename']) ?? '';

$p = new PageGenerator(sprintf(_T("Updates history for entity %s", 'updates'), $completename));
$p->setSideMenu($sidemenu);

$p->display();
$params = ['entity' => $_GET['entity'], 'completename' => $_GET['completename']];
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxAuditByEntity"), "container", $params, 'form');
$ajax->display();
$ajax->displayDivToUpdate();
?>