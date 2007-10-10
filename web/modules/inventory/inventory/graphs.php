<?php

require("localSidebar.php");
require("graph/navbar.inc.php");
require("modules/inventory/includes/xmlrpc.php");
require("modules/inventory/includes/html.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];

$p = new PageGenerator(_T("Graphique"));
$p->setSideMenu($sidemenu);
$p->display();

$img = new RenderedImage(urlStr("inventory/inventory/graph", array("type"=>$type, "field"=>$field, "filter"=>$filter)), 'graph', 'center');
$img->display();

$lnk = new RenderedLink(urlStr("inventory/inventory/".strtolower($type), array('filter'=>$filter)), _T('back'));
$lnk->display();

?>

