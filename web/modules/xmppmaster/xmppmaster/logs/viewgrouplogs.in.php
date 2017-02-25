<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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

require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
?>
<?
require_once("modules/dyngroup/includes/includes.php");

$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment logs for group",'xmppmaster')." ". $group->getName());
$p->setSideMenu($sidemenu);
$p->display();
$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");

if ($info['len'] != 0){
    $uuid=$info['objectdeploy'][0]['inventoryuuid'];
        $state=$info['objectdeploy'][0]['state'];
        $start=get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
        $result=$info['objectdeploy'][0]['result'];
        $resultatdeploy =json_decode($result, true);
        $host=$info['objectdeploy'][0]['host'];
        $jidmachine=$info['objectdeploy'][0]['jidmachine'];
        $jid_relay=$info['objectdeploy'][0]['jid_relay'];

        $datestart =  date("Y-m-d H:i:s", $start);
        echo "Start deployment :".$datestart;// [".$infodeploy['len'] ." steps] "


       if (isset($resultatdeploy['descriptor']['info'])){
        echo "<br>";
        echo "<h2>Package</h2>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
                echo "<thead>";
                    echo "<tr>";
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Name</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Software</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Version</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Description</span>';
                        echo '</td>';
                    echo "</tr>";
                echo "</thead>";
                echo "<tbody>";
                    echo "<tr>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['description'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['name'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['software'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['version'];
                        echo "</td>";
                    echo "</tr>";
                echo "</tbody>";
            echo "</table>";
            echo '<br>';

      }
}
else{
echo '
    <form id="formgroup" action="'.$_SERVER['PHP_SELF'].'" METHODE="GET" >
        <input type="hidden" name="tab" value ="'.$tab.'" >
        <input type="hidden" name="gid" value ="'.$gid.'" >
        <input type="hidden" name="cmd_id" value ="'.$cmd_id.'" >
        <input type="hidden" name="login" value ="'.$login.'" >
        <input type="hidden" name="action" value ="viewlogs" >
        <input type="hidden" name="module" value ="xmppmaster" >
        <input type="hidden" name="submod" value ="xmppmaster" >
    </form>';

echo'
            <script type="text/javascript">
            setTimeout(refresh, 10000);
            function  refresh(){
               jQuery( "#formgroup" ).submit();
            }
        </script>
        ';
}
$group->prettyDisplay();

?>

<style>
li.remove_machine a {
        padding: 1px 3px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("img/common/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>
