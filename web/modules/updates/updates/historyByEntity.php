<?php 
echo 'history';
echo '<pre>';
print_r($_GET);
echo '</pre>';

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

$completename = htmlentities($_GET['completename']) ?? '';

$p = new PageGenerator(_T(sprintf("History on entity %s",$completename), 'updates'));
$p->setSideMenu($sidemenu);

$p->display();
$params = ['entity' => $_GET['entity'], 'completename' => $_GET['completename']];
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxHistoryByEntity"), "container", $params, 'form');
$ajax->display();
$ajax->displayDivToUpdate();
?>