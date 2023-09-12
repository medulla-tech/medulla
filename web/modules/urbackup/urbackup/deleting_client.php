<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$groupname = htmlspecialchars($_GET["groupname"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);
$clientid = htmlspecialchars($_GET["clientid"]);
$clientname = htmlspecialchars($_GET["clientname"]);
$editclient = htmlspecialchars($_GET["editclient"]);
$authkey = htmlspecialchars($_GET["authkey"]);

$p = new PageGenerator(_T("Delete group", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

if ($editclient == "disable")
{
    $clientRemove = xmlrpc_remove_client($jidMachine, $clientid);
    $editStateClient = "enable";
}

if ($editclient == "enable")
{
    $clientAdd = xmlrpc_enable_client($jidMachine, $clientid, $authkey);
    $editStateClient = "disable";
}


?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$clientid.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidmachine.'&editStateClient='.$editStateClient;

header("Location: ".$url);
?>
