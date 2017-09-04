<?php
/**
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

include_once("modules/dashboard/includes/panel.class.php");
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
    	$machines_list = xmlrpc_getListPresenceMachine();
        $total_machines = count(getComputersList());

        $machines_online = 0;
    	foreach($machines_list as $id_machine=>$machine)
        {
            if($machine['type'] != 'relayserver')
                $machines_online++;
            else
                continue;
        }
        $machines_offline = $total_machines - $machines_online;
        echo 'Total machines : '.$total_machines.'<br/>';
        echo '<span style="color:green">Machines online : '.$machines_online.'</span><br/>';
        echo '<span style="color:red">Machines offline : '.$machines_offline.'</span><br/>';
    }
}
?>