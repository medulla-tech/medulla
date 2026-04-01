<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$p = new PageGenerator(_T("Detail on actions", 'mastering'));

$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();


$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxActionList"), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>