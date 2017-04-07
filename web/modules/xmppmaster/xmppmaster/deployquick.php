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

    <HTML>
        <head>
            <title>Siveo Pulse</title>
            <link href='/mmc/graph/master.css' rel='stylesheet' media='screen' type='text/css' />
        </head>
        <BODY style='background-color: #FFFFFF;'>
        <? 
        echo "<h1>Quick Actions</h1>";
        echo "<h2>Machinec :".$_GET['cn']."</h2>";
        echo "<h2>Os : ".$_GET['os']."</h2>";
        echo "<h2>Entity : ".$_GET['entity']."</h2>";
        //objectUUID
        ?>
            <table style="width : 500px;">
                <tr> 
                <?
                    if ($_GET['presencemachinexmpp']){
                        echo '<td align="center">ICI Icone</td>';
                        echo '<td align="center">ICI Icone</td>';
                        echo '<td align="center">ICI Icone</td>';
                    }
                    else{
                        echo '<td align="center">ICI Icone</td>';
                    }
                 ?>
                </tr>
                 <tr>
                 <?
                 if ($_GET['presencemachinexmpp']){
                    echo '<td id="shutdown" align="center">Shutdown</td>';
                    echo '<td id="reboot" align="center">Reboot</td>';
                    echo '<td id="inventory" align="center">Run inventory</td>';
                 }
                 else{
                    echo '<td id="wol" align="center">Wake on LAN</td>';
                }
                 ?>

                </tr>
            </table>

<script type="text/javascript">
   var uuid = <? echo json_encode($_GET); ?>

    jQuery('#wol').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", uuid )
            .done(function( data ) {
                alert( "wakeonlan to machine : " + uuid['cn'] + " in " + uuid['entity'] )
            })
    })

    jQuery('#inventory').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", uuid )
            .done(function( data ) {
                alert( "inventory : " + uuid['cn'] + " in " + uuid['entity'] )
            })
    })

    jQuery('#reboot').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", uuid )
            .done(function( data ) {
                alert( "reboot : " + uuid['cn'] + " in " + uuid['entity'] )
            })
    })

    jQuery('#shutdown').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", uuid )
            .done(function( data ) {
                alert( "shutdown : " + uuid['cn'] + " in " + uuid['entity'] )
            })
    })
</script>


</BODY>
  </HTML>

<?
 echo "<pre>";
// jQuery.get( "actionwakeonlan.php", uuid );
 echo "</pre>";
?>
