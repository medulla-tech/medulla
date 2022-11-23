<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);

$p = new PageGenerator(_T("Delete group", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

#au niveau du client
# set backup_enable to 0 too
$client_remove = xmlrpc_remove_client($jidMachine);

?>
<br>
<?php

$url = 'main.php?module=base&submod=computers&action=machinesList';

header("Location: ".$url);
?>