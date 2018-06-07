<?php
/*
 * (c) 2016 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 * File xmppMinotoring.php
 */
?>

style type='text/css'>
textarea {
    width:50% ;
    height:150px;
    margin:auto;   /* exemple pour centrer */
    display:block; /* pour effectivement centrer ! */
}
</style>


<?

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

    $p = new PageGenerator(_T("Quick monitoring", 'xmppmaster'));
    $p->setSideMenu($sidemenu);
    $p->display();

    echo "<h2>Machine : ". $_GET['cn']." ( ".$_GET['os']." )"."</h2>";

     $jidmachine = xmlrpc_getjidMachinefromuuid( $_GET['UUID'] );

     switch($_GET['information']){
        case 'battery':
            $re =  xmlrpc_remoteXmppMonotoring("battery", $jidmachine, 100);
                if ($re == ""){
                    $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "BATTERY\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'winservices':
            $re =  xmlrpc_remoteXmppMonotoring("winservices", $jidmachine, 240);
                if ($re == ""){
                $re = "time out command";
                }
                
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "WIN SERVICES\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'clone_ps_aux':
            $re =  xmlrpc_remoteXmppMonotoring("clone_ps_aux", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "PROCESSUS LIST\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'disk_usage':
            $re =  xmlrpc_remoteXmppMonotoring("disk_usage", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "DISK USAGE\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'sensors_fans':
            $re =  xmlrpc_remoteXmppMonotoring("sensors_fans", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
         echo "SENSORS FANS\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'mmemory':
            $re =  xmlrpc_remoteXmppMonotoring("mmemory", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "MEMORY USAGE\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'ifconfig':
            $re =  xmlrpc_remoteXmppMonotoring("ifconfig", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "NETWORK INTERFACE\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'cpu_num':
            $re =  xmlrpc_remoteXmppMonotoring("cpu_num", $jidmachine, 100);
                if ($re == ""){
                $re = "time out command";
                }
        echo "<pre style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
        echo "CPU NUM\n";
            foreach( $re[result] as $datareseau){
                echo $datareseau;
                echo "\n";
            }
        echo "</pre>";
        break;

        case 'netstat':
            $re =  xmlrpc_remoteXmppMonotoring("netstat", $jidmachine, 50);
                if ($re == ""){
                $re = "time out command";
                }
            echo "<table style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
            echo "NETSTAT\n";
            $entete = array_shift ( $re[result] );
            echo $entete;
            echo "<tr>";
            //Proto Local address@Remote address@Status@PID@Program name
            echo "<th>Proto</th>
            <th>Local address</th>
            <th>Remote address</th>
            <th>Status</th>
            <th>PID</th>
            <th>Program name</th>";
            echo "</tr>";
            foreach( $re[result] as $datareseau){
                echo "<tr>";
                    $ligne = explode("@", $datareseau);
                    $color = "black";
                    switch($ligne[0]){
                        case "tcp":
                            $color = "blue";
                        break;
                        case "udp":
                            $color = "navy";
                        break;
                        case "udp6":
                            $color = "maroon";
                        break;
                    }
                    foreach($ligne as $data){
                         echo "<td><span style='color :$color'> $data </span></td>";
                    }
                echo "</tr>";
            }
            echo "</table>";
        break;
    }
?>
