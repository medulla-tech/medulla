<?php
/**
 * (c) 2021 Siveo / http://siveo.net
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


include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$options = array(
    "class" => "DeploymentsLaunchedPanel",
    "id" => "deploymentsLaunched",
    "refresh" => 14400,
    "title" => _T("Deployments Launched", "dashboard"),
    "enable" => TRUE
);

class DeploymentsLaunchedPanel extends Panel {
  function display_content() {
    $result = xmlrpc_get_count_total_deploy_for_dashboard();


    $json = [];

    $now = new DateTime("now");
    $months = [$now->format("M-Y")];
    for($i=0; $i<5; $i++){
      $months[] = $now->sub(new DateInterval('P1M'))->format("M-Y");
    }
    $months = array_reverse($months);
    foreach($result as $key=>$value){
      $json[] = ["x"=>$key, "y"=>$value, "label"=>$months[$key]];
    }

    $_json = json_encode($json);
    echo '<h1>'._T("Deployements launched from ".$months[0]." to ".end($months), 'xmppmaster').'</h1>';
    echo <<< RATE
    <div id="deploymentsLaunched-graphs"></div>
    <script>
      var datas = $_json;

      lineChart("deploymentsLaunched-graphs",{"datas":datas, "config": {"xlabel":true,"delta":"relative", "height":150,"unit":"deploy."}})
    </script>
RATE;
echo '<div id="deploymentsLaunched-legend">';
  echo '<ul style="padding-left:15px;">';
    echo '<li>'.end($json)['label'].' : '.current($json)['y'].' depl.</li>';
    echo '<li>'.prev($json)['label'].' : '.current($json)['y'].' depl.</li>';
    echo '<li>'.prev($json)['label'].' : '.current($json)['y'].' depl.</li>';
  echo '</ul>';
echo '</div>';
  }
}
