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
// <!--<script src="jsframework/lib/Chart.min.js" type="text/javascript"></script>-->
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
     //echo json_encode($_GET);
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
                                        <br>
                                        Message shutdown<br>
                                        <input type="text" id="msgshutdown"  value="Shutdown from admin">
                                    </div>
                                </form></td>';
                        echo '<td id="reboot0" align="center">Reboot</td>';
                        echo '<td id="inventory0" align="center">Run inventory</td>';
                    }
                    if ($nbr_absent != 0){
                        echo '<td id="wol0">Wake on LAN</td>';
                    }
                 ?>
                </tr>
            </table>
        </div>

<script type="text/javascript">
   var groupinfo = <? echo json_encode($_GET); ?>


jQuery('#checkboxshutdown').click(function() {
    jQuery("#shutdowninfo").toggle();
})
//     if( jQuery('input[name=checkboxshutdown]').is(':checked') ){
//         jQuery("#wolinfo").hide(500);
//     }
//     else{
//         jQuery("#wolinfo").show(500);
//     }

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

    function shutdownfunction(data){
        uuid = data[0];
        cn = data[1];
        presence = data[2];
        machine_already_present = data[3];
        machine_not_present = data[4];
        if (machine_already_present.length == 0){
            alert("All machines are off\nshutdown only on running machines")
        }
        else{
                text = "";
                for(var i = 0; i < machine_already_present.length; i++){
                    text = text +  machine_already_present[i] + ", ";
                }
            alert("shutdown sur les machines suivante en cours\n"+text)
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
        //         val = jQuery.param({'time' : jQuery('#mytimeshutdown').val(), 'msg' : jQuery('#msgshutdown').val()})
        groupinfo['time'] = jQuery('#mytimeshutdown').val()
        groupinfo['msg'] = jQuery('#msgshutdown').val()
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo )
            .done(function( data ) {
                shutdownfunction(data)
            })
    })

    jQuery('#shutdown0').on('click', function(){
        groupinfo['time'] = jQuery('#mytimeshutdown').val()
        groupinfo['msg'] = jQuery('#msgshutdown').val()
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", groupinfo )
            .done(function( data ) {
                shutdownfunction(data)
            })
    })
</script>
