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
$url = array();
$ee = xmlrpc_getGuacamoleidforUuid($_GET['objectUUID']);
foreach ($ee as $k){
    $cux_id_hex = bin2hex($k[1]).'00'.bin2hex('c').'00'.bin2hex('mysql');
    $cux_id=base64_encode(hex2bin($cux_id_hex));
    $url[$k[0]] = str_replace('@@CUX_ID@@',$cux_id,$dd['urlguacamole']);
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
                <?
                foreach ($url as $clef=>$val){
                    if ($clef == "SSH"){
                        echo '<td align="center">
                            <a href="'.$url['SSH'].'" target="blank" id="ssh">
                            <img src="modules/xmppmaster/graph/img/SSHguacamole.png"
                            alt="remote ssh View"
                            style="width:104px;height:104px;">
                            </a>
                            <br>
                            <h1>SSH</h1>
                        </td>';
                        }
                    if ($clef == "RDP"){
                        echo '<td align="center">
                            <a href="'.$url['RDP'].'" target="blank" id="rdp">
                            <img src="modules/xmppmaster/graph/img/RDPguacamole.png"
                            alt="remote rdp View"
                            style="width:104px;height:104px;">
                            </a>
                            <br>
                            <h1>RDP</h1>
                        </td>';
                        }
                    if ($clef == "VNC"){
                        echo '<td align="center">
                            <a href="'.$url['VNC'].'" target="blank" id="vnc">
                            <img src="modules/xmppmaster/graph/img/VNCguacamole.png"
                            alt="remote rdp View"
                            style="width:104px;height:104px;">
                            </a>
                            <br>
                            <h1>VNC</h1>
                        </td>';
                        }
                }
                ?>
                </tr>
            </table>
<?
if ($dd['agenttype'] == "relayserver")
    printf("SERVER");
    else
    printf("COMPUTER");
    echo "<hr>";
    echo "<br>";
    printf("Hostname : %s<br> Platform : %s<br>architecture : %s<br>", $dd['hostname'], $dd['platform'], $dd['archi']);
    printf("<br>IP : %s/%s<br> Macadress : %s", $dd['ip_xmpp'], $dd['subnetxmpp'], $dd['macaddress']);
?>

</BODY>
  </HTML>
<?
 echo "           </BODY>
            </HTML>
";
?>

<script type="text/javascript">

jQuery('#ssh').on('click', function(){
    alert( "The SSH control session opens in a new window" )
})

jQuery('#rdp').on('click', function(){
    alert( "The RDP control session opens in a new window" )
})

jQuery('#vnc').on('click', function(){
    alert( "The VNC control session opens in a new window" )
})

</script>
