<?php


require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Installation Requests",'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("kiosk/kiosk/ajaxAcknowledges"));
$ajax->display();
$ajax->displayDivToUpdate();

?>
