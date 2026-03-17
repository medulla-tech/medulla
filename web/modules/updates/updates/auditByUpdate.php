<?php 

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

$p = new PageGenerator(sprintf(_T("Updates history for update %s", 'updates'), $completename));
$p->setSideMenu($sidemenu);

$p->display();
$params = ['kb' => $_GET['kb'], 'updateid' => $_GET['updateid']];
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxAuditByUpdate"), "container", $params, 'form');
$ajax->display();
$ajax->displayDivToUpdate();
?>