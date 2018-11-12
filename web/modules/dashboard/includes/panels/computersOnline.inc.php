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
          echo 'Total machines : '.$total_machines.'<br/>';
          echo '<span style="color:green">'._T("Machines online : ","dashboard").$machines_online.'</span><a href="'.$urlRedirect.'&machines=online"><img title="'._T("Create a group","dashboard").'" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a><br/>';
          echo '<span style="color:red">'._T("Machines offline : ","dashboard").$machines_offline.'</span><a href="'.$urlRedirect.'&machines=offline"><img title="'._T("Create a group","dashboard").'" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a><br/>';
        }
        else {
          echo '<span style="color:red">'._T("A problem occurred while counting machines").'</span>';
        }
    }
}
?>
