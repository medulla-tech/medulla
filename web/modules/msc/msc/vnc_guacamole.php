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
    $cux[$k[0]] = $k[1];
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
                      $os_up_case = strtoupper($dd["platform"]);
                      if (strpos ($os_up_case, "WINDOW") !== false){
                          $src = 'modules/xmppmaster/graph/img/cmd.png';
                          $title = "CMD";
                          $alt = "Remote cmd View";
                      }
                      else {
                        $src = 'modules/xmppmaster/graph/img/SSHguacamole.png';
                        $title = "SSH";
                        $alt = "Remote ssh View";
                      }
                        echo '<td align="center" id="ssh">
                            <img src="'.$src.'"
                            alt="'.$alt.'"
                            style="width:104px;height:104px;">
                            <br>
                            <h1>'.$title.'</h1>
                        </td>';
                        }
                    if ($clef == "RDP"){
                        echo '<td align="center" id="rdp">
                            <img src="modules/xmppmaster/graph/img/RDPguacamole.png"
                            alt="remote rdp View"
                            style="width:104px;height:104px;">
                            <br>
                            <h1>RDP</h1>
                        </td>';
                        }
                    if ($clef == "VNC"){
                        echo '<td align="center" id="vnc">
                            <img src="modules/xmppmaster/graph/img/VNCguacamole.png"
                            alt="remote vnc View"
                            style="width:104px;height:104px;">
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

var uuid = '<?php echo $_GET['objectUUID']; ?>'
var cn = '<?php echo $_GET['cn']; ?>'

<?
if (isset($url['SSH'])){
    echo "jQuery('#ssh').on('click', function(){
    var ssh_url = '".$url['SSH']."';
    var ssh_cux = '".$cux['SSH']."';";
    echo 'jQuery.get( "modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: ssh_cux, cux_type: "SSH" } )
    .done(function( data ) {
      window.open( ssh_url )
      alert( "The SSH control session opens in a new window" )
    })
});';
};

if (isset($url['RDP'])){
    echo "jQuery('#rdp').on('click', function(){
        var rdp_url = '" . $url['RDP'] ."';
        var rdp_cux = '". $cux['RDP']."';";
    echo '
    jQuery.get( "modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: rdp_cux, cux_type: "RDP" } )
    .done(function( data ) {
      window.open( rdp_url )
      alert( "The RDP control session opens in a new window" )
    })
  });';
};


if (isset($url['VNC'])){
    echo "jQuery('#vnc').on('click', function(){
        var vnc_url = '".$url['VNC']."';
        var vnc_cux = '".$cux['VNC']."';";
    echo '
    jQuery.get( "modules/xmppmaster/xmppmaster/actionreversesshguacamole.php", { uuid: uuid, cn: cn, cux_id: vnc_cux, cux_type: "VNC" } )
    .done(function( data ) {
      window.open( vnc_url )
      alert( "The VNC control session opens in a new window" )
    })
  });';
};

?>

</script>
