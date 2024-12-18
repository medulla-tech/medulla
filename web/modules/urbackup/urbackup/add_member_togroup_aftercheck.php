<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse.
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = $_POST['group'];
$client_id = htmlspecialchars($_GET["clientid"]);
$clientname = htmlspecialchars($_GET["clientname"]);
$jidMachine = htmlspecialchars($_GET["jidmachine"]);
$auth = htmlspecialchars($_GET["auth"]);

$group_id_new = "-".$group_id;

print_r($group_id_new);

$p = new PageGenerator(_T("Assign member to profile", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$ini_array_local = parse_ini_file("/etc/mmc/plugins/urbackup.ini.local");
$username_urbackup = isset($ini_array_local["usernameapi"]) ? $ini_array_local["usernameapi"] : $ini_array["usernameapi"];
$password_urbackup = isset($ini_array_local["passwordapi"]) ? $ini_array_local["passwordapi"] : $ini_array["passwordapi"];
$url_urbackup = isset($ini_array_local["url"]) ? $ini_array_local["url"] : $ini_array["url"];

//-----------------------------------START LOGIN FUNCTION
$url = $url_urbackup."?a=login";

$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
'username'=>$username_urbackup,
'password'=>$password_urbackup,
'plainpw'=>1
];

$urlencoded = "";
foreach($datas as $key=>$val)
{
    $urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid))
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
    $result = (array)json_decode($response);

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1)
    $session = $result['session'];
//-----------------------------------END LOGIN

//-----------------------------------START ADD MEMBER TO GROUP FUNCTION
$url = $url_urbackup."?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>"clientsettings_save",
    't_clientid'=>$group_id_new,
    'overwrite'=>"true",
    'group_mem_changes'=>$client_id.$group_id_new,
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val)
{
    $urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid))
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
    $result = (array)json_decode($response);

curl_close($curlid);

$array = json_decode(json_encode($reviews), true);

$addgroup = $result;
$array_progress = json_decode(json_encode($addgroup), true);

$clients = $array_progress['navitems']['clients'];
//-----------------------------------END ADD MEMBER TO GROUP
?>
<br>
<?php

foreach($clients as $client)
{
    if ($client['name'] == $clientname)
    {
        $groupname = $client['groupname'];
    }
}

$enable_client = xmlrpc_enable_client($jidMachine, $client_id, $auth);
$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$client_id.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine.'&newClient=true';

header("Location: ".$url);
?>