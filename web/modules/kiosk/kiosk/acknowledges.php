<?php


require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Acknowledges",'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("kiosk/kiosk/ajaxAcknowledges"));
$ajax->display();
$ajax->displayDivToUpdate();

?>