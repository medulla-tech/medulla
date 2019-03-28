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
 * File xmppMonitoring.php
 */
?>

<style type='text/css'>
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
            $re =  xmlrpc_remoteXmppMonitoring("battery", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("winservices", $jidmachine, 240);
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
            $re =  xmlrpc_remoteXmppMonitoring("clone_ps_aux", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("disk_usage", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("sensors_fans", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("mmemory", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("ifconfig", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("cpu_num", $jidmachine, 100);
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
            $re =  xmlrpc_remoteXmppMonitoring("netstat", $jidmachine, 50);
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
        case 'cputimes':
            echo "TIMES CPU\n";
            //todo mise en forme result
            $suject = array();
            $suject['subaction'] = 'cputimes';
            $r = explode(",", $_GET['args']);
            if (count($r) != 0 and $r[0] != ""){
                $suject['args'] = $r;
            }else{
                $suject['args'] = array();
            }
            $suject['kwargs'] =  json_decode($_GET['kwargs'], true);
            $sujectmonitoring = json_encode ($suject);
            $re =  xmlrpc_remoteXmppMonitoring($sujectmonitoring, $jidmachine, 100);
            $tabresult = json_decode($re['result'][0], true);
            $keystab = array_keys ($tabresult['allcpu']);
            echo "<table style='font-family: Consolas, \"Liberation Mono\", Courier, monospace, sans-serif; font-size: 20px; '>";
                echo "<thead><tr>";
                //Proto Local address@Remote address@Status@PID@Program name
                    echo "<th>CPU num</th>";
                    foreach($keystab as $data){
                                echo "<th>$data</th>";
                            }
                    echo "</tr></thead>";
                    for ($i = 0; $i < $tabresult['nbcpu'];$i++){
                        echo "<tbody><tr>";
                            echo "<td>".$i."</td>";
                        //print_r($tabresult['cpu'.$i] );
                            foreach ($tabresult['cpu'.$i] as $dd => $va){
                                echo "<td>".$va."</td>";
                            }
                    echo "</tr></tbody>";
                    }
                    echo "<tfoot>
                    <tr>";
                        echo "<td>Total Times</td>";
                        foreach ($tabresult['allcpu'] as $dd => $va){
                            echo "<td>".$va."</td>";
                        }
                    echo "</tr>
                    </tfoot>";
            echo "</table>";
        break;
        case 'agentinfos':
            $lp = xmlrpc_get_plugin_lists();
            $descriptor_base = xmlrpc_get_agent_descriptor_base();// search descriptor agent local
            $confx = xmlrpc_get_conf_master_agent();//search configuration of agent master local
            $confxmppmaster = json_decode($confx, true);
            #### self.diragentbase
            $re =  xmlrpc_remoteXmppMonitoring("agentinfos", $jidmachine, 15);//search information machine distante.
                if ($re == ""){
                    $re = "time out command";
                }
                $re = implode("", $re['result']);
                $re = json_decode($re, true);

//                 echo "<pre>";
//                     //print_r($descriptor_base);
//                     // print_r($confxmppmaster); 
//                     //print_r($re);
//                     //print_r($lp);
//                 echo "</pre>";
                //print_r($re);
                echo "<table>";
                    echo "<tr>";
                        echo "<td>";
                        echo "<h1 style=\"font-size: 25px; color:blue; font-weight: bold;\">AGENT BASE</h1>";
                        echo "</td><td>";
                        echo "<h1 style=\"font-size: 25px; color:blue; font-weight: bold;\">AGENT REMOTE</h1>";
                        echo "</td><td>";
                        echo "<h1 style=\"font-size: 25px; color:blue; font-weight: bold;\">AGENT REMOTE IMAGE</h1>";
                        echo "</td>";
                    echo "</tr>";
                    //----------------------- PLUGIN INFORMATIONS -----------------------
                    echo "<tr>";
                        echo "<td>";
                        echo "<h2  colspan=\"3\" style=\"font-size: 20px; color:blue; font-weight: bold;\">PLUGIN INFORMATIONS</h2>";
                        echo "</td>";
                    echo "</tr>";

                    echo "<tr>";
                        echo "<td>";
                            echo "<h2 style=\"color:blue; font-weight: bold;\">PLUGIN BASE</h2>";
                        echo "</td>";
                        echo "<td>";
                            echo "<h2 style=\"color:blue; font-weight: bold;\">LIST PLUGIN AGENT</h2>";
                        echo "</td>";
                        echo "<td>";
                            echo "<h2 style=\"color:blue; font-weight: bold;\"></h2>";
                        echo "</td>";
                    echo "</tr>";
                    
                    echo "<tr>";
                        // ------------------------------ PLUGIN BASE ----------------------------------------
                        echo "<td>";
                            echo "<Hn>list pulgin base</Hn>";
                            echo "<ul>";
                            foreach($lp[0] as $k => $v ){
                                echo "<li>";
                                    if ($v[1] == "relayserver"){
                                        echo "<span style='color:blue;'>";
                                    }
                                        echo $k." <span style='font-weight: bold;'>".$v[0]."</span><span style='font-weight: bold;'> ".$v[1]."</span>";
                                        if ($v[2] != "0.0.0"){
                                            echo " <span style='font-weight: bold;'>(Agent  > ".$v[2].")</span>";
                                        }
                                    if ($v[1] == "relayserver"){
                                        echo "</span>";
                                    }
                                echo "</li>"; 
                            }
                            echo "</ul>";
                            echo "<Hn>list pulgin scheduler</Hn>";
                            echo "<ul>";
                                foreach($lp[1] as $k => $v ){
                                    echo "<li>";
                                        echo $k."=>". $v;
                                    echo "</li>"; 
                                }
                            echo "</ul>";
                        echo "</td>";
                        
                        // ------------------------------ LIST PLUGIN AGENT ----------------------------------------
                        echo "<td>";
                        echo "<Hn>list pulgin distant</Hn>";
                        echo "<ul>";
                            foreach ($re['plugins']['plu'] as $key=>$val){
                                echo "<li>";
                                echo "$key   =>  $val";
                                echo "</li>";
                            }
                        echo "</ul>";
                        echo "<Hn>list pulgin scheduler distant</Hn>";
                        echo "<ul>";
                            foreach ($re['plugins']['schedule'] as $key=>$val){
                                echo "<li>";
                                echo "$key   =>  $val";
                                echo "</li>";
                            }
                        echo "</ul>";
                        
                        
                        echo "</td><td>";
                        echo "<h2 style=\"color:blue; font-weight: bold;\"></h2>";
                        echo "</td>";
                    echo "</tr>";
                    //----------------------------- UPDATE INFORMATIONS ----------------------------------
                    echo "<tr>";
                        echo "<td>";
                        echo "<h2  colspan=\"3\" style=\"font-size: 20px;color:blue; font-weight: bold;\">UPDATE INFORMATIONS</h2>";
                        echo "</td>";
                    echo "</tr>";
                    // ------------------------------ PARAMETERS ----------------------------------------
                    echo "<tr>";
                        echo "<td colspan=\"3\">";
                        echo "<h2  style=\"color:blue; font-weight: bold;\">PARAMETERS</h2>";
                        echo "</td>";
                    echo "</tr>";

                    echo "<tr>";
                        echo "<td>";
                              echo "[global]<br>";
                              echo "autoupdate=".$confxmppmaster['_sections']['global']['autoupdate']."<br>";
                              echo "autoupdatebyrelay=".$confxmppmaster['_sections']['global']['autoupdatebyrelay'];
                        echo "</td>";
                        echo "<td>";
                        echo "[updateagent]<br>";
                        echo "updating=".$re['conf'];
                        echo "</td>";
                        echo "<td>";
                            echo "";
                        echo "</td>";
                    echo "</tr>";
                    // ------------------------------ PATH AGENT ----------------------------------------
                    echo "<tr>";
                        echo "<td colspan=\"3\">";
                        echo "<h2  style=\"color:blue; font-weight: bold;\">PATH AGENT</h2>";
                        echo "</td>";
                    echo "</tr>";
                    echo "<tr>";
                        echo "<td>";
                        echo $confxmppmaster['diragentbase'];
                        echo "</td>";
                        echo "<td>";
                        echo $re['pathagent'];
                        echo "</td><td>";
                        echo $re['pathimg'];
                        echo "</td>";
                    echo "</tr>";
                    
                    
                    
                    echo "<tr>";
                        // ------------------------------ DESCIPTOR AGANT BASE ----------------------------------------
                        echo "<td>";
                                foreach($descriptor_base['directory']  as $key => $value)
                                {
                                    //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
                                    echo "<h2 style=\"color:blue; font-weight: bold;\">".$key."</h2>";
                                    echo "<ul>";
                                    switch ($key ){
                                        case "program_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "lib_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
//                                         case "version_agent" :
//                                             //echo "<p>$value</p>";
//                                             echo "<li>$value</li>";
//                                             break;
                                        case "version" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                        case "script_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "fingerprint" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                    }
                                    echo "</ul>";
                                }
                        echo "</td>";
                        echo "<td>";
                         // ------------------------------ DESCIPTOR AGANT REMOTE ----------------------------------------
                                $json_data = json_decode($re['agentdescriptor'], true);
                                foreach($json_data  as $key => $value)
                                {
                                    //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
                                    echo "<h2 style=\"color:blue; font-weight: bold;\">".$key."</h2>";
                                    echo "<ul>";
                                    switch ($key ){
                                        case "program_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "lib_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
//                                         case "version_agent" :
//                                             //echo "<p>$value</p>";
//                                             echo "<li>$value</li>";
//                                             break;
                                        case "version" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                        case "script_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "fingerprint" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                    }
                                    echo "</ul>";
                                }
                        echo "</td>";
                        echo "<td>";
                            // ------------------------------ DESCIPTOR AGANT REMOTE iMAGE ----------------------------------------
                                $json_data = json_decode($re['imgdescriptor'], true);
                                foreach($json_data  as $key => $value)
                                {
                                    //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
                                    echo "<h2 style=\"color:blue; font-weight: bold;\">".$key."</h2>";
                                    echo "<ul>";
                                    switch ($key ){
                                        case "program_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "lib_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
//                                         case "version_agent" :
//                                             //echo "<p>$value</p>";
//                                             echo "<li>$value</li>";
//                                             break;
                                        case "version" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                        case "script_agent" :
                                            foreach($value as $key1 => $val1){
                                                //echo "$key1 => $val1"."<br>";
                                                echo "<li>$key1 => $val1</li>";
                                            }
                                            break;
                                        case "fingerprint" :
                                            //echo "<p>$value</p>";
                                            echo "<li>$value</li>";
                                            break;
                                    }
                                    echo "</ul>";
                                }
                        echo "</td>";
                    echo "</tr>";
                    // ------------------------------ ACTION POSSIBLE ----------------------------------------
                    echo "<tr>";
                        echo "<td>";
                        echo "</td>";
                        echo "<td colspan=\"2\">";
                            printf("<h2 style=\"color:blue; font-weight: bold;\">%s</h2>",_T("check img remote agent", "xmppmaster"));
                            echo $re['testmodule'];
                        echo "</td>";
                    echo "</tr>";
                    echo "<tr>";
                        echo "<td>";
                        echo "</td>";
                        echo "<td colspan=\"2\">";
                            printf("<h2 style=\"color:blue; font-weight: bold;\">%s</h2>",_T("diff information", "xmppmaster"));
                            echo "<p>".$re['information']."</p>";
                        echo "</td>";
                    echo "</tr>";
                    echo "<tr>";
                        echo "<td>";
                        echo "</td>";
                        echo "<td colspan=\"2\">";
                            printf("<h2 style=\"color:blue; font-weight: bold;\">%s</h2>",_T("Action diff", "xmppmaster"));
                            $txtsearch = array( "Replace or add agent files",
                                    "Action for program_agent",
                                    "Action for lib_agent", 
                                    "Action for script_agent");
                            $se = array();
                            foreach($txtsearch as $tx ){
                            if( $tx == "Replace or add agent files") continue;
                                $pos1 = stripos($re['actiontxt'], $tx);
                                if ($pos1 !== false) {
                                $se[] = $tx;
                                }
                            }
                            $re['actiontxt'] = str_replace( $txtsearch,"", $re['actiontxt']);
                            $re['actiontxt'] = str_replace( "][", "],[", $re['actiontxt']);
                            $json_data = json_decode('[' . $re['actiontxt'] . ']', true);

                            if (count($se) != count($json_data)){
                                array_unshift($se,"Action for program_agent");
                            }
                            foreach($json_data as $val1){
                                $i=0;
                                echo "<Hn>$se[$i]</Hn>";
                                    echo "<ul>";
                                        foreach($val1 as $b){
                                        echo "<li>";
                                            echo $b;
                                        echo "</li>";
                                        }
                                    echo "</ul>";
                                $i++;
                            }
                        echo "</td>";
                    echo "</tr>";
                echo "</table>";
    }
?>
