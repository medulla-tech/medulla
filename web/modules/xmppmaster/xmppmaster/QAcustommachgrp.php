<?php
/*
 * (c) 2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 *
 * file : xmppmaster/QAcustommachgrp.php
 */
?>
<style>
li.folder a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/folder.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
}

li.folderg a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/folder.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
       filter: grayscale(50%);
       -webkit-filter: grayscale(50%);
       -moz-filter: grayscale(50%);
       opacity:0.5;
}
li.console a {
       padding: 3px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/console.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
}

li.consoleg a {
       padding: 3px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/console.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
       filter: grayscale(50%);
       -webkit-filter: grayscale(50%);
       -moz-filter: grayscale(50%);
       opacity:0.5;
}
li.quick a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/quick.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
}

li.guaca a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/guaca.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
}

li.guacag a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/guaca.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
       filter: grayscale(50%);
       -webkit-filter: grayscale(50%);
       -moz-filter: grayscale(50%);
       opacity:0.5;
}
li.quickg a {
       padding: 0px 0px  5px 22px;
       margin: 0 0px 0 0px;
       background-image: url("modules/base/graph/computers/quick.png");
       background-repeat: no-repeat;
       background-position: left top;
       line-height: 18px;
       text-decoration: none;
       color: #FFF;
       filter: grayscale(50%);
       -webkit-filter: grayscale(50%);
       -moz-filter: grayscale(50%);
       opacity:0.5;
}

</style>
<?php
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

include_once('modules/pulse2/includes/menu_actionaudit.php');
echo "<br><br><br>";

$machinelist = getRestrictedComputersList(0, -1, array('uuid' => $_GET['uuid']), False);
$machine = $machinelist[$_GET['uuid']][1];
$namemachine = $machine['cn'][0];
$usermachine = $machine['user'][0];

$p = new PageGenerator(_T("Quick action on machine", 'xmppmaster')." : $namemachine");
$p->setSideMenu($sidemenu);
$p->display();

$custom_command = xmlrpc_getCommand_qa_by_cmdid($_GET['cmd_id']);
$startdate = timestamp_to_datetime($custom_command['command_start']->timestamp);

echo "<h3>". _T("Name of Quick Action  :", 'xmppmaster')." ". $custom_command['command_name']."</h3>";

$result = "";
$listmessage = array();

$resultAQformachine = xmlrpc_getQAforMachine($_GET['cmd_id'], $_GET['uuid'] );
if (count($resultAQformachine) != 0){
    foreach($resultAQformachine as $message ){
        if ( $message[3] == "result"){
            $result = base64_decode($message[4]);
        }
        else{
            $listmessage[] = $message;
        }
    }
}

if ($result == ""){
    echo "<div style=\"text-align: left;\">";
        echo "<h3>Command :</h3>";
        echo "<pre>";
        echo  $custom_command['command_action'];
        echo "</pre>";
    echo "</div>";
}

if (count($listmessage)!=0){
    echo "<table>";
        echo "<tr>";
            echo "<th>";
                echo "Date";
            echo "</th>";
            echo "<th>";
                echo "Type";
            echo "</th>";
            echo "<th>";
                echo "Message";
            echo "</th>";
        echo "</tr>";

    foreach($listmessage as $message ){
        echo "<tr>";
            echo "<td>";
                echo $message[1];
            echo "</td>";
            echo "<td>";
                echo $message[3];
            echo "</td>";
            echo "<td>";
                echo $message[4];
            echo "</td>";
        echo "</tr>";
    echo "</table>";
    }
}
echo "<div style=\"text-align: center;\">";

if ($result != ""){
    echo "<h3>command :</h3>";
    echo "<pre>";
    echo  $custom_command['command_action'];
    echo "</pre>";
        echo '<textarea rows="25"
                        id="resultat"
                        spellcheck="false"
                        style = "height : 500px;
                                width : 50%;
                                background : black;
                                color : white;
                                FONT-SIZE : 15px;
                                font-family : \'Courier New\', Courier, monospace;
                                border:10px solid ;
                                padding : 15px;
                                border-width:1px;
                                border-radius: 25px;
                                border-color:#FFFF00;
                                box-shadow: 6px 6px 0px #6E6E6E;" >';
            echo $result;
        echo '</textarea>';
}
echo "</div>";
 ?>

<form>
  <input class="btnPrimary"  type="button" value="Back" onclick="history.go(-1)">
</form>
