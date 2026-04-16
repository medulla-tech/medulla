<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Photos", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

if (!xmlrpc_require_configured_hmdm_account()) {
	return;
}
?>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxPhotosList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
