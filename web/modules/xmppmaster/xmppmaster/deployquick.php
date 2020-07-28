<?php
/*
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
 *
 * file deployquick.php
*/

require_once("modules/xmppmaster/includes/xmlrpc.php");


?>
<style type="text/css">
    .popup{
        width : 500px
    }
</style>

    <div style="width : 600px;">
        <?
        if(!isset($_GET['os']))
        {
          if(isset($_GET["objectUUID"]))
          {
            $machine = xmlrpc_getMachinefromuuid($_GET["objectUUID"]);
            $_GET["os"] = $machine["platform"];
          }
        }

        echo "<h1>Quick Actions</h1>";
        echo "<h2>Machine :".$_GET['cn']."</h2>";
        echo "<h2>Os : ".$_GET['os']."</h2>";
        echo "<h2>Entity : ".$_GET['entity']."</h2>";
        ?>
        <table style="width : 500px;">
            <tr>
            <?
                if ($_GET['presencemachinexmpp']){
                    echo '<td id="shutdown0" align="center"><img src="modules/base/graph/computers/shutdown.png" height="70" width="70"> </td>';
                    echo '<td id="reboot0" align="center"><img src="modules/base/graph/computers/reboot.png" height="70" width="70" ></td>';
                    echo '<td id="inventory0" align="center"><img src="modules/base/graph/computers/inventory0.png" height="70" width="70" ></td>';
                    echo '<td id="vncchangeperms0" align="center"><img src="modules/base/graph/computers/remotedesktop.png" height="70" width="70" ></td>';
                    echo '<td id="installkey0" align="center"><img src="modules/base/graph/computers/installkeydesktop.png" height="70" width="70" ></td>';
                }
                else{
                    echo '<td id="wol0" align="center"><img src="modules/base/graph/computers/wol.png" height="70" width="70" ></td>';
                }
                ?>
            </tr>
                <tr>
                <?
                if ($_GET['presencemachinexmpp']){
                    echo '<td><span id="shutdown">Shutdown</span>
                                <form name = "infosshutdown">
                                    <label>
                                        options <input type="checkbox" name="checkboxshutdown" id = "checkboxshutdown">
                                    </label>
                                    <div id="shutdowninfo" style="display : none">
                                        time before Shutdown
                                        <input type="number" id="mytimeshutdown"  value ="60" name="quantity" min="0" max="120" size="2" >
                                        Message shutdown<br>
                                        <input type="text" id="msgshutdown"  value="Shutdown from admin">
                                    </div>
                                </form></td>';
                    echo '<td id="reboot" align="center">Reboot</td>';
                    echo '<td id="inventory" align="center">Run inventory</td>';
                    echo '<td><span id="vncchangeperms">Change VNC settings</span>
                                <form name = "infosvncchangeperms">
                                    <label>
                                        <input type="checkbox" name="askpermission" id = "checkboxvncchangeperms" checked> Ask user approval
                                    </label>
                                </form></td>';
                    echo '<td id="installkey" align="center">Installing the ARS public key on the machine agent</td>';
                }
                else{
                    echo '<td align="center"><span id="wol">Wake on LAN</span>
                            <form name = "infoswolimaging">
                                    <label>
                                        Imaging <input type="checkbox" name="checkboxwol" id = "checkboxwol">
                                    </label>
                                </form></td>';
                }
                ?>
            </tr>
            </table>
            <?php
            if ($_GET['presencemachinexmpp']){
                $qacomand =array();
                $mm = array();
                $os_up_case = strtoupper ($_GET['os']);
                if ($_GET['presencemachinexmpp']){
                    if (strpos ($os_up_case, "WINDOW") !== false){
                        $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "windows" );
                    }
                    else{
                        if ((strpos ($os_up_case, "LINUX") | strpos ($os_up_case, "UBUNTU")) !== false){
                            $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "linux" );
                        }
                        else{
                            if (strpos ($os_up_case, "MACOS") !== false){
                                $qacomand = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], "macos" );
                            }
                        }
                    }
                }
                echo "<table>";
                    echo '<tr>';
                    echo'<td>Custom command</td>
                    <td>
                        <select id="select">';
                        foreach($qacomand['command'] as $tabblecommand){
                            $tabblecommand['customcmd'] = preg_replace('/\r?\n|\r/',' ', $tabblecommand['customcmd']);
                            $tabblecommand['customcmd'] = trim ( $tabblecommand['customcmd'] , " \t\n\r");
                            echo '<option value="'.$tabblecommand['customcmd'].'">'.$tabblecommand['namecmd'].'</option>';
                                    $mm[] =  "'".addslashes($tabblecommand['namecmd'])."': {
                                        'description' : '".addslashes( $tabblecommand['description'] )."',
                                        'customcmd' : '".addslashes($tabblecommand['customcmd'])."',
                                        'os' : '".addslashes($tabblecommand['os'])."',
                                        'user' : '".addslashes($tabblecommand['user'])."'}";
                                    };
                        echo'</select>
                    </td>
                    <td><input id="buttoncmd" class="btn btn-primary" type=button value="Send custom command"></td>';
                    echo '</tr>';
                echo "</table>";
                echo "<form name='formcmdcustom' id ='formcmdcustom' action='main.php' method='GET' >";
                echo "<input type=hidden name ='module' value ='xmppmaster'>";
                echo "<input type=hidden name ='submod' value ='xmppmaster'>";
                foreach ($_GET as $key=>$valu){
                    if($key == "displayName" ||
                        $key == 'owner_realname' ||
                        $key == 'owner_firstname'||
                        $key == 'mod'
                    ){
                        continue;
                    }
                    if($key == "action"){
                        echo "<input type='hidden' name ='action' value ='ActionQuickconsole'>";
                    }
                    else{
                        echo "<input type='hidden' name ='".$key."' value ='".$valu."'>";
                    }
                }
                echo "<input id='namecmd' type=hidden name ='namecmd' value =''>";
                echo "<input id='customcmd' type=hidden name ='customcmd' value =''>";
                echo "<input id='description' type=hidden name ='description' value =''>";
                echo "<input id='os' type=hidden name ='os' value =''>";
                echo "<input id='user' type=hidden name ='user' value =''>";
                echo "</form>";
            }

