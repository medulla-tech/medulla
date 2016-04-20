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

echo "
            <HTML>
            <head>
                <title>Siveo Pulse</title>
                <link href='/mmc/graph/master.css' rel='stylesheet' media='screen' type='text/css' />
            </head>
            <BODY style='background-color: #FFFFFF;'>

            hhhhhhhhhhhhhhhh";

if(isset($_GET['objectUUID'])){
    $dd = xmlrpc_getGuacamoleRelaisServerMachineUuid($_GET['objectUUID']);
    print_r($dd);
}

 echo "<pre>";
 //[vnctype] => guacamole
 print_r($_GET);
 
//  print_r($_POST);
//  
//  print_r($_SESSION);
 
 echo "</pre>";
 echo "           </BODY>
            </HTML>
";
// SELECT * FROM xmppmaster.machines
// INNER JOIN xmppmaster.relaisserver
// ON xmppmaster.relaisserver.subnet = xmppmaster.machines.subnetxmpp 
// where xmppmaster.machines.uuid_inventorymachine = "UUID4"  ;

?>
