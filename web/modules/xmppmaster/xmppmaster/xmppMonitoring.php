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
    margin:auto;
    display:block;
}
table.monitoring-table {
  width: 100%;
}
table.monitoring-table td, table.monitoring-table th {
    vertical-align: top;
    width: 33.33%;
    padding: 5px;
}
table.monitoring-table td li {
  margin-bottom: 2px;
}
table.monitoring-table td ul {
  padding-left: 10px;
}
</style>

<?php

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("Quick monitoring", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

if(isset($_GET['jid'])) {
    $jidmachine = $_GET['jid'];

    if(isset($_GET['agenttype']) && $_GET['agenttype'] != '') {
        echo "<h2>".$_GET['agenttype']." : ". $jidmachine."</h2>";
    } else {
        echo "<h2>". $jidmachine."</h2>";
    }
} else {
    echo "<h2>"._T('Machine : ', 'xmppmaster'). $_GET['cn']." ( ".$_GET['os']." )"."</h2>";
    $jidmachine = xmlrpc_getjidMachinefromuuid($_GET['UUID']);
}
switch($_GET['information']) {
    case 'battery':
        $re =  xmlrpc_remoteXmppMonitoring("battery", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('BATTERY', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'winservices':
        $re =  xmlrpc_remoteXmppMonitoring("winservices", $jidmachine, 240);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }

        echo "<pre class='code-output'>";
        echo _T('WIN SERVICES', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'clone_ps_aux':
        $re =  xmlrpc_remoteXmppMonitoring("clone_ps_aux", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('PROCESSES LIST', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'disk_usage':
        $re =  xmlrpc_remoteXmppMonitoring("disk_usage", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('DISK USAGE', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'sensors_fans':
        $re =  xmlrpc_remoteXmppMonitoring("sensors_fans", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('SENSORS FANS', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'mmemory':
        $re =  xmlrpc_remoteXmppMonitoring("mmemory", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('MEMORY USAGE', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'ifconfig':
        $re =  xmlrpc_remoteXmppMonitoring("ifconfig", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('NETWORK INTERFACE', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'cpu_num':
        $re =  xmlrpc_remoteXmppMonitoring("cpu_num", $jidmachine, 100);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<pre class='code-output'>";
        echo _T('CPU NUM', 'xmppmaster')."\n";
        foreach($re["result"] as $datareseau) {
            echo $datareseau;
            echo "\n";
        }
        echo "</pre>";
        break;

    case 'netstat':
        $re =  xmlrpc_remoteXmppMonitoring("netstat", $jidmachine, 50);
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        echo "<table class='code-output'>";
        echo _T('NETSTAT', 'xmppmaster')."\n";
        $entete = array_shift($re['result']);
        //echo $entete;
        echo "<tr>";
        //Proto Local address@Remote address@Status@PID@Program name
        echo "<th>"._T("Proto", "xmppmaster")."</th>
        <th>"._T("Local address", "xmppmaster")."</th>
        <th>"._T("Remote address", "xmppmaster")."</th>
        <th>"._T("Status", "xmppmaster")."</th>
        <th>"._T("PID", "xmppmaster")."</th>
        <th>"._T("Program name", "xmppmaster")."</th>";
        echo "</tr>";
        foreach($re['result'] as $datareseau) {
            echo "<tr>";
            $ligne = explode("@", $datareseau);
            $color = "black";
            switch($ligne[0]) {
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
            foreach($ligne as $data) {
                echo "<td><span style='color :$color'> $data </span></td>";
            }
            echo "</tr>";
        }
        echo "</table>";
        break;
    case 'litlog':
        echo "<h2>"._T("AGENT LOG MACHINE", "xmppmaster")."</h2>";
        $subject = array();
        $subject['subaction'] = 'litlog';
        $r = explode(",", $_GET['args']);
        if (safeCount($r) != 0 and $r[0] != "") {
            $subject['args'] = $r;
        } else {
            $subject['args'] = array();
        }
        $subject['kwargs'] =  json_decode($_GET['kwargs'], true);
        $subjectmonitoring = json_encode($subject);
        //print_r($subjectmonitoring);
        $re =  xmlrpc_remoteXmppMonitoring($subjectmonitoring, $jidmachine, 100);
        //$description = nl2br($re['result'][0]);
        $description = str_replace(array("\\r\\n","\\r","\\n"), "<br/>", $re['result'][0]);
        echo "$description";
        break;
    case 'cputimes':
        echo _T('TIMES CPU', 'xmppmaster')."\n";
        //todo mise en forme result
        $subject = array();
        $subject['subaction'] = 'cputimes';
        $r = explode(",", $_GET['args']);
        if (safeCount($r) != 0 and $r[0] != "") {
            $subject['args'] = $r;
        } else {
            $subject['args'] = array();
        }
        $subject['kwargs'] =  json_decode($_GET['kwargs'], true);
        $subjectmonitoring = json_encode($subject);
        $re =  xmlrpc_remoteXmppMonitoring($subjectmonitoring, $jidmachine, 100);
        $tabresult = json_decode($re['result'][0], true);
        $keystab = array_keys($tabresult['allcpu']);
        echo "<table class='code-output'>";
        echo "<thead><tr>";
        //Proto Local address@Remote address@Status@PID@Program name
        echo "<th>"._T("CPU num", "xmppmaster")."</th>";
        foreach($keystab as $data) {
            echo "<th>$data</th>";
        }
        echo "</tr></thead>";
        for ($i = 0; $i < $tabresult['nbcpu'];$i++) {
            echo "<tbody><tr>";
            echo "<td>".$i."</td>";
            //print_r($tabresult['cpu'.$i] );
            foreach ($tabresult['cpu'.$i] as $dd => $va) {
                echo "<td>".$va."</td>";
            }
            echo "</tr></tbody>";
        }
        echo "<tfoot>
                <tr>";
        echo "<td>"._T("Total Times", "xmppmaster")."</td>";
        foreach ($tabresult['allcpu'] as $dd => $va) {
            echo "<td>".$va."</td>";
        }
        echo "</tr>
                </tfoot>";
        echo "</table>";
        break;
    case 'agentinfos':
        $lp = xmlrpc_get_plugin_lists();
        $descriptor_base = xmlrpc_get_agent_descriptor_base();// search descriptor agent local
        # Add a delay to delay IQ queries
        sleep(5);
        // $confx = xmlrpc_get_conf_master_agent();//search configuration of agent master local
        // $confxmppmaster = json_decode($confx, true);
        #### self.diragentbase
        $re =  xmlrpc_remoteXmppMonitoring("agentinfos", $jidmachine, 15);//search information machine distante.
        if ($re == "") {
            $re = _T("time out command", "xmppmaster");
        }
        if($re != _T("time out command", "xmppmaster")) {
            $re = implode("", $re['result']);
            $re = json_decode($re, true);
        }

        echo "<table class='monitoring-table'>";
        echo "<tr>";
        echo "<td>";
        echo "<h1 style=\"font-size:25px;font-weight:bold;\">"._T("BASE AGENT", "xmppmaster")."</h1>";
        echo "</td><td>";
        echo "<h1 style=\"font-size:25px;font-weight:bold;\">"._T("REMOTE AGENT", "xmppmaster")."</h1>";
        echo "</td><td>";
        echo "<h1 style=\"font-size:25px;font-weight:bold;\">"._T("REMOTE IMAGE", "xmppmaster")."</h1>";
        echo "</td>";
        echo "</tr>";
        //----------------------- PLUGIN INFORMATIONS -----------------------
        echo "<tr>";
        echo "<td>";
        echo "<h2 colspan=\"4\" style=\"font-size:12px;font-weight:bold;\">"._T("PLUGINS", "xmppmaster")."</h2>";
        echo "</td>";
        echo "</tr>";

        echo "<tr>";
        // ------------------------------ PLUGIN BASE ----------------------------------------
        echo "<td>";
        echo "<Hn>"._T("Base plugins", "xmppmaster")."</Hn>";
        echo "<ul>";
        foreach($lp[0] as $k => $v) {
            echo "<li>";
            if ($v[1] == "relayserver") {
                echo "<span class='text-blue'>";
            }
            echo $k." <span class='text-bold'>".$v[0]."</span><span class='text-bold'> ".$v[1]."</span>";
            if ($v[2] != "0.0.0") {
                echo " <span class='text-bold'>(Agent  > ".$v[2].")</span>";
            }
            if ($v[1] == "relayserver") {
                echo "</span>";
            }
            echo "</li>";
        }
        echo "</ul>";
        echo "<Hn>"._T("Base scheduler plugins", "xmppmaster")."</Hn>";
        echo "<ul>";
        foreach($lp[1] as $k => $v) {
            echo "<li>";
            echo $k."=>". $v;
            echo "</li>";
        }
        echo "</ul>";
        echo "</td>";

        // ------------------------------ LIST PLUGIN AGENT ----------------------------------------
        echo "<td valign=\"top\">";
        echo "<Hn>"._T("Remote plugins", "xmppmaster")."</Hn>";
        echo "<ul>";
        if(isset($re['plugins']['plu'])) {
            foreach ($re['plugins']['plu'] as $key => $val) {
                echo "<li>";
                echo "$key   =>  $val";
                echo "</li>";
            }
        } else {
            new NotifyWidgetFailure(_("Trouble to get the distant plugins"));
        }
        echo "</ul>";
        echo "<Hn>"._T("Remote scheduler plugins", "xmppmaster")."</Hn>";
        echo "<ul>";
        if(isset($re['plugins']['plu'])) {
            foreach ($re['plugins']['schedule'] as $key => $val) {
                echo "<li>";
                echo "$key   =>  $val";
                echo "</li>";
            }
        }
        echo "</ul>";


        echo "</td><td>";
        echo "<h2 class=\"text-blue text-bold\"></h2>";
        echo "</td>";
        echo "</tr>";
        //----------------------------- UPDATE INFORMATIONS ----------------------------------
        echo "<tr>";
        echo "<td>";
        echo "<h2  colspan=\"3\" style=\"font-size:12px;font-weight:bold;\">"._T('UPDATE DETAILS', "xmppmaster")."</h2>";
        echo "</td>";
        echo "</tr>";
        // ------------------------------ PARAMETERS ----------------------------------------
        echo "<tr>";
        echo "<td colspan=\"3\">";
        echo "<h2  class=\"text-bold\">"._T("Parameters", "xmppmaster")."</h2>";
        echo "</td>";
        echo "</tr>";

        echo "<tr>";
        echo "<td>";
        echo "[global]<br>";
        $autoupdate = isset($confxmppmaster['_sections']['global']['autoupdate']) ? $confxmppmaster['_sections']['global']['autoupdate'] : '';
        echo "autoupdate=".$autoupdate."<br>";
        $autoupdatebyrelay = isset($confxmppmaster['_sections']['global']['autoupdatebyrelay']) ? $confxmppmaster['_sections']['global']['autoupdatebyrelay'] : '';
        echo "autoupdatebyrelay=".$autoupdatebyrelay;
        echo "</td>";
        echo "<td>";
        echo "[updateagent]<br>";
        $updating = (isset($re['conf'])) ? $re['conf'] : '';
        echo "updating=".$updating;
        echo "</td>";
        echo "<td>";
        echo "";
        echo "</td>";
        echo "</tr>";
        // ------------------------------ PATH AGENT ----------------------------------------
        echo "<tr>";
        echo "<td colspan=\"3\">";
        echo "<h2  class=\"text-bold\">"._T("Folder Path", "xmppmaster")."</h2>";
        echo "</td>";
        echo "</tr>";
        echo "<tr>";
        echo "<td>";
        echo (isset($lp[2])) ? $lp[2] : '';
        echo "</td>";
        echo "<td>";
        echo (isset($re['pathagent'])) ? $re['pathagent'] : '';
        echo "</td><td>";
        echo (isset($re['pathimg'])) ? $re['pathimg'] : '';
        echo "</td>";
        echo "</tr>";



        echo "<tr>";
        // ------------------------------ DESCIPTOR AGANT BASE ----------------------------------------
        echo "<td>";
        foreach($descriptor_base['directory']  as $key => $value) {
            //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
            echo "<h2 class=\"text-bold\">".$key."</h2>";
            echo "<ul>";
            switch ($key) {
                case "program_agent":
                    foreach($value as $key1 => $val1) {
                        //echo "$key1 => $val1"."<br>";
                        echo "<li>$key1 => $val1</li>";
                    }
                    break;
                case "lib_agent":
                    foreach($value as $key1 => $val1) {
                        //echo "$key1 => $val1"."<br>";
                        echo "<li>$key1 => $val1</li>";
                    }
                    break;
                case "version":
                    //echo "<p>$value</p>";
                    echo "<li>$value</li>";
                    break;
                case "script_agent":
                    foreach($value as $key1 => $val1) {
                        //echo "$key1 => $val1"."<br>";
                        echo "<li>$key1 => $val1</li>";
                    }
                    break;
                case "fingerprint":
                    //echo "<p>$value</p>";
                    echo "<li>$value</li>";
                    break;
            }
            echo "</ul>";
        }
        echo "</td>";
        echo "<td>";
        // ------------------------------ DESCIPTOR AGANT REMOTE ----------------------------------------
        if(isset($re['agentdescriptor'])) {
            $json_data = json_decode($re['agentdescriptor'], true);
            foreach($json_data  as $key => $value) {
                //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
                echo "<h2 class=\"text-bold\">".$key."</h2>";
                echo "<ul>";
                switch ($key) {
                    case "program_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                    case "lib_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                    case "version":
                        //echo "<p>$value</p>";
                        echo "<li>$value</li>";
                        break;
                    case "script_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                    case "fingerprint":
                        //echo "<p>$value</p>";
                        echo "<li>$value</li>";
                        break;
                }
                echo "</ul>";
            }
        }
        echo "</td>";
        echo "<td>";
        // ------------------------------ DESCIPTOR AGANT REMOTE iMAGE ----------------------------------------
        if(isset($re['imgdescriptor'])) {
            $json_data = json_decode($re['imgdescriptor'], true);
            foreach($json_data  as $key => $value) {
                //echo "<p style=\"color:blue;font-weight: bold;\">".$key."</p>";
                echo "<h2 class=\"text-bold\">".$key."</h2>";
                echo "<ul>";
                switch ($key) {
                    case "program_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                    case "lib_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                        //                                         case "version_agent" :
                        //                                             //echo "<p>$value</p>";
                        //                                             echo "<li>$value</li>";
                        //                                             break;
                    case "version":
                        //echo "<p>$value</p>";
                        echo "<li>$value</li>";
                        break;
                    case "script_agent":
                        foreach($value as $key1 => $val1) {
                            //echo "$key1 => $val1"."<br>";
                            echo "<li>$key1 => $val1</li>";
                        }
                        break;
                    case "fingerprint":
                        //echo "<p>$value</p>";
                        echo "<li>$value</li>";
                        break;
                }
                echo "</ul>";
            }
        }
        echo "</td>";
        echo "</tr>";
        // ------------------------------ ACTION POSSIBLE ----------------------------------------
        echo "<tr>";
        echo "<td>";
        echo "</td>";
        echo "<td colspan=\"2\">";
        printf("<h2 class=\"text-bold\">%s</h2>", _T("Remote image verifications", "xmppmaster"));
        echo (isset($testmodule)) ? $re['testmodule'] : '';
        echo "</td>";
        echo "</tr>";
        echo "<tr>";

        echo "<td colspan=\"2\">";
        printf("<h2 class=\"text-bold\">%s</h2>", _T("Diff information", "xmppmaster"));
        if(isset($re['information'])) {
            $re['information'] = str_replace(",", "<br>", $re['information']);
            echo "<p>" . $re['information'] . "</p>";
        }
        echo "</td>";
        echo "</tr>";
        echo "<tr>";
        echo "<td colspan=\"2\">";
        printf("<h2 class=\"text-bold\">%s</h2>", _T("Action", "xmppmaster"));
        $txtsearch = array("Replace or add agent files", "Action for program_agent", "Action for lib_agent", "Action for script_agent", "Unused agent file");
        $se = array();

        foreach($txtsearch as $tx) {
            if (strpos($re['actiontxt'], "No UPDATING, no diff between agent and agentimage, Agent up to date") !== false) {
                $cleanedText = trim($re['actiontxt'], ", ");
                echo "<br><p>" . $cleanedText . "</p>";
                break;
            } else {
                if($tx == "Replace or add agent files" || $tx == "Unused agent file") {
                    continue;
                }
                $actiontxt = (isset($re['actiontxt'])) ? $re['actiontxt'] : '';
                $pos1 = stripos($actiontxt, $tx);
                if ($pos1 !== false) {
                    $se[] = $tx;
                }
            }

            if(isset($re['actiontxt'])) {
                $re['actiontxt'] = str_replace($txtsearch, "", $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/^,\s*,/', '', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\s*\[/', '[', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\[\s*,/', '[', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\[\s*/', '[', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/,\s*\[/', '[', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/,\s*\]/', ']', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\s*\]/', ']', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\s*,\s*,/', ',', $re['actiontxt']);
                $re['actiontxt'] = preg_replace('/\\\\\\\\/', '\\', $re['actiontxt']);
                $re['actiontxt'] = str_replace("\\", "\\\\", $re['actiontxt']);
                $json_data = json_decode('[' . $re['actiontxt'] . ']', true);
            } else {
                $json_data = [];
            }

            if (safeCount($se) != safeCount($json_data)) {
                array_unshift($se, "Action for program_agent");
            }

            $i = 0;
            foreach($json_data as $val1) {
                echo "<Hn>$se[$i]</Hn>";
                echo "<ul>";
                foreach($val1 as $b) {
                    echo "<li>";
                    echo $b;
                    echo "</li>";
                }
                echo "</ul>";
                $i++;
            }
        }
        echo "</td>";
        echo "</tr>";
        echo "</table>";
}
?>
