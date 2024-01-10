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

$clientname = htmlspecialchars($_GET["cn"]);
$jidMachine = htmlspecialchars($_GET["jid"]);

$p = new PageGenerator(_T("Assign profile to computer ".$clientname, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clients = xmlrpc_get_backups_all_client();
$clients = $clients["clients"];

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
foreach($datas as $key=>$val){
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
{
$result = (array)json_decode($response);
}

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1){
    $session = $result['session'];
}
//-----------------------------------END LOGIN

//-----------------------------------START SAVE SETTINGS FUNCTION
$url = $url_urbackup."?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'general',
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

$result = (array)json_decode($response);

curl_close($curlid);

$settings = $result;
$array = json_decode(json_encode($settings), true);

$groups = $array['navitems']['groups'];
$clients_settings = $array['navitems']['clients'];

foreach ($clients_settings as $client)
{
    if ($client["name"] == $clientname)
    {
        $id = $client["id"];
        if ($client['groupname'] != "")
        {
            $exist = "true";
        }
        else
        {
            $exist = "false";
        }
    }
    else
        $exist = "false";
}

?>
<br>
<?php
$groupname = "";
$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$id.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine;

if ($exist == "true")
{
    foreach ($clients_settings as $client)
    {
        if ($client["name"] == $clientname)
        {
            $groupname = $client['groupname'];
            $groupid = $client['groupname'];
        }
    }
    $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$id.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine;
    header("Location: ".$url);
}
else
{
    $create_client = xmlrpc_add_client($clientname);
    $insertClientDatabase = xmlrpc_insertNewClient($create_client["new_clientid"], $create_client["new_authkey"]);

    if ($create_client["already_exists"] == "true") 
    {
        foreach ($clients_settings as $client)
        {
            if ($client["name"] == $clientname)
            {
                if ($client['groupname'] == "")
                {
                    $check_client = xmlrpc_enable_client($jidMachine, $create_client["new_clientid"], $create_client["new_authkey"]);
                    ?>
                        <form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup_aftercheck&amp;clientid=<?php echo $client["id"]; ?>&amp;clientname=<?php echo $clientname; ?>&amp;groupname=<?php echo $group['name']; ?>&amp;jidmachine=<?php echo $jidMachine; ?>" method="post">
                            <div>
                                <h3><?php echo _T("Computer name", "urbackup"); ?></h3>
                                <br>
                                <p style="font-weight: bold;"><?php echo "    ".$clientname; ?></p>
                                <br>
                            </div>
                            <div>
                                <h3><?php echo _T("Choose profile to computer", "urbackup"); ?></h3>
                                <select name="group" id="group">
                                    <?php
                                    foreach($groups as $group)
                                    {
                                        echo '<option value="'.$group['id'].'">'.$group['name'].'</option>';
                                    }
                                    ?>
                                </select>
                                <input type="submit" value="Add <?php echo $clientname; ?> on profile">
                            </div>
                        </form>
                    <?php
                }
                else
                {
                    print_r(_T("User already exists" ,"urbackup"));
                    $groupname = $client['groupname'];
                    $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$id.'&clientname='.$clientname.'&groupname='.$groupname.'&jidmachine='.$jidMachine;
                    header("Location: ".$url);
                }
            }
        }
    }
    else
    {
        $check_client = xmlrpc_enable_client($jidMachine, $create_client["new_clientid"], $create_client["new_authkey"]);
        ?>
            <form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup_aftercheck&amp;clientid=<?php echo $create_client["new_clientid"]; ?>&amp;clientname=<?php echo $clientname; ?>&amp;groupname=<?php echo $group['name']; ?>&amp;jidmachine=<?php echo $jidMachine; ?>" method="post">
                <div>
                    <h3><?php echo _T("Computer name", "urbackup"); ?></h3>
                    <br>
                    <p style="font-weight: bold;"><?php echo "    ".$clientname; ?></p>
                    <br>
                </div>
                <div>
                    <h3><?php echo _T("Choose profile to computer", "urbackup"); ?></h3>
                    <select name="group" id="group">
                        <?php
                        foreach($groups as $group)
                        {
                            echo '<option value="'.$group['id'].'">'.$group['name'].'</option>';
                        }
                        ?>
                    </select>
                    <input type="submit" value="Add <?php echo $create_client["new_clientname"]; ?> on profile">
                </div>
            </form>
        <?php
    }
}
?>
