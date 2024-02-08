<?php
/*
 * (c) 2017-2021 siveo, http://www.siveo.net/
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
 *
 *  file : logs/viewmachinelogs.php
 */
?>
<style>

.log_err{
  color : red;
}

.log_warn{
  color : orange;
}

.log_ok{
  color : green;
}

.shadow
{
  -moz-box-shadow: 4px 4px 10px #888;
  -webkit-box-shadow: 4px 4px 10px #888;
  box-shadow:4px 4px 6px #888;
}

.actions:target {
   background-color: #ffa;
}
.actions{
  margin-bottom:5px;
  padding:3px;
  border: dashed 1px rgb(100,100,100);
  display:flex;
}

.actions a:hover{
  background-color: #007fff;
  color:rgb(255, 255, 255);
  border: 1px solid #003eff
}

.actions a{
  padding:1px;
}

.action_datas, .action_result{
  width:50%;
  padding:10px;
}
</style>

<?php

require_once("modules/medulla_server/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
include_once('modules/medulla_server/includes/menu_actionaudit.php');
include_once('modules/glpi/includes/xmlrpc.php');
include_once('modules/pkgs/includes/xmlrpc.php');

// Retrieve information deploy. For cmn_id

$info = xmlrpc_getdeployfromcommandid($cmd_id, $uuid);

if($info["len"] == 0){?>
    <script>
    function refresh(){
        location.reload();
    }
    window.setTimeout(refresh, 10000);
    </script>
<?php }

$isUpdate = (substr($info['objectdeploy'][0]['sessionid'], 0, 6) == "update") ? true : false;
$deploymachine = xmlrpc_get_deployxmpponmachine($cmd_id, $uuid);

$tab = xmlrpc_get_conrainte_slot_deployment_commands([$cmd_id]);
$contrainte  = safeCount($tab) ? $tab[$cmd_id] : "";

$pkgname = get_pkg_name_from_uuid($deploymachine['package_id']);
$pkgcreator = get_pkg_creator_from_uuid($deploymachine['package_id']);

$update_datas = [];
if($isUpdate) {
    $update_kb = xmlrpc_get_update_kb($deploymachine['package_id']);
}

$p = new PageGenerator(_T("Deployment [machine ", 'xmppmaster')." ".$deploymachine['target_name']."]");
$p->setSideMenu($sidemenu);
$p->display();

$hideText = _T("Hide", "xmppmaster");
$showText = _T("Show", "xmppmaster");

if(isset($info['objectdeploy'][0]['state']) && $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT ABORT") {
    echo "<H1>DEPLOYMENT ABORT</H1>";
}

$boolterminate = false;
if(isset($info['objectdeploy'][0]['sessionid'])) {
    if (isset($_POST['bStop'])) {
        $_SESSION[$info['objectdeploy'][0]['sessionid']] = "end";
        // if stop deploy message direct in les log
        // session for session id
        //xmlrpc_getlinelogssession($sessionxmpp);
        xmlrpc_set_simple_log(
            '<span style="color : Orange, font-style : bold">WARNING !!! </span><span  style="color : Orange ">Request for a stop of deployment</span>',
            $info['objectdeploy'][0]['sessionid'],
            "deploy",
            "-1",
            "pulse_mmc"
        );
        xmlrpc_updatedeploy_states_start_and_process($info['objectdeploy'][0]['sessionid'], "ABORT DEPLOYMENT CANCELLED BY USER");
    }
    $sessionxmpp = $info['objectdeploy'][0]['sessionid'];
    $infodeploy = xmlrpc_getlinelogssession($sessionxmpp);
    $uuid = $info['objectdeploy'][0]['inventoryuuid'];
    foreach($infodeploy['log'] as $line) {
        if ($line['text'] == "DEPLOYMENT TERMINATE" || strpos($line['text'], "DEPLOYMENT ABORT") !== false) {
            $boolterminate = true;
        }
    }
}

$datawol = xmlrpc_getlinelogswolcmd($cmd_id, $uuid);
$resultinfo = (isset($info['objectdeploy'][0]['result']) ? json_decode($info['objectdeploy'][0]['result']) : null);
unset($info['objectdeploy'][0]['result']);

$infoslist = null;
$descriptorslist = null;
$otherinfos = null;
$ipmaster = null;
$iprelay = null;
$ipmachine = null;
if($resultinfo) {
    $infoslist = $resultinfo->infoslist;
    unset($resultinfo->infoslist);
    $descriptorslist = $resultinfo->descriptorslist;
    unset($resultinfo->descriptorslist);
    $otherinfos = $resultinfo->otherinfos;
    $ipmaster = $otherinfos[0]->ipmaster;
    $iprelay =  $otherinfos[0]->iprelay;
    $ipmachine = $otherinfos[0]->ipmachine;
    unset($resultinfo->otherinfos);
}

$ipmachine = ($otherinfos) ? $otherinfos[0]->ipmachine : null;
$macstr = "";
$macList = ($otherinfos) ? getMachinesMac($otherinfos[0]->uuid)[strtoupper($otherinfos[0]->uuid)] : null;

if($macList) {
    // remove empty values
    // keep only uniq values
    // then join result with ' || '
    $macstr = join(" || ", array_values(array_filter(array_unique($macList))));
}
//     if ( isset($resultinfo->title)){
//         echo "User : $resultinfo->user "."PACKAGE ". $resultinfo->title."<br>";
//     }
if ($datawol['len'] != 0) {
    echo "<br>";
    echo '<h2 class="replytab" id="wol">'.$hideText.' '._T("Wake on Lan", "xmppmaster").'</h2>';
    echo "<div id='titlewol'>";
    echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
    echo "<thead>";
    echo "<tr>";
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">START</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">STEP</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">DESCRIPTION</span>';
    echo '</td>';
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";
    foreach($datawol['log'] as $line) {
        $startsteparray = get_object_vars($line['date']);
        $datestartstep = date("Y-m-d H:i:s", $startsteparray['timestamp']);
        echo '<tr class="alternate">';
        echo "<td>";
        echo $datestartstep;
        echo "</td>";
        echo "<td>";
        echo $line['priority'];
        echo "</td>";
        echo "<td>";
        echo $line['text'];
        echo "</td>";
        echo "</tr>";
    }
    echo "</tbody>";
    echo "</table>";
    echo "</div>";
}
if ($info['len'] == 0 || $boolterminate == false) {
    $result = command_detail($cmd_id);
    $start_date = mktime(
        $result['start_date'][3],
        $result['start_date'][4],
        $result['start_date'][5],
        $result['start_date'][1],
        $result['start_date'][2],
        $result['start_date'][0]
    );
    $start_date = date("Y-m-d H:i:s", $start_date);
    $end_date = mktime(
        $result['end_date'][3],
        $result['end_date'][4],
        $result['end_date'][5],
        $result['end_date'][1],
        $result['end_date'][2],
        $result['end_date'][0]
    );
    $end_date = date("Y-m-d H:i:s", $end_date);
    echo "<h2>Please wait (".$result['title'].")</h2>";
    if(isset($info['objectdeploy'][0]['state']) &&
        (strpos($info['objectdeploy'][0]['state'], "DEPLOYMENT START") !== false ||
          $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT DIFFERED")) {
        echo "<br>Preparing deployment. Please wait...";
        echo "<img src='modules/xmppmaster/img/waitting.gif'>";
        echo "<br>";
    }
}
if (safeCount($deploymachine) != 0) {
    $creation_date = mktime(
        $deploymachine['creation_date'][3],
        $deploymachine['creation_date'][4],
        $deploymachine['creation_date'][5],
        $deploymachine['creation_date'][1],
        $deploymachine['creation_date'][2],
        $deploymachine['creation_date'][0]
    );
    $creation_date = date("Y-m-d H:i:s", $creation_date);

    $start_datemsc = mktime(
        $deploymachine['startdatec'][3],
        $deploymachine['startdatec'][4],
        $deploymachine['startdatec'][5],
        $deploymachine['startdatec'][1],
        $deploymachine['startdatec'][2],
        $deploymachine['startdatec'][0]
    );

    $start_datemsc = date("Y-m-d H:i:s", $start_datemsc);

    $start_date_plan_msc = mktime(
        $deploymachine['startdateh'][3],
        $deploymachine['startdateh'][4],
        $deploymachine['startdateh'][5],
        $deploymachine['startdateh'][1],
        $deploymachine['startdateh'][2],
        $deploymachine['startdateh'][0]
    );
    $start_date_plan_msc = date("Y-m-d H:i:s", $start_date_plan_msc);

    $end_date_plan_msc = mktime(
        $deploymachine['enddateh'][3],
        $deploymachine['enddateh'][4],
        $deploymachine['enddateh'][5],
        $deploymachine['enddateh'][1],
        $deploymachine['enddateh'][2],
        $deploymachine['enddateh'][0]
    );
    $end_date_plan_msc = date("Y-m-d H:i:s", $end_date_plan_msc);

    if (isset($otherinfos[0]->ipmachine) && $otherinfos[0]->ipmachine != "") {
        $titleip = _T("IP Address (from XMPP)", "xmppmaster");
    } else {
        $titleip = _T("IP Address (from GLPI)", "xmppmaster");
    }
    echo "<br>";
    echo '<h2 class="replytab" id="detailmach">'.$hideText.' '._T("Machine Details", "xmppmaster"). '</h2>';
    echo "<div id='titledetailmach'>";
    echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
    echo "<thead>";
    echo "<tr>";
    echo '<td style="width: 210px;">';
    echo '<span style="padding-left: 32px;">'._T("Machine", "xmppmaster").'</span>';
    echo '</td>';

    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'.$titleip.'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("MAC Address", "xmppmaster").'</span>';
    echo '</td>';
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";
    echo "<tr>";
    echo "<td>";
    echo $deploymachine['target_name'];
    echo "</td>";

    echo "<td>";
    echo (isset($otherinfos[0]->ipmachine) && $otherinfos[0]->ipmachine != "") ? $otherinfos[0]->ipmachine : $deploymachine['target_ipaddr'];
    echo "</td>";
    echo "<td>";
    if($macstr == "" && isset($deploymachine['target_macaddr'])) {
        $macList = explode("||", $deploymachine['target_macaddr']);
        $macstr = join(" || ", array_values(array_filter(array_unique($macList))));
    }
    echo $macstr;
    echo "</td>";
    echo "</tr>";
    echo "</tbody>";
    echo "</table>";
    echo "</div>";
    echo '<br>';
    echo "<br>";
    echo '<h2 class="replytab" id="detailpack">'.$hideText.' '._T("Package Details", "xmppmaster").'</h2>';
    echo "<div id='titledetailpack'>";
    echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
    echo "<thead>";
    echo "<tr>";
    echo '<td style="width:250 ;">';
    echo '<span style=" padding-left: 32px;">'._T("Creator", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Name", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Folder", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: 300px;">';
    echo '<span style=" padding-left: 32px;">'._T("Creation Date", "xmppmaster").'</span>';
    echo '</td>';
    if($isUpdate) {
        echo '<td class="action" style="text-align:center;">';
        echo '<span>'._T("Actions", "updates").'</span>';
        echo '</td>';
    }
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";
    echo "<tr>";
    echo "<td>";
    echo $pkgcreator[$deploymachine['package_id']];
    echo "</td>";
    echo "<td>";
    echo $pkgname[$deploymachine['package_id']];
    echo "</td>";
    echo "<td>";
    echo $deploymachine['package_id'];
    echo "</td>";
    echo "<td>";
    echo $creation_date;
    echo "</td>";
    if($isUpdate) {
        echo '<td class="action" style="text-align:center;">';
        echo '<ul class="action">';
        echo '<li class="infoupdate"><a href="https://www.catalog.update.microsoft.com/Search.aspx?q='.$deploymachine['package_id'].'"> </a></li>';
        echo '<li class="helpupdate"><a href="https://support.microsoft.com/help/'.$update_kb.'"> </a></li>';
        echo '</ul>';
        echo '</td>';
    }
    echo "</tr>";
    echo "</tbody>";
    echo "</table>";
    echo "</div>";
    echo '<br>';
    echo '<h2 class="replytab" id="deployplan">'.$hideText.' '._T("Deployment plan", "xmppmaster").'</h2>';
    echo "<div id='titledeployplan'>";
    echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
    echo "<thead>";
    echo "<tr>";
    echo '<td style="width:250 ;">';
    echo '<span style=" padding-left: 32px;">'._T("User", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Package Name", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Start Date", "xmppmaster").'</span>';
    echo '</td>';
    if ($contrainte != "") {
        echo '<td style="width: ;">';
        echo '<span style=" padding-left: 32px;">'._T("Deployment Interval Constraint", "xmppmaster").'</span>';
        echo '</td>';
    }
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Stop Date", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="width: ;">';
    echo '<span style=" padding-left: 32px;">'._T("Session Id", "xmppmaster").'</span>';
    echo '</td>';
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";
    echo "<tr>";
    echo "<td>";
    echo $deploymachine['creator'];
    echo "</td>";
    echo "<td>";
    echo $deploymachine['title'];
    echo "</td>";
    echo "<td>";
    echo $start_date_plan_msc;
    echo "</td>";
    if ($contrainte != "") {
        echo "<td>";
        echo $contrainte;
        echo "</td>";
    }
    echo "<td>";
    echo $end_date_plan_msc;
    echo "</td>";
    echo "<td>";
    echo $info['objectdeploy'][0]['sessionid'];
    echo "</td>";
    echo "</tr>";
    echo "</tbody>";
    echo "</table>";
    echo "</div>";
    echo '<br>';
}

if ($info['len'] != 0) {
    if(isset($info['objectdeploy'][0]['state']) &&
        (strpos($info['objectdeploy'][0]['state'], "DEPLOYMENT START") !== false ||
            $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT DIFFERED")) {
        if (!$boolterminate && !isset($_POST['bStop'])) {
            if (!isset($_SESSION[$info['objectdeploy'][0]['sessionid']])) {
                $f = new ValidatingForm();
                $f->add(new HiddenTpl("id"), array("value" => $_GET['cmd_id'], "hide" => true));
                $f->addButton("bStop", "Stop Deploy");
                $f->display();
            }
        }
    }
    $state = $info['objectdeploy'][0]['state'];
    $start = get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
    $host = $info['objectdeploy'][0]['host'];
    $jidmachine = $info['objectdeploy'][0]['jidmachine'];
    $jid_relay = $info['objectdeploy'][0]['jid_relay'];
    $datestart =  date("Y-m-d H:i:s", $start);
    $scalardate = get_object_vars($info['objectdeploy'][0]['start'])['scalar'];
    $formateddate = substr($scalardate, 0, 4).'-'.substr($scalardate, 4, 2).'-'.substr($scalardate, 6, 2).' '.substr($scalardate, 9);
    echo "<div>";
    echo '<H2 style="align=center;">'._T("Start deployment : ", "xmppmaster").$formateddate.'</H2>';
    echo "</div>";
    if (isset($infoslist)) {
        if ($info['len'] != 0) {
            $jidmachine = $info['objectdeploy'][0]['jidmachine'];
            $jid_relay = $info['objectdeploy'][0]['jid_relay'];
            echo "<br>";
            echo '<h2 class="replytab" id="xmppinfo">'.$hideText.' '._T("XMPP Information", "xmppmaster").'</h2>';
            echo "<div id='titlexmppinfo'>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
            echo "<thead>";
            echo "<tr>";
            echo '<td style="text-align: center";>';
            echo '<span>'._T("Machine JID", "xmppmaster").'</span>';
            echo '</td>';
            echo '<td style="text-align: center";>';
            echo '<span">'._T("Relay Server JID", "xmppmaster").'</span>';
            echo '</td>';
            echo '<td style="text-align: center";>';
            echo '<span>'._T("Machine IP", "xmppmaster").'</span>';
            echo '</td>';
            echo '<td style="text-align: center";>';
            echo '<span>'._T("Relay Server IP", "xmppmaster").'</span>';
            echo '</td>';
            echo '<td style="text-align: center";>';
            echo '<span>'._T("Master IP", "xmppmaster").'</span>';
            echo '</td>';
            echo "</tr>";
            echo "</thead>";

            echo "<tbody>";
            echo '<tr>';
            echo '<td style="text-align: center";>' . $jidmachine . '</td>';
            echo '<td style="text-align: center";>' . $jid_relay . '</td>';
            echo '<td style="text-align: center";>' . $ipmachine . '</td>';
            echo '<td style="text-align: center";>' . $iprelay . '</td>';
            echo '<td style="text-align: center";>' . $ipmaster . '</td>';
            echo "</tr>";
            echo "</tbody>";
            echo "</table>";
            echo "</div>";
        }
        echo "<br>";
        echo '<h2 class="replytab"  id="dependency">'.$hideText.' '._T("Package and Dependency", "xmppmaster").'</h2>';
        echo "<div id='titledependency'>";
        echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
        echo "<thead>";
        echo "<tr>";
        echo '<td style="text-align: center";>';
        echo '<span>'._T("Name", "xmppmaster").'</span>';
        echo '</td>';
        echo '<td style="text-align: center";">';
        echo '<span>'._T("Software", "xmppmaster").'</span>';
        echo '</td>';
        echo '<td style="text-align: center";">';
        echo '<span>'._T("Version", "xmppmaster").'</span>';
        echo '</td>';
        echo '<td style="text-align: center";">';
        echo '<span>'._T("Description", "xmppmaster").'</span>';
        echo '</td>';
        echo "</tr>";
        echo "</thead>";
        echo "<tbody>";
        foreach (range(0, safeCount($infoslist) - 1) as $index) {
            $inf = $infoslist[$index];
            echo "<tr>";
            echo '<td style="text-align: center";>';
            echo $inf->name;
            echo "</td>";
            echo '<td style="text-align: center";>';
            echo $inf->software;
            echo "</td>";
            echo '<td style="text-align: center";>';
            echo $inf->version;
            echo "</td>";
            echo '<td style="text-align: center";>';
            echo $inf->description;
            echo "</td>";
            echo "</tr>";
        }
        echo "</tbody>";
        echo "</table>";
        echo "</div>";
        echo '<br>';
    }
    echo "<br>";
    echo '<h2 class="replytab" id="phase">'.$hideText.' '._T("Deployment phases", "xmppmaster").'</h2>';
    echo "<div id='titlephase'>";
    echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
    echo "<thead>";
    echo "<tr>";
    echo '<td  style="width : 120px;">';
    echo '<span style=" padding-left: 32px;">'._T("START", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td>';
    echo '<span style=" padding-left:0px;">'._T("STEP", "xmppmaster").'</span>';
    echo '</td>';
    echo '<td style="text-align: center";>';
    echo '<span style="padding-left: 32px;">'._T("DESCRIPTION", "xmppmaster").'</span>';
    echo '</td>';
    echo "</tr>";
    echo "</thead>";
    echo "<tbody>";

    foreach($infodeploy['log'] as $line) {
        $scalardate = get_object_vars($line['date'])['scalar'];
        $formateddate = substr($scalardate, 0, 4).'-'.substr($scalardate, 4, 2).'-'.substr($scalardate, 6, 2).' '.substr($scalardate, 9);
        //$startsteparray= get_object_vars( $line['date']);
        //$datestartstep = date("Y-m-d H:i:s", $startsteparray['timestamp']);
        //$datestartstep = date("Y-m-d H:i:s", $info['objectdeploy'][0]['start']->timestamp);

        echo '<tr class="alternate">';
        echo "<td>";
        echo $formateddate;
        //echo $formateddate;
        echo "</td>";
        echo "<td>";
        echo '<span  style="padding-left:10px;">';
        echo $line['priority'];
        echo "</span>";
        echo "</td>";
        echo "<td>";
        echo $line['text'];
        echo "</td>";
        echo "</tr>";
    }
    echo "</tbody>";
    echo "</table>";
    echo "</div>";
    $actionsname = array(
                          "action_pwd_packagecompleted" =>  "Current directory is package directory",
                          "action_pwd_package" =>  "Current directory is package directory",
                          "actionprocessscript" => "Script Running in process",
                          "action_command_natif_shell" => "Script Running in thread",
                          "actionerrorcompletedend" => "<span style='color:red;'>Deployment terminated on an error. Clean packages</span>",
                          "actionsuccescompletedend" => "Deployment terminated successfully. Clean package",
                          "actioncleaning"  => "Clean downloaded package",
                          "actionrestartbot" => "Restart agent",
                          "actionrestart" => "Restart Machine",
                          "action_unzip_file" => "unzip file",
                          "action_set_environ" => "Initializes environment variables",
                          "action_no_operation" => "no action",
    );
    if (isset($descriptorslist)) {
        echo "<br>";

        $header = "";
        $values = "";
        $content = "";

        $deploymentCompleted = $boolterminate ? true : false;
        $deploymentSuccessed = false;

        // Do some modifications on actions result
        $resultcommand = '@resultcommand';
        $_1lastlines = '1@lastlines';
        $_10lastlines = '10@lastlines';
        $_20lastlines = '20@lastlines';
        $_30lastlines = '30@lastlines';

        $_1firstlines = '1@firstlines';
        $_10firstlines = '10@firstlines';
        $_20firstlines = '20@firstlines';
        $_30firstlines = '30@firstlines';
        $associations = [];
        foreach($descriptorslist[0] as $keyId => $_action) {
            $associations[$_action->actionlabel] = $_action;
            // Digest name for action step names
            $_action->action = ltrim(ltrim($_action->action, 'action'), '_');

            // Explicit if the step is in success state
            if($_action->completed && $_action->completed == 1 && isset($_action->codereturn)) {
                $_action->successed = ($_action->codereturn == 0) ? true : false;
            } else {
                $_action->successed = false;
            }
            // Explicit if the step has been completed
            if(!isset($_action->completed)) {
                $_action->completed = false;
            }

            // Determine if the deployment is finished and if it is in success or error
            if($_action->actionlabel == "END_ERROR" && isset($_action->completed) && $_action->completed == 1) {
                $deploymentCompleted = true;
                $_action->successed = true;
                //$deploymentSuccessed is already set to false
            }
            if($_action->actionlabel == "END_SUCCESS" && isset($_action->completed) && $_action->completed == 1) {
                $deploymentCompleted = true;
                $deploymentSuccessed = true;
                $_action->successed = true;
            }
        }

        echo '<h2 class="replytab2">'._T("Deployment Status", "xmppmaster").'</h2>';
        if($deploymentCompleted) {
            if($deploymentSuccessed) {
                echo '<p style="font-weight:bold; color:green;">'._T("Complete", 'xmppmaster')." : "._T("yes", "xmppmaster").'</p>';
                echo '<p style="font-weight:bold; color:green;">'._T("Successed", "xmppmaster").' : '._T("yes", "xmppmaster").'</p>';
            } else {
                echo '<p style="font-weight:bold; color:green;">'._T("Complete", 'xmppmaster')." : "._T("yes", "xmppmaster").'</p>';
                echo '<p style="font-weight:bold; color:red;">'._T("Success", "xmppmaster").' : '._T("no", "xmppmaster").'</p>';
            }
        } else {
            echo '<p style="font-weight:bold; color:blue;">'._T("Complete", "xmppmaster").' : '._T("processing", "xmppmaster").'</p>';
        }

        // Now we know all the steps status

        // step processing : !deploymentCompleted && !completed
        // step completed but error : completed && !successed
        // step completed and success : completed && successed == 0
        // step ignored : deploymentCompleted && !completed
        foreach($descriptorslist[0] as $_action) {

            $content .= "<div class='actions' id='".$cmd_id."-".$_action->step."'>";
            $content .= "<div class='action_datas'>";

            if($deploymentCompleted && !$_action->completed) {
                $content .= '<h3>['._T("Not completed", "xmppmaster").'] Action '.$_action->action.' '._T("labelled", "xmppmaster").' '.$_action->actionlabel.'</h3>';
            }
            // step processing
            if(!$deploymentCompleted && !$_action->completed) {

                $content .= '<h3>['._T("Processing", "xmppmaster").'] Action '.$_action->action.' '._T("labelled", "xmppmaster").' '.$_action->actionlabel.'</h3>';
            }
            // step failed
            elseif($_action->completed && !$_action->successed) {
                $content .= '<h3>['._T("Failure", "xmppmaster").'] Action '.$_action->action.' '._T("labelled", "xmppmaster").' '.$_action->actionlabel.'</h3>';
            }
            // step successed
            elseif($_action->completed && $_action->successed) {
                $content .= '<h3>['._T("Success", "xmppmaster").'] Action '.$_action->action.' '._T("labelled", "xmppmaster").' '.$_action->actionlabel.'</h3>';
            }


            $content .= '<ul>';
            if(isset($_action->command)) {
                $command = base64_decode($_action->command, true) == false ? $_action->command : base64_decode($_action->command);
                $content .= '<li>';
                $content .= _T("Executed Command", "pkgs").' : '.htmlentities($command);
                $content .= '</li>';
            }
            if(isset($_action->typescript) && $_action->typescript != "") {
                $content .= '<li>';
                $content .= _T("Type Script", "pkgs").' : '.htmlentities($_action->typescript);
                $content .= '</li>';
            }
            if(isset($_action->bang) && $_action->bang != "") {
                $content .= '<li>';
                $content .= _T("Shebang", "pkgs").' : '.htmlentities($_action->bang);
                $content .= '</li>';
            }
            if(isset($_action->script)) {
                $content .= '<li>';
                $script = (base64_decode($_action->script, true) == false) ? $_action->script : base64_decode($_action->script);
                $content .= _T("Script", "pkgs").' : '.nl2br(htmlentities($script));
                $content .= '</li>';
            }
            if(isset($_action->timeout) && $_action->timeout != "") {
                $content .= '<li>';
                $content .= _T("Timeout", "pkgs").' : '.htmlentities($_action->timeout);
                $content .= '</li>';
            }
            if(isset($_action->codereturn) && $_action->codereturn != "") {
                $content .= '<li>';
                $content .= _T("Code Return", "pkgs").' : '.htmlentities($_action->codereturn);
                $content .= '</li>';
            }
            if(isset($_action->packageuuid)  && $_action->packageuuid != "") {
                $content .= '<li>';
                $content .= _T("Alternate Package", "pkgs").' : '.htmlentities($_action->packageuuid);
                $content .= '</li>';
            }
            if(isset($_action->environ)  && $_action->environ != []) {
                $content .= '<li>';
                $content .= _T("Set Environ Variable", "pkgs").' : ';
                $content .= '<ul>';
                foreach($_action->environ as $opt => $optval) {
                    $content  .= '<li>'.htmlentities($opt).': '.htmlentities($optval).'</li>';
                }
                $content .= '</ul>';
                $content .= '</li>';
            }
            if(isset($_action->filename)  && $_action->filename != "") {
                $content .= '<li>';
                $content .= _T("File", "pkgs").' : '.htmlentities($_action->filename);
                $content .= '</li>';
            }
            if(isset($_action->set)  && $_action->set != "") {
                $content .= '<li>';
                $set = (base64_decode($_action->set, true) == false) ? $_action->set : base64_decode($_action->set);
                $content .= _T("Set", "pkgs").' : '.htmlentities($set);
                $content .= '</li>';
            }
            if(isset($_action->url)  && $_action->url != "") {
                $content .= '<li>';
                $content .= _T("Download File", "pkgs").' : <a href="'.htmlentities($_action->url).'">'.htmlentities($_action->url).'</a>';
                $content .= '</li>';
            }
            if(isset($_action->targetrestart)  && $_action->targetrestart != "") {
                $content .= '<li>';
                $content .= ($_action->targetrestart == "AM") ? _T("Restart", "pkgs").' : '._T("Agent Machine", "pkgs") : _T("Restart", "pkgs").' : '._T("Machine", "pkgs");
                $content .= '</li>';
            }
            if(isset($_action->waiting)  && $_action->waiting != "") {
                $content .= '<li>';
                $content .= _T("Waiting", "pkgs").' : '.$_action->waiting.' '._T('secs.', "pkgs").'<br>';
                $content .= _T("Go to", "pkgs").' : <a href="#'.$cmd_id.'-'.htmlentities($associations[$_action->goto]->step).'">'.htmlentities($associations[$_action->goto]->action).' at '.htmlentities($associations[$_action->goto]->actionlabel).'</a>';
                $content .= '</li>';
            }
            if(isset($_action->comment)  && $_action->comment != "") {
                $content .= '<li>';
                $_comment = (base64_decode($_action->comment, true) == false) ? $_action->comment : base64_decode($_action->comment);
                $content .= _T("Comment", "pkgs").' : '.nl2br(htmlentities($_comment));
                $content .= '</li>';
            }
            if(isset($_action->inventory)) {
                $content .= '<li>';
                $content .= _T("Inventory", "pkgs").' : '.htmlentities($_action->inventory);
                if(isset($_action->actioninventory)) {
                    $content .= ', '.htmlentities($_action->actioninventory);
                }
                $content .= '</li>';
            }
            if(isset($_action->clear)) {
                $content .= '<li>';
                $content .= _T("Clear package after install", "pkgs").' : '.htmlentities($_action->clear);
                $content .= '</li>';
            }


            $content .= '</ul>';

            // Choose the next step. If failed && error defined : goto error
            if((isset($_action->error) && !$_action->successed && $_action->completed)) {
                $content .= '<a href="#'.$cmd_id.'-'.$descriptorslist[0][$_action->error]->step.'">'._T("Next Step", 'xmppmaster').' : '.$descriptorslist[0][$_action->error]->action.' '._T("at", "xmppmaster").' '.$descriptorslist[0][$_action->error]->actionlabel.'</a>';
            }
            // If success && success defined : goto success
            elseif(isset($_action->success) && $_action->successed) {
                $content .= '<a href="#'.$cmd_id.'-'.$descriptorslist[0][$_action->success]->step.'">'._T("Next Step", 'xmppmaster').' : '.$descriptorslist[0][$_action->success]->action.' '._T("at", "xmppmaster").' '.$descriptorslist[0][$_action->success]->actionlabel.'</a>';
            }
            // If closure action (end or success action) : end point
            elseif($_action->actionlabel == "END_ERROR" || $_action->actionlabel == "END_SUCCESS") {
                $content .= 'End of deployment';
            } else {
                $content .= '<a href="#'.$cmd_id.'-'.($_action->step + 1).'">'._T("Next Step", 'xmppmaster').' : '.$descriptorslist[0][$_action->step + 1]->action.' '._T("at", "xmppmaster").' '.$descriptorslist[0][$_action->step + 1]->actionlabel.'</a>';
            }
            $content .= '</div>'; // .action_datas
            $content .= '<div class="action_result">';

            if(isset($_action->$resultcommand) && $_action->$resultcommand != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$resultcommand));
            }
            if(isset($_action->$_1lastlines) && $_action->$_1lastlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_1lastlines));
            }
            if(isset($_action->$_1firstlines) && $_action->$_1firstlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_1firstlines));
            }

            if(isset($_action->$_10lastlines) && $_action->$_10lastlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_10lastlines));
            }
            if(isset($_action->$_20lastlines) && $_action->$_20lastlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_20lastlines));
            }
            if(isset($_action->$_30lastlines) && $_action->$_30lastlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_30lastlines));
            }

            if(isset($_action->$_10firstlines) && $_action->$_10firstlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_10firstlines));
            }

            if(isset($_action->$_20firstlines) && $_action->$_20firstlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_20firstlines));
            }

            if(isset($_action->$_30firstlines) && $_action->$_30firstlines != "") {
                $content .= '<h3>'._T("Result Command", "pkgs").'</h3>';
                $content .= nl2br(htmlentities($_action->$_30firstlines));
            }
            $content .= '</div>';// .action_result
            $content .= '</div>'; // .actions
        }
        echo $content;
    }
    if (isset($otherinfos[0]->environ) && safeCount((array)$otherinfos[0]->environ) == 1) {
        if ($info['len'] != 0) {
            $res = str_replace("{'", "'", $otherinfos[0]->environ);
            $res = str_replace("'}", "'", $res);
            $res = str_replace("  ", " ", $res);
            $res = str_replace("  ", " ", $res);
            $res = str_replace("  ", " ", $res);
            $res = str_replace("': '", "' : '", $res);
            $res = str_replace("', '", "' , '", $res);
            $res = str_replace("\\\\", "\\", $res);
            $res = str_replace("C:\\", "C:\\\\", $res);
            $res = explode("' , '", $res);
            echo "<br>";
            echo '<h2 class="replytab" id="titleenv" >'.$hideText.' '._T("Environment", "xmppmaster").'</h2>';
            echo "<div id='env'>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
            echo "<thead>";
            echo "<tr>";
            echo '<td  style="width : 120px;">';
            echo '<span style=" padding-left: 32px;">'._T("key", "xmppmaster").'</span>';
            echo '</td>';
            echo '<td>';
            echo '<span style=" padding-left:0px;">'._T("value", "xmppmaster").'</span>';
            echo '</td>';
            echo "</tr>";
            echo "</thead>";
            echo "<tbody>";
            foreach ($res as $ll) {
                $ff =  explode("' : '", $ll);
                echo "<tr>";
                echo "<td>";
                echo trim($ff[0], "'");
                echo "</td>";
                echo "<td>";
                echo '<span  style="padding-left:10px;">';
                echo trim($ff[1], "'");
                echo "</span>";
                echo "</td>";
                echo "</tr>";
            }
            echo "</tbody>";
            echo "</table>";
            echo "</div>";
        }
    }
    echo"</div>";
}

