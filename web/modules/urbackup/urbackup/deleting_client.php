<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$groupname = htmlspecialchars($_GET["groupname"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);
$clientid = htmlspecialchars($_GET["clientid"]);
$clientname = htmlspecialchars($_GET["clientname"]);

$p = new PageGenerator(_T("Delete group", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_remove = xmlrpc_remove_client($jidMachine);

?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$clientid.'&clientname='.$clientname.'&groupename='.$groupename.'&jidmachine='.$jidmachine.'&disableclient=true';

header("Location: ".$url);
?>
