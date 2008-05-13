<?php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/html.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];

$p = new PageGenerator(_T("Graphique"));
$p->setSideMenu($sidemenu);
$p->display();

$img = new RenderedImage(urlStr("inventory/inventory/graph", array("type"=>$type, "field"=>$field, "filter"=>$filter)), 'graph', 'center');
$img->display();

$params = array();
foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
    $params[$get] = $_GET[$get];
}

$lnk = new RenderedLink(urlStr("base/computers/invtabs", $params), _T('back')); //array('tab'=>$_GET['tab'], 'filter'=>$filter));
$lnk->display();

?>

