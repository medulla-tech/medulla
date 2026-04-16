<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Contacts Sync", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
	return;
}

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxContactsList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
