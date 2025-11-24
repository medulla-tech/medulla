<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Applications", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxApplicationsList"));
$ajax->display();
$ajax->displayDivToUpdate();