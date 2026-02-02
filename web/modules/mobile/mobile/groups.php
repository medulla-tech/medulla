<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("List of all groups", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxGroupList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>
