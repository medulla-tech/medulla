<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");
require_once("modules/glpi/includes/html.php");


unset($_POST);
$_POST = [];

$p = new PageGenerator(_T("Create An Action", 'mastering'));
$p->setSideMenu($sidemenu);
$p->display();

$entitiesList = [];
$entitiesIds = [];

list($entitiesList, $entitiesIds) = getEntitiesSelectableElements();

$ajax = new AjaxFilterLocation(urlStrRedirect("mastering/mastering/ajaxActionMachine"), "container", "entity");

$ajax->setElements($entitiesList);
$ajax->setElementsVal($entitiesIds);

$ajax->display();
$ajax->displayDivToUpdate();
?>

