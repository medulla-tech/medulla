<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse
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

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("List user on profil ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clients = xmlrpc_get_backups_all_client();

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

$clients = $array['navitems']['clients'];
//-----------------------------------END SAVE SETTINGS

?>
<br>
<h2><?php echo _T("Add member to this profile", 'urbackup'); ?></h2>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup&amp;groupname=<?php echo $group_name; ?>&amp;groupid=<?php echo $group_id; ?>" method="post">
    <select name="client">
        <?php
        foreach($clients as $client)
        {
            if ($client['group'] != $group_id)
            {
                echo '<option id="clientid" name="clientid" value="'.$client['id'].'">'.$client['name'].'</option>';
            }
        }
        ?>
    </select>
    <input type="submit" name="subadd" id="subadd" value="Add this member">
</form>
<br>
<br>
<div style="display:flex">
    <div style="padding: 5px;">
        <h3 style="margin-left: 10px; margin-bottom: 5px;"> <?php echo _T("Computer <b>outside</b> the profile","urbackup"); ?></h3>
        <div>
            <?php
            foreach($clients as $client)
            {
                if ($client['group'] == 0)
                {
                    $groupname_client = "";
                }
                else
                {
                    $groupname_client = "(".$client['groupname'].")";
                }
                if ($client['group'] != $group_id)
                {
                    echo "<p value=".$client['id']." style='margin-left: 20px; font-weight: bold; width: 250px; height: 14px;'>".$client['name']." ".$groupname_client."</p>";
                }
            }
            ?>
        </div>
    </div>
    <div style="margin-left: 50px; padding: 5px;">
        <h3 style="margin-left: 10px; margin-bottom: 5px;"><?php echo _T("Computer <b>inside</b> the profile","urbackup"); ?></h3>
        <div>
            <?php
            foreach($clients as $client)
            {
                if ($client['group'] == $group_id)
                {
                    echo "<p value=".$client['id']." style='margin-left: 20px; font-weight: bold; width: 250px; height: 14px;'>".$client['name']."</p>";
                }
            }
            ?>
        </div>
    </div>
</div>
