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
 * file : xmppmaster/deployquickgroup.php
*/

?>



<style type="text/css">
.popup{
    width : 500px
}
input[type="number"] {
   width:40px;
}
input[type="text"] {
   width:100px;
}
</style>
<?
    require_once("modules/base/includes/computers.inc.php");
    if ($_GET['type'] !== 0) $grouptype = "";else $grouptype = "(Imaging)";
     $id  = $_GET['id'];
     $gid = $_GET['gid'];
?>

<?
    $list = getRestrictedComputersList(0, -1, array('gid' => $_GET['gid']), False);
    $count = getRestrictedComputersListLen( array('gid' => $_GET['gid']));
    $nbr_presense = 0;
    foreach($list as $key =>$value){
        if( xmlrpc_getPresenceuuid($key) != 0 ){
            $nbr_presense ++; 
        }
    }
    $nbr_absent = $count - $nbr_presense;
?>


        <div style="width : 600px;">
        <? 
            echo "<h1>Quick Actions group</h1>";
            echo "<h2>groupName ".$grouptype." : ".$_GET['groupname']."</h2>";
            echo "<h3>".$count." machine in group ".$_GET['groupname']."</h3>";
//             echo '<canvas id="myChart" width="100" height="100"></canvas>';
            if ($nbr_presense == 0){
                echo '<h3>There is no machine "turned ON" in this group.</h3>';
            }
            else{
                if ($nbr_absent == 0){
                    echo '<h3>There is no machine "turned OFF" in this group.</h3>';
                }
                else{
                    echo '<h3>machine "turned ON"'.$nbr_presense."/".$count." machines</h3>";
                    echo '<h3>machine "turned OFF"'.$nbr_absent."/".$count." machines</h3>";
                }
            }
        ?>
        <script type="text/javascript">

//         var ctx = document.getElementById("myChart").getContext('2d');
//         data = {
//             datasets: [{
//                 data: [10, 20, 30]
//             }],
// 
//             // These labels appear in the legend and in the tooltips when hovering different arcs
//             labels: [
//                 'Red',
//                 'Yellow',
//                 'Blue'
//             ]
//         };
        /*
        var myPieChart = new Chart(ctx,{
                                        type: 'pie',
                                        data: data,
                                        options: options
                                    });*/

        </script>
            <table style="width : 500px;">
                <tr>
                <?
                    if ($nbr_presense != 0){
                        echo '<td id="shutdown" align="center"><img src="modules/base/graph/computers/shutdown.png" height="70" width="70"> </td>';
                        echo '<td id="reboot" align="center"><img src="modules/base/graph/computers/reboot.png" height="70" width="70" ></td>';
                        echo '<td id="inventory" align="center"><img src="modules/base/graph/computers/inventory0.png" height="70" width="70" ></td>';
                        echo '<td id="vncchangeperms" align="center"><img src="modules/base/graph/computers/remotedesktop.png" height="70" width="70" ></td>';
                        echo '<td id="installkey" align="center"><img src="modules/base/graph/computers/installkeydesktop.png" height="70" width="70" ></td>';

                    }
                    if ($nbr_absent != 0){
                        echo '<td id="wol"><img src="modules/base/graph/computers/wol.png" height="70" width="70" ></td>';
                    }
                ?>
                </tr>
                 <tr>
                 <?
                    if ($nbr_presense != 0){
                        echo '<td><span id="shutdown0">Shutdown</span>
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
                        echo '<td id="reboot0" align="center">Reboot</td>';
                        echo '<td id="inventory0" align="center">Run inventory</td>';
                        echo '<td><span id="vncchangeperms0">Change VNC settings</span>
                                    <form name = "infosvncchangeperms">
                                        <label>
                                            <input type="checkbox" name="askpermission" id = "checkboxvncchangeperms" checked> Ask user approval
                                        </label>
                                    </form></td>';
                        echo '<td id="installkey0" align="center">Installing the ARS public key on the machine agent</td>';
                    }
                    if ($nbr_absent != 0){
                        echo '<td><span id="wol0">Wake on LAN</span>
                            <form name = "infoswolimaging">
                                    <label>
                                        Imaging <input type="checkbox" name="checkboxwol" id = "checkboxwol">
                                    </label>
                                </form></td>';
                    }
                 ?>
                </tr>
            </table>
        </div>
