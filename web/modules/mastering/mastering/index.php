<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mastering/includes/xmlrpc.php");

$p = new PageGenerator(_T("Mastering test", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();


echo '<pre>';
print_r($test);
echo '</pre>';
?>

