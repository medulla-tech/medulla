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

$p = new PageGenerator(_T("Enable or disable client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clientEnable = xmlrpc_getComputersEnableValue($jidMachine);

if ($clientEnable['0']['enabled'] == '1')
{
    if ($editclient == "disable")
    {
        $clientRemove = xmlrpc_remove_client($jidMachine, $clientid);
        $editStateClient = "disable";
    }

    if ($editclient == "enable")
    {
        $client = xmlrpc_get_client_status($clientid);
        $client_authkey = $client["0"]["authkey"];

        $clientAdd = xmlrpc_enable_client($jidMachine, $clientid, $client_authkey);
        $editStateClient = "enable";
    }

    $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$clientid.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine.'&editStateClient='.$editStateClient.'&error=false';
}
else
{
    $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$clientid.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine.'&error=true';
}
?>
<br>
<?php
header("Location: ".$url);
?>
