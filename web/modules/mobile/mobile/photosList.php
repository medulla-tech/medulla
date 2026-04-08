<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("Device Photos", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();
?>

<?php
$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxPhotosList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