$objectUUID = (isset($_GET['objectUUID'])) ? $_GET['objectUUID'] : '';
$cn = (isset($_GET['cn'])) ? $_GET['cn'] : '';
$type = (isset($_GET['type'])) ? $_GET['type'] : '';
$owner_realname = (isset($_GET['owner_realname'])) ? $_GET['owner_realname'] : '';
$entity = (isset($_GET['entity'])) ? $_GET['entity'] : '';
$owner = (isset($_GET['owner'])) ? $_GET['owner'] : '';
$owner_firstname = (isset($_GET['owner_firstname'])) ? $_GET['owner_firstname'] : '';
$presencemachinexmpp = (isset($_GET['presencemachinexmpp'])) ? $_GET['presencemachinexmpp'] : '';
$vnctype = (isset($_GET['vnctype'])) ? $_GET['vnctype'] : '';
$mod = (isset($_GET['mod'])) ? $_GET['mod'] : '';
$user = (isset($_GET['user'])) ? $_GET['user'] : '';

        echo "<form name='formmonitoring' id ='formmonitoring' action='main.php' method='GET' >";
            echo "<input type= 'hidden' name = 'module' value ='xmppmaster'>";
            echo "<input type= 'hidden' name = 'submod' value ='xmppmaster'>";
            echo "<input type= 'hidden' name = 'action' value ='xmppMonitoring'>";
            echo "<input type= 'hidden' name = 'UUID' value='".$objectUUID."'>";
            echo "<input type= 'hidden' name = 'cn' value='".$cn."'>";
            echo "<input type= 'hidden' name = 'type' value='".$type."'>";
            echo "<input type= 'hidden' name = 'owner_realname' value='".$owner_realname ."'>";
            echo "<input type= 'hidden' name = 'entity' value='".$entity."'>";
            echo "<input type= 'hidden' name = 'owner' value='".$owner."'>";
            echo "<input type= 'hidden' name = 'user' value='".$_GET['user']."'>";
            echo "<input type= 'hidden' name = 'owner_firstname' value='".$owner_firstname."'>";
            echo "<input type= 'hidden' name = 'os' value='".$_GET['os']."'>";
            echo "<input type= 'hidden' name = 'presencemachinexmpp' value='".$presencemachinexmpp."'>";
            echo "<input type= 'hidden' name = 'vnctype' value='".$vnctype."'>";
            echo "<input type= 'hidden' name = 'mod' value='".$mod."'>";
            echo "<input id='informationmonitor' type= 'hidden' name = 'information' value=''>";
            echo "<input id='args' type= 'hidden' name = 'args' value=''>";
            echo "<input id='kwargs' type= 'hidden' name = 'kwargs' value=''>";
        echo '</form>';

        if ($_GET['presencemachinexmpp']){
            //echo "<h2>Status Machine :".$_GET['cn']."</h2>";
            echo "<table>";
            echo '<tr>';
//                 echo '<td id="battery" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//                 $pos1 = stripos($_GET['os'], "win");
//                 if ($pos1 !== false) {
//                     echo '<td id="winservices" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//                 }
                echo '<td id="clone_ps_aux" align="center"><img src="modules/base/graph/navbar/process.png" height="45" width="45"> </td>';
                 echo '<td id="disk_usage" align="center"><img src="modules/base/graph/navbar/diskusage.png" height="45" width="45"> </td>';
//                 echo '<td id="sensors_fans" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//                 echo '<td id="mmemory" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//                 echo '<td id="ifconfig" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//
//                echo '<td id="cpu_num" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//
//                 echo '<td id="netstat" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
//                 echo '<td id="cputimes" align="center"><img src="modules/base/graph/navbar/load_hl.png" height="45" width="45"> </td>';
                echo '<td id="agentinfo" align="center"><img src="modules/base/graph/navbar/information.png" height="45" width="45"> </td>';
            echo "</tr>";
            echo '<tr>';
//                 echo '<td id="battery0" align="center">battery </td>';
//                 $pos1 = stripos($_GET['os'], "win");
//                 if ($pos1 !== false) {
//                     echo '<td id="winservices0" align="center">win services </td>';
//                 }
                   echo '<td id="clone_ps_aux0" align="center">show process list</td>';
                  echo '<td id="disk_usage0" align="center">disk usage </td>';
//                 echo '<td id="sensors_fans0" align="center">sensors_fans</td>';
//                 echo '<td id="mmemory0" align="center">memory</td>';
//                 echo '<td id="ifconfig0" align="center">if config</td>';
//
//                 echo '<td id="cpu_num0" align="center">cpu_num</td>';
//
//                 echo '<td id="netstat0" align="center">netstat</td>';
//                 echo '<td id="cputimes0" align="center">cpu times</td>';
                echo '<td id="agentinfo0" align="center">Agent details</td>';
            echo "</tr>";
            echo "</table>";
        }
             ?>
    </div>
