<?php
/*
 * (c) 2016 siveo, http://www.siveo.net/
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

require_once("modules/dashboard/includes/panel.class.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");

$options = array(
    "class" => "ComputersOnlinePanel",
    "id" => "computersOnline",
    "refresh" => 300,
    "title" => _T("Machines Online", "dashboard"),
    "enable" => true,
);

class ComputersOnlinePanel extends Panel {

    function display_content() {
        $urlRedirect = urlStrRedirect("base/computers/createMachinesStaticGroup");
        $total_machines = getSimpleComputerCount();
        $machines_online = xmlrpc_getCountOnlineMachine();

        if($total_machines >= $machines_online) {
          $machines_offline = $total_machines - $machines_online;
          $online_text = _T("Machines online : ","dashboard");
          $offline_text = _T("Machines offline : ","dashboard");

          echo <<< ONLINE
          <script>
            var onlineDatas = [
              {"label": "$online_text", "value":$machines_online, "href":"$urlRedirect&machines=online"},
              {'label': '$offline_text', 'value': $machines_offline, "href": "$urlRedirect&machines=offline"}
            ];

            donut("computersOnline",onlineDatas, "Total", $total_machines);
          </script>
ONLINE;
        }
        else {
          echo '<span style="color:red">'._T("A problem occurred while counting machines").'</span>';
        }
    }
}
?>
