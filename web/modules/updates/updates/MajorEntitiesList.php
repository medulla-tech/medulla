<?php


require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");
$p = new PageGenerator(_T("Entities Compliance", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

$params = ["source" => "xmppmaster"];

$ajaxmajor = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesList"),
                            "container-Major", $params, 'formMajor');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();

?>
