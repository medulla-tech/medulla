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

    <div style="width : 600px;">
        <? 
        echo "<h1>Quick Actions</h1>";
        echo "<h2>Machinec :".$_GET['cn']."</h2>";
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
                }
                else{
                    echo '<td id="wol0" align="center"><img src="modules/base/graph/computers/wol.png" height="70" width="70" ></td>';
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
    </div>
<script type="text/javascript">
   var uuid = <? echo json_encode($_GET); ?>

    jQuery('#wol').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", uuid )
            .done(function( data ) {
                alert( "wakeonlan to machine : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#inventory').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", uuid )
            .done(function( data ) {
                alert( "inventory : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#reboot').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", uuid )
            .done(function( data ) {
                alert( "reboot : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#shutdown').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", uuid )
            .done(function( data ) {
                alert( "shutdown : to machine" + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#wol0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionwakeonlan.php", uuid )
            .done(function( data ) {
                alert( "wakeonlan to machine : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#inventory0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actioninventory.php", uuid )
            .done(function( data ) {
                alert( "inventory : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

    jQuery('#reboot0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", uuid )
            .done(function( data ) {
                alert( "reboot : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]")
            })
    })

    jQuery('#shutdown0').on('click', function(){
        jQuery.get( "modules/xmppmaster/xmppmaster/actionshutdown.php", uuid )
            .done(function( data ) {
                alert( "shutdown : " + uuid['cn'] + " in entity [" + uuid['entity'] + "]" )
            })
    })

</script>
