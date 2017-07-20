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

?>
<style type="text/css">
.popup{
    width : 500px
}
</style>
<?
    if ($_GET['type'] !== 0) $grouptype = "";else $grouptype = "(Imaging)";
     $id  = $_GET['id'];
     $gid = $_GET['gid'];
     //echo json_encode($_GET);
?>
        <div style="width : 600px;">
        <? 
        echo "<h1>Quick Actions group</h1>";
        echo "<h2>groupName ".$grouptype." : ".$_GET['groupname']."</h2>";
        ?>

            <table style="width : 500px;">
                <tr> 
                <?
                    echo '<td id="shutdown" align="center"><img src="modules/base/graph/computers/shutdown.png" height="70" width="70"> </td>';
                    echo '<td id="reboot" align="center"><img src="modules/base/graph/computers/reboot.png" height="70" width="70" ></td>';
                    echo '<td id="inventory" align="center"><img src="modules/base/graph/computers/inventory0.png" height="70" width="70" ></td>';
                    echo '<td id="wol" align="center"><img src="modules/base/graph/computers/wol.png" height="70" width="70" ></td>';
                 ?>
                </tr>
                 <tr>
                 <?
                    echo '<td id="shutdown0" align="center">Shutdown</td>';
                    echo '<td id="reboot0" align="center">Reboot</td>';
                    echo '<td id="inventory0" align="center">Run inventory</td>';
                    echo '<td id="wol0" align="center">Wake on LAN</td>';
                 ?>
                </tr>
            </table>
        </div>
<script type="text/javascript">


   var groupinfo = <? echo json_encode($_GET); ?>

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
            alert("Wakeonlan on extinct machines in progress\n"+text)
        }
    }

    function inventory(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];

        if (machine_already_present.length == 0){
            alert("All machines are off\nInventory only on running machines")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_not_present[i] + ", ";
                }
            alert("Inventory on the following machines in progress\n"+text)
        }
    }

    function reboot(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("No machines are running\nRebbot only on running machine")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_not_present[i] + ", ";
                }
            alert("Reboot on the following machines in progress\n"+text)
        }
    }

    function shutdown(){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("No machines are running\nShutdown only on running machine")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_not_present[i] + ", ";
                }
            alert("on the following machines in progress\n"+text)
        }
    }

    jQuery('#wol').unbind().on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", groupinfo )
            .done(function( data ) {
                wol(data)
            })
    })

    jQuery('#wol0').unbind().on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", groupinfo )
            .done(function( data ) {
                wol(data)
            })
    })

    jQuery('#inventory').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", groupinfo )
            .done(function( data ) {
                inventory(data)
            })
    })

    jQuery('#inventory0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", groupinfo )
            .done(function( data ) {
                inventory(data)
            })
    })

    jQuery('#reboot').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", groupinfo )
            .done(function( data ) {
                reboot(data)
            })
    })

    jQuery('#reboot0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", groupinfo )
            .done(function( data ) {
                reboot(data)
            })
    })

    jQuery('#shutdown').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo )
            .done(function( data ) {
                shutdown(data)
            })
    })

    jQuery('#shutdown0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo )
            .done(function( data ) {
                shutdown(data)
            })
    })
</script>
