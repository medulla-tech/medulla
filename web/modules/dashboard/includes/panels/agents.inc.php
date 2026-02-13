<?php
/**
 * (c) 2021 Siveo / http://siveo.net
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
require_once("modules/xmppmaster/includes/xmlrpc.php");

$options = array(
    "class" => "AgentsPanel",
    "id" => "agents",
    "refresh" => 14400,
    "title" => _T("Agents", "dashboard"),
    "enable" => TRUE
);

class AgentsPanel extends Panel {
  function display_content() {
    $result = xmlrpc_get_count_agent_for_dashboard();


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
    echo '<h1>'._T("Machines in Medulla from ".$months[0]." to ".end($months), 'xmppmaster').'</h1>';
    echo <<< RATE
    <div id="agents-graphs"></div>
    <script>
      var datas = $_json;

      lineChart("agents-graphs",{"datas":datas, "config": {"xlabel":true,"delta":"relative", "height":150,"unit":"agents"}})
    </script>
RATE;
// Reset array pointer to end
end($json);
$latest = current($json);
$prev1 = prev($json);
$prev2 = prev($json);
echo '<div id="agents-legend" style="text-align:center;font-size:10px;color:#666;margin-top:8px;">';
  echo $latest['label'].': <strong>'.$latest['y'].'</strong>';
  echo ' &nbsp;|&nbsp; '.$prev1['label'].': <strong>'.$prev1['y'].'</strong>';
  echo ' &nbsp;|&nbsp; '.$prev2['label'].': <strong>'.$prev2['y'].'</strong>';
echo '</div>';
  }
}