<script type="text/javascript">
    <?
     if ($_GET['presencemachinexmpp']){
        echo 'var myObject = {';
            echo implode(",", $mm);
            echo '};';
        echo"
        jQuery(function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
            jQuery('#customcmd').val(myObject[t].customcmd);
            jQuery('#description').val(myObject[t].description);
            jQuery('#os').val(myObject[t].os);
            jQuery('#user').val(myObject[t].user);
        });

        jQuery( '#buttoncmd' ).click(function() {
            jQuery( '#formcmdcustom' ).submit();
        });

        jQuery('#select').on('change', function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
            jQuery('#customcmd').val(myObject[t].customcmd);
            jQuery('#description').val(myObject[t].description);
            jQuery('#os').val(myObject[t].os);
            jQuery('#user').val(myObject[t].user);
        });
    ";
    }
    ?>
   var uuid = <? echo json_encode($_GET); ?>;
   <?php
        if ($_GET['presencemachinexmpp']){
            echo"
                jQuery('#battery, #battery0').click(function() {
                    jQuery('#informationmonitor').val('battery');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#winservices, #winservices0').click(function() {
                    jQuery('#informationmonitor').val('winservices');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#clone_ps_aux, #clone_ps_aux0').click(function() {
                    jQuery('#informationmonitor').val('clone_ps_aux');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#disk_usage, #disk_usage0').click(function() {
                    jQuery('#informationmonitor').val('disk_usage');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#sensors_fans, #sensors_fans0').click(function() {
                    jQuery('#informationmonitor').val('sensors_fans');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#mmemory, #mmemory0').click(function() {
                    jQuery('#informationmonitor').val('mmemory');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#ifconfig, #ifconfig0').click(function() {
                    jQuery('#informationmonitor').val('ifconfig');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#cpu_num, #cpu_num0').click(function() {
                    jQuery('#informationmonitor').val('cpu_num');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#netstat, #netstat0').click(function() {
                    jQuery('#informationmonitor').val('netstat');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#cputimes, #cputimes0').click(function() {
                    jQuery('#informationmonitor').val('cputimes');
                    jQuery('#args').val('');
                    jQuery('#kwargs').val('{\"percpu\" : true}');
                    jQuery( '#formmonitoring' ).submit();
                })
                jQuery('#agentinfo, #agentinfo0').click(function() {
                    jQuery('#informationmonitor').val('agentinfos');
                    jQuery( '#formmonitoring' ).submit();
                })
                ";
        };
    ?>
    jQuery('#checkboxshutdown').click(function() {
        jQuery('#shutdowninfo').toggle();
    })

    jQuery('#wol, #wol0').on('click', function(){
        uuid['wol'] = jQuery('#checkboxwol').is(':checked');
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", uuid )
            .done(function( data ) {
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "wakeonlan to machine : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert( "wakeonlan to machine : " + uuid['cn'] , "" , "alert-info" )
                }
            })
    })

    jQuery('#inventory, #inventory0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", uuid )
            .done(function( data ) {
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "inventory : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert( "inventory : " + uuid['cn'] , "" , "alert-info" )
                }
            })
    })

    jQuery('#reboot, #reboot0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", uuid )
            .done(function( data ) {
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "reboot : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert( "reboot : " + uuid['cn'] , "" , "alert-info" )
                }
            })
    })

    jQuery('#shutdown, #shutdown0').on('click', function(){
        uuid['time'] = jQuery('#mytimeshutdown').val()
        uuid['msg']  = jQuery('#msgshutdown').val()
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", uuid )
            .done(function( data ) {
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "shutdown : to machine" + uuid['cn'] + " in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert( "shutdown : to machine" + uuid['cn'] , "" , "alert-info" )
                }
            })
    })

    jQuery('#vncchangeperms, #vncchangeperms0').on('click', function(){
        if (jQuery('#checkboxvncchangeperms').is(":checked")){
            uuid['askpermission'] = 1
        }
        else {
            uuid['askpermission'] = 0
        }
        jQuery.get( "modules/xmppmaster/xmppmaster/actionvncchangeperms.php", uuid )
            .done(function( data ) {
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "VNC settings change : to machine" + uuid['cn'] + " in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert( "VNC settings change : to machine" + uuid['cn'] , "" , "alert-info" )
                }
            })
    })

    jQuery('#installkey, #installkey0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionkeyinstall.php", uuid )
            .done(function( data ) {
                var obj = jQuery.parseJSON(data);
                if (typeof(uuid['entity'] ) != "undefined"){
                    alert( "Install key Pub ARS [" + obj.groupdeploy + "] on AM [" + obj.hostname +"] " + "in entity [" + uuid['entity'] + "]" , "" , "alert-info" )
                }
                else{
                    alert("Install key Pub ARS [" + obj.groupdeploy + "] on AM [" + obj.hostname +"] " , "" , "alert-info" )
                }
            })
    })

</script>
