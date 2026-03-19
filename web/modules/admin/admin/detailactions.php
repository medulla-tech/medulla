<?php
/*
 * (c) 2020 siveo, http://www.siveo.net/
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
 * file detailactions.php
*/

require_once("modules/xmppmaster/includes/xmlrpc.php");

if(isset($_GET['jid']))
{
  $jid = $_GET['jid'];
  $agenttype = '';
  if(isset($_GET['agenttype']))
    $agenttype= htmlentities($_GET['agenttype']);

  echo '<div class="quick-actions-popup">';
  echo '<h1>' . _T("Detail Actions", 'glpi') . '</h1>';

  // Actions section
  echo '<div class="actions-section">';
  echo '<div class="actions-grid">';
  echo '<div class="action-item" id="reboot"><img src="img/actions/restart.svg" width="50" height="50"><span>'._T("Reboot", "xmppmaster").'</span></div>';
  echo '<a class="action-item" href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'clone_ps_aux']).'"><img src="img/actions/process.svg" width="50" height="50"><span>'._T("Process", "xmppmaster").'</span></a>';
  echo '<a class="action-item" href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'disk_usage']).'"><img src="img/actions/disk.svg" width="50" height="50"><span>'._T("Disk usage", "xmppmaster").'</span></a>';
  echo '<a class="action-item" href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'agentinfos']).'"><img src="img/actions/info.svg" width="50" height="50"><span>'._T("Agent details", "xmppmaster").'</span></a>';
  echo '<a class="action-item" href="'.urlStrRedirect("xmppmaster/xmppmaster/xmppMonitoring", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'netstat']).'"><img src="img/actions/network.svg" width="50" height="50"><span>'._T("Netstat", "xmppmaster").'</span></a>';
  echo '<a class="action-item" href="'.urlStrRedirect("xmppmaster/xmppmaster/consolexmpp", ['jid'=>$jid, 'agenttype'=>$agenttype,'information'=>'agentinfos']).'"><img src="img/actions/console.svg" width="50" height="50"><span>'._T("Console", "xmppmaster").'</span></a>';
  echo '</div>';
  echo '</div>';

  // Custom command section
  $qalist = xmlrpc_get_qa_for_relays($_SESSION['login']);
  echo '<div class="custom-command-section">';
  echo '<h3>'._T("Custom command", "xmppmaster").'</h3>';
  echo '<form action="'.urlStrRedirect("admin/admin/qalaunched").'" method="post">';
  echo '<div class="command-row">';
  echo '<select name="qa_relay_id">';
  foreach($qalist as $qa){
    echo '<option value="'.$qa['id'].'" >'.htmlspecialchars($qa['description']).'</option>';
  }
  echo '</select>';
  echo '<input type="hidden" name="jid" value="'.htmlspecialchars($jid).'"/>';
  echo '<input type="hidden" name="launch_relay_qa" value="'.htmlspecialchars($jid).'"/>';
  echo '<input class="btnPrimary" type="submit" value="'._T("Send custom command", "xmppmaster").'">';
  echo '</div>';
  echo '</form>';
  echo '</div>';

  echo '</div>';
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
