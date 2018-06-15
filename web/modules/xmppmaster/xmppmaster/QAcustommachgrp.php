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

<?php
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");


$machinelist = getRestrictedComputersList(0, -1, array('uuid' => $_GET['uuid']), False);
$machine = $machinelist[$_GET['uuid']][1];
$namemachine = $machine['cn'][0];
$usermachine = $machine['user'][0];

$p = new PageGenerator(_T("Quick Action", 'xmppmaster') . " "._T("Result Machine", 'xmppmaster') . " : $namemachine");
$p->setSideMenu($sidemenu);
$p->display();

if ($_GET['gid'] != ""){
    echo "<h2>". _T("From Group :", 'xmppmaster')." ". $_GET['groupname']."</h2>";
}

$eez = xmlrpc_getCommand_qa_by_cmdid($_GET['cmd_id']);

$startdate = date('Y-m-d H:i:s', $eez['command_start']->timestamp);
echo "<h3>". _T("Start Custom Quick Action:", 'xmppmaster')." ". $startdate."</h3>";
echo "<h3>". _T("User Custom Quick Action:", 'xmppmaster')." ". $eez['command_login']."</h3>";
echo "<h3>". _T("Name Custom Quick Action  :", 'xmppmaster')." ". $eez['command_name']."</h3>";
echo "<h3>". _T("OS Custom Quick Action:", 'xmppmaster')." ". $eez['command_os']."</h3>";

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
echo "<div style=\"text-align: center;\">";
    echo "<h3>command :</h3>";
    echo "<pre>";
    echo  $eez['command_action'];
    echo "</pre>";
echo "</div>";
}

if (count($listmessage)!=0){
    echo "<table>";
        echo "<tr>";
            echo "<th>";
                echo "date";
            echo "</th>";
            echo "<th>";
                echo "type";
            echo "</th>";
            echo "<th>";
                echo "message";
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
    echo  $eez['command_action'];
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
  <input class="btnPrimary"  type="button" value="Retour" onclick="history.go(-1)">
</form>
