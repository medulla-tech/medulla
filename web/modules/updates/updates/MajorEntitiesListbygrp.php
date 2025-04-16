<?php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/xmlrpc.php");

$params = array(
    "source" => "xmppmaster",
    "gid" => isset($_GET['gid']) ? $_GET['gid'] : null,
    "groupname" => isset($_GET['groupname']) ? $_GET['groupname'] : null
);

$p = new PageGenerator(_T("Grp Compliance", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();




$ajaxmajor = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesListbygrp"),
                            "container-Major", $params, 'formMajor');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();

?>
