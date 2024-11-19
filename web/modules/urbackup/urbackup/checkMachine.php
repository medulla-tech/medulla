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
$machineid = htmlentities($_GET["UUID"]);

$p = new PageGenerator(_T("Assign profile to computer ".$clientname, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clientAndGroupsAll = xmlrpc_get_clients();

$clients = $clientAndGroupsAll["navitems"]["clients"];
$groups = $clientAndGroupsAll["navitems"]["groups"];

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$ini_array_local = parse_ini_file("/etc/mmc/plugins/urbackup.ini.local");
$username_urbackup = isset($ini_array_local["usernameapi"]) ? $ini_array_local["usernameapi"] : $ini_array["usernameapi"];
$password_urbackup = isset($ini_array_local["passwordapi"]) ? $ini_array_local["passwordapi"] : $ini_array["passwordapi"];
$url_urbackup = isset($ini_array_local["url"]) ? $ini_array_local["url"] : $ini_array["url"];

$id = "";
$auth = "";
$groupid = "";
$groupname = "";

$clientExist = "";
$name_user = "";

if (count($clients) != 0)
{
    foreach ($clients as $client)
    {
        $clientExist = "false";
        $clientHaveProfile = "false";

        if ($client["name"] == $clientname)
        {
            $id = $client["id"];
            $client_info = xmlrpc_get_auth_client($id);
            $auth = $client_info["value"];
            $groupid = $client["group"];
            $groupname = $client["groupname"];

            $clientExist = "true";
            
            if ($groupname != "")
                $clientHaveProfile = "true";
        }
    }
}

?>
<br>
<?php

if ($clientExist = "false") 
{
    $createClient = xmlrpc_add_client($clientname);

    if (!empty($createClient["added_new_client"]) && $createClient["added_new_client"] == 1)
    {
        $id = $createClient["new_clientid"];
        $groupid = "";
        $groupname = "";
        $auth = $createClient["new_authkey"];
    }
}

if ($groupname == "")
{
    $insertClientDatabase = xmlrpc_insertNewClient($id, $auth);

    ?>
    <form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=add_member_togroup_aftercheck&amp;clientid=<?php echo $id; ?>&amp;clientname=<?php echo $clientname; ?>&amp;auth=<?php echo $auth; ?>&amp;groupid=<?php echo $group['id']; ?>&amp;groupname=<?php echo $group['name']; ?>&amp;jidmachine=<?php echo $jidMachine; ?>" method="post">
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
                    if ($group['name'] != "")
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
    $params = [
        "module" => "urbackup",
        "submod" => "urbackup",
        "action" => "list_backups",
        "clientid" => $id,
        "clientname" => $clientname,
        "machineid" =>$machineid,
        "groupid" =>$groupid,
        "groupname" => $groupname,
        "jidmachine" => $jidMachine,
    ];

    $paramsStr = http_build_query($params);
    //User exist and have a profile
    $url = 'main.php?'.$paramsStr;
    header("Location: ".$url);
}

?>