$tab = "";
?>
<form id="formpage" action="<?php echo $_SERVER['PHP_SELF']; ?>" METHODE="GET" >
    <input type="hidden" name="tab" value ="<?php echo $tab; ?>" >
    <input type="hidden" name="module" value ="<?php echo $module; ?>" >
    <input type="hidden" name="submod" value ="<?php echo $submod; ?>" >
    <input type="hidden" name="action" value ="<?php echo $action; ?>" >
    <input type="hidden" name="uuid" value ="<?php echo $uuid; ?>" >
    <input type="hidden" name="hostname" value ="<?php echo $hostname; ?>" >
    <input type="hidden" name="gid" value ="<?php echo $gid; ?>" >
    <input type="hidden" name="cmd_id" value ="<?php echo $cmd_id; ?>" >
    <input type="hidden" name="login" value ="<?php echo $login; ?>" >
    <input type="hidden" name="mach" value ="1" >
</form>


<script type="text/javascript">
    function hideid(id){
        jQuery("#"+ id).hide();
        a = jQuery("#"+"title"+id).text();
        if (a.search( '<?php echo $showText;?>' ) != -1){
            a = a.replace("<?php echo $showText;?> ", "<?php echo $hideText;?> ");
        }
        else{
            a = a.replace("<?php echo $hideText;?> ", "<?php echo $showText;?> ");
        }
        jQuery("#"+"title"+id).text(a);
    }
    //hidden table by default.decommente pour hide by default
    hideid("env");
        jQuery( ".replytab" ).click(function() {
            a = jQuery(this).text();
            if (a.search( "<?php echo $showText;?>" ) != -1){
                a = a.replace( "<?php echo $showText;?> ",  "<?php echo $hideText;?> ");
            }
            else{
                a = a.replace("<?php echo $hideText;?> ",  "<?php echo $showText;?> ");
            }
            jQuery(this).text(a);
            jQuery(this).next('div').toggle();
        });

        jQuery( ".replytab2" ).click(function() {
            a = jQuery(this).text();
            jQuery(this).text(a);
            completed = jQuery(this).next('p');
            successed = completed.next('p');
            action = jQuery(".actions");
            completed.toggle();
            successed.toggle();
            action.toggle();
        });
</script>
<?php
if (isset($_GET['gr_cmd_id'])  || $datawol['len'] != 0) {
    echo '
    <form id="formgroup" action="'.$_SERVER['PHP_SELF'].'" METHODE="GET" >
        <input type="hidden" name="tab" value ="'.$tab.'" >
        <input type="hidden" name="uuid" value ="'.$uuid.'" >
        <input type="hidden" name="gid" value ="'.$gid.'" >
        <input type="hidden" name="cmd_id" value ="'.$cmd_id.'" >
        <input type="hidden" name="login" value ="'.$login.'" >
        <input type="hidden" name="action" value ="viewlogs" >
        <input type="hidden" name="module" value ="xmppmaster" >
        <input type="hidden" name="submod" value ="xmppmaster" >
        <input type="submit" value ="group view" >
    </form>';
}

?>
