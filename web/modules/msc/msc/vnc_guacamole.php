<?php
/**
 * (c) 2015 siveo, http://www.siveo.net/
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
if(isset($_GET['objectUUID'])){
    $dd = xmlrpc_getGuacamoleRelayServerMachineUuid($_GET['objectUUID']);
}
$url=array();

$ee = xmlrpc_getGuacamoleidforUuid($_GET['objectUUID']);
foreach ($ee as $k){
    $url[$k[0]]=$dd['urlguacamole'].$k[1];
}

 ?>
    <HTML>
        <head>
            <title>Siveo Pulse</title>
            <link href='/mmc/graph/master.css' rel='stylesheet' media='screen' type='text/css' />
        </head>
        <BODY style='background-color: #FFFFFF;'>
        <h1>REMOTE</h1>
            <table id="tablevnc">
                <tr>

                    <!--  <td align="center">
                        <a href="http://www.apple.com/fr/"> <img src="modules/xmppmaster/graph/img/VNCguacamole.png" alt="Mountain View" style="width:104px;height:104px;"></a><br><h1>VNC</h1>
                    </td>
                    -->
                    <td align="center">
                        <a href="<? echo $url['RDP']; ?>" target="blank"> <img src="modules/xmppmaster/graph/img/RDPguacamole.png" alt="Mountain View" style="width:104px;height:104px;"></a><br><h1>RDP</h1>
                    </td>
                    <td align="center">
                        <a href="<? echo $url['SSH']; ?>" target="blank"><img src="modules/xmppmaster/graph/img/SSHguacamole.png" alt="Mountain View" style="width:104px;height:104px;"></a><br><h1>SSH</h1>
                    </td>
                </tr>
            </table>
<?
if ($dd['agenttype'] == "relayserver")
    printf("SERVER");
    else
    printf("COMPUTER");
    echo "<hr>";
    echo "<br>";
    printf("Hostname : %s<br> Platform : %s",$dd['hostname'],$dd['platform']);
    printf("<br>IP : %s/%s<br> Macadress : %s",$dd['ip_xmpp'],$dd['subnetxmpp'],$dd['macadress']);
?>

</BODY>
  </HTML>
<?
 echo "<pre>";
 print_r($_GET['objectUUID']);
 echo "</pre>";
 echo "           </BODY>
            </HTML>
";
?>
