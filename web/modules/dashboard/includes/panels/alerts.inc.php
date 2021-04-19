<?php

/*
 * (c) 2021 Siveo, http://siveo.net
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
 */
include_once("modules/dashboard/includes/panel.class.php");
include_once("modules/xmppmaster/includes/panel.class.php");
$options = array(
    "class" => "AlertsPanel",
    "id" => "alerts",
    "refresh" => 3600,
    "title" => _T("Alerts", "dashboard"),
);

class AlertsPanel extends Panel {

    function display_content() {
      $result = xmlrpc_get_mon_events(0, 5, "");
      echo '<div id="alertsaccordion">';

      foreach($result['datas'] as $alert){

        $machine = explode('.',$alert['machine_jid'])[0];
        $uuid = $alert['machine_uuid'];
        $params = [
          'cn'=> $machine,
          'objectUUID' => $uuid
      ];
        echo '<h3 class="'.$alert['device_status'].'"><b>'.$alert['rule_comment'].'</b> on machine: <b>'.$machine.'</b></h3>';

        echo '<div>';
        echo '<b>'._T("Status","xmppmaster").'</b> : '.$alert['device_status'].'<br>';
        echo '<b>'._T("Date","xmppmaster").'</b> : '.$alert['mon_machine_date'].'<br>';
        echo '<b>'._T("Evenement","xmppmaster").'</b> : '.$alert['rule_comment'].'<br>';
        echo '<b>'._T("Machine","xmppmaster").'</b> : <a href="'.urlStrRedirect("base/computers/glpitabs", $params).'">'.$machine.'</a><br>';
        echo '</div>';

      }
      echo '</div>';

      ?>
<script>
jQuery(function(){
  jQuery('.warning').css('background-color', 'orange');
  jQuery('.error').css('background-color', 'red');
  jQuery('.ready').css('background-color', 'green');
  jQuery("#alertsaccordion").accordion({
    'collapsible': true,

  });
});
</script>
      <?php
    }

}

?>