<?php

                $qacomand =array();
                $mm = array();
                // convention les commande de l'user root sont appliquer a tous
                $qacomand = xmlrpc_getlistcommandforuserbyos("root" );
                echo "<table>";
                    echo '<tr>';
                    echo'<td>Custom command</td>
                    <td>
                        <select id="select">';
                        foreach($qacomand['command'] as $tabblecommand){
                            echo '<option value="'.$tabblecommand['customcmd'].'">'.$tabblecommand['namecmd'].'</option>';
                                    $mm[] =  '"'.addslashes($tabblecommand['namecmd']).'": {
                                        "description" : "'.addslashes( $tabblecommand['description'] ).'",
                                        "customcmd" : "'.addslashes($tabblecommand['customcmd']).'",
                                        "os" : "'.addslashes($tabblecommand['os']).'",
                                        "user" : "'.addslashes($tabblecommand['user']).'}';
                                    };
                        echo'</select>
                    </td>
                    <td><input id="buttoncmd" class="btn btn-primary" type=button value="Send custom command"></td>';
                    echo '</tr>';
                echo "</table>";
                echo "<form name='formcmdcustom' id ='formcmdcustom' action='main.php' method='GET' >";
                    foreach ($_GET as $key=>$valu){
                        if ( $key == "mod" || $key == "id" || $key == "type" ) continue;
                        echo "<input type='hidden' id='".$key."'  name ='".$key."' value ='".$valu."'>";
                    }
                    echo "<input type='hidden' id='action'  name ='action' value ='ActionQuickGroup'>";
                    echo "<input type='hidden' id='namecmd'  name ='namecmd' value =''>";
                    echo "<input type='hidden' id='user'  name ='user' value ='root'>";
                    echo "<input type='hidden' id='cmdid'  name ='cmdid' value =''>";
                echo "</form>";
?>

<script type="text/javascript">
   var groupinfo = <? echo json_encode($_GET); ?>

        jQuery(function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
        });
        jQuery('#select').on('change', function() {
            var t = jQuery('#select option:selected').text();
            jQuery('#namecmd').val(t);
        });

        jQuery( '#buttoncmd' ).click(function() {
            groupinfo["namecmd"]=jQuery('#namecmd').val()
            groupinfo["user"]=jQuery('#user').val()
            groupinfo["actionqa"]=jQuery('#action').val()
            groupinfo["groupname"] = jQuery('#groupname').val()
            groupinfo["type"] = jQuery('#type').val()
            jQuery.get( "modules/xmppmaster/xmppmaster/actioncustomquickactiongrp.php", groupinfo)
                .done(function( data ) {
                    jQuery('#cmdid').val(data);
                    jQuery( '#formcmdcustom' ).submit();
                })
        });

        jQuery('#checkboxshutdown').click(function() {
            jQuery("#shutdowninfo").toggle();
        })
    //console.log(groupinfo);

    function wol(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_not_present.length == 0){
            alert("All machines are running")
        }
        else{
                text = "";
                for(var i = 0; i < machine_not_present.length; i++){
                    text = text +  machine_not_present[i] + ", ";
                }
            alert("Wakeonlan on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    function inventory(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];

        if (machine_already_present.length == 0){
            alert("All machines are off\nInventory possible only on running machines")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_already_present[i] + ", ";
                }
            alert("Inventory on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    function reboot(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("No machines are running\nReboot possible only on running machine")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_not_present[i] + ", ";
                }
            alert("Reboot on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    function shutdownfunction(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("All machines are off\nShutdown possible only on running machines")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_already_present[i] + ", ";
                }
            alert("shutdown on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    function vncchangepermsfunction(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("All machines are off\nVNC settings change available only on running machines")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_already_present[i] + ", ";
                }
            alert("VNC settings change on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    function installkey(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("No machines are running\nARS key installation possible only on running machine")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_already_present[i] + ", ";
                }
            alert("ARS key installation on the following machines in progress\n"+text , "" , "alert-info")
        }
    }

    jQuery('#wol,#wol0').unbind().on('click', function(){
        groupinfo['wol'] = jQuery('#checkboxwol').is(':checked'); 
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", groupinfo )
            .done(function( data ) {
                wol(data)
            })
    })

    jQuery('#inventory,#inventory0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", groupinfo )
            .done(function( data ) {
                inventory(data)
            })
    })
    jQuery('#reboot,#reboot0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", groupinfo )
            .done(function( data ) {
                reboot(data)
            })
    })

    jQuery('#installkey,#installkey0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionkeyinstall.php", groupinfo )
            .done(function( data ) {
            //alert(data);
               installkey(data)
            })
    })

    jQuery('#shutdown,#shutdown0').on('click', function(){
        groupinfo['time'] = jQuery('#mytimeshutdown').val()
        groupinfo['msg'] = jQuery('#msgshutdown').val()
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo )
            .done(function( data ) {
                shutdownfunction(data)
            })
    })

    jQuery('#vncchangeperms,#vncchangeperms0').on('click', function(){
        if (jQuery('#checkboxvncchangeperms').is(":checked")){
          groupinfo['askpermission'] = 1
        }
        else {
          groupinfo['askpermission'] = 0
        }
        jQuery.get( "modules/xmppmaster/xmppmaster/actionvncchangeperms.php", groupinfo )
            .done(function( data ) {
                shutdownfunction(data)
            })
    })
</script>
