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
    "class" => "SuccessRatePanel",
    "id" => "successRate",
    "refresh" => 14400,
    "title" => _T("Success Rate", "dashboard"),
    "enable" => TRUE
);

class SuccessRatePanel extends Panel {
  function display_content() {
    $result = xmlrpc_get_count_success_rate_for_dashboard();
    $json = [];

    foreach($result as $key=>$value){
      $newKey = ($key+1)." w.";
      $json[] = ["label"=>$newKey, "value"=>number_format($value, 1)];
    }
    $json = json_encode($json);
    echo '<h1>'._T('Deployment success rates for the past 6 weeks','dashboard').'</h1>';
    echo <<< RATE

    <div id="successRate-graphs"></div>
    <script>
      datas = {"datas": $json};
      barchart("successRate-graphs", datas);
    </script>
RATE;
  }
}
