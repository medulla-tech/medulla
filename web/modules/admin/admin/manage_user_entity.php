<?php

// modules/admin/admin/manage_entity.php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
$p = new PageGenerator(_T("Client Entities Management", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

$params = ["source" => "xmppmaster"];


$ajaxmajor = new AjaxFilter(urlStrRedirect("admin/admin/ajax_entity_user_user"),
                            "container-ajax_entity_user_user", $params, 'entity_user_user');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();

$ajaxmajor = new AjaxFilter(urlStrRedirect("admin/admin/ajax_entity_user_admin"),
                            "container-ajax_entity_user_admin", $params, 'entity_user_admin');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();

?>
