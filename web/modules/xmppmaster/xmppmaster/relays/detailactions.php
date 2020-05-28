<?php
/*
 * (c) 2015-2020 siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

$p = new PageGenerator(_T("Detail Actions", 'glpi'));
$p->display();
if(isset($_GET['jid']))
{
  $jid = $_GET['jid'];
  $agenttype = '';
  if(isset($_GET['agenttype']))
    $agenttype= htmlentities($_GET['agenttype']);
  echo '<table>';
  echo '<tr>';
    echo '<th>Reboot</th>';
    echo '<th>Process</th>';
    echo '<th>Disk Usage</th>';
    echo '<th>Agent Version</th>';
    echo '<th>Netstat</th>';
    echo '<th>Console</th>';
  echo '</tr>';

  echo '<tr>';
  echo '<td id="reboot" align="center"><img src="modules/base/graph/computers/reboot.png" height="70" width="70"></td>';
  echo '<td id="process" align="center"><a href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'clone_ps_aux']).'"><img src="modules/base/graph/navbar/process.png" height="70" width="70"></a></td>';
  echo '<td id="diskusage" align="center"><a href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'disk_usage']).'"><img src="modules/base/graph/navbar/diskusage.png" height="70" width="70"></a></td>';
  echo '<td id="agentversion" align="center"><a href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'agentinfos']).'"><img src="modules/base/graph/navbar/information.png" height="70" width="70"></a></td>';
  echo '<td id="netstat" align="center"><a href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'netstat']).'"><img src="modules/base/graph/computers/network.png" height="70" width="70"></a></td>';
  echo '<td id="console" align="center"><a href="'.urlStrRedirect("xmppmaster/xmppmaster/consolexmpp", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'agentinfos']).'"><img src="modules/base/graph/computers/console.jpg" height="70" width="70"></a></td>';
  echo '</tr>';
  echo '</table>';
}

?>

<script>
var datas = <? echo json_encode($_GET); ?>;
jQuery('#reboot').on('click', function(){

    jQuery.get( "modules/xmppmaster/xmppmaster/actionrestart.php", datas )
        .done(function( data ) {
            alert( "reboot : " + datas['jid'] , "" , "alert-info" );
        })
})
</script>
