<?php
require("graph/navbar.inc.php");
require("localSidebar.php");


$p = new PageGenerator(_T("Liste de tous les mobiles", 'mobile'));
$p->setSideMenu($sidemenu);

$p->display();


$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxMobileList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>