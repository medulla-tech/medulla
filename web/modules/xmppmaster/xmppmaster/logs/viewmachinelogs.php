<?php
/*
 * (c) 2017 siveo, http://www.siveo.net/
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

$p = new PageGenerator(_T("Deployment [machine ", 'xmppmaster')." ".$hostname."]");
$p->setSideMenu($sidemenu);
$p->display();

?>
<style>
.shadow
{
  -moz-box-shadow: 4px 4px 10px #888;
  -webkit-box-shadow: 4px 4px 10px #888;
  box-shadow:4px 4px 6px #888;
}

 li.folder a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.folderg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.console a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.consoleg a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quick a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guaca a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guacag a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quickg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
</style>

<?

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
include_once('modules/pulse2/includes/menu_actionaudit.php');
include_once('modules/glpi/includes/xmlrpc.php');
    // Retrieve information deploy. For cmn_id

$info = xmlrpc_getdeployfromcommandid($cmd_id, $uuid);

$deploymachine = xmlrpc_get_deployxmpponmachine($cmd_id);


    if(isset($info['objectdeploy'][0]['state']) && $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT ABORT"){
        echo "<H1>DEPLOYMENT ABORT</H1>";
    }

    $boolterminate = false;
    if(isset($info['objectdeploy'][0]['sessionid'])){
        if (isset($_POST['bStop'])){
            $_SESSION[$info['objectdeploy'][0]['sessionid']]="end";
            // if stop deploy message direct in les log
            // session for session id
            //xmlrpc_getlinelogssession($sessionxmpp);
            xmlrpc_set_simple_log('<span style="color : Orange, font-style : bold">WARNING !!! </span><span  style="color : Orange ">Request for a stop of deployment</span>',
                                    $info['objectdeploy'][0]['sessionid'], "deploy",
                                    "-1",
                                    "pulse_mmc" );
            xmlrpc_updatedeploy_states_start_and_process($info['objectdeploy'][0]['sessionid'], "DEPLOYMENT ABORT");
        }
        $sessionxmpp = $info['objectdeploy'][0]['sessionid'];
        $infodeploy = xmlrpc_getlinelogssession($sessionxmpp);
        $uuid = $info['objectdeploy'][0]['inventoryuuid'];
        foreach($infodeploy['log'] as $line){
            if ($line['text'] == "DEPLOYMENT TERMINATE" || strpos($line['text'], "DEPLOYMENT ABORT") !== false){
                $boolterminate = true;
            }
        }
    }

    $datawol = xmlrpc_getlinelogswolcmd($cmd_id,$uuid );
    //$resultinfo=(isset($info['objectdeploy'][0]['result'])?json_decode($info['objectdeploy'][0]['result']):Null);
    $resultinfo = json_decode($info['objectdeploy'][0]['result']);
    unset($info['objectdeploy'][0]['result']);
    $infoslist = $resultinfo->infoslist;
    unset($resultinfo->infoslist);
    $descriptorslist = $resultinfo->descriptorslist;
    unset($resultinfo->descriptorslist);
    $otherinfos = $resultinfo->otherinfos;
    $ipmaster = $otherinfos[0]->ipmaster;
    $iprelay =  $otherinfos[0]->iprelay;
    $ipmachine = $otherinfos[0]->ipmachine;
    unset($resultinfo->otherinfos);

    $ipmachine = $otherinfos[0]->ipmachine;
    $macstr = "";
    $macList = getMachinesMac($otherinfos[0]->uuid)[strtoupper($otherinfos[0]->uuid)];

    foreach($macList as $mac)
    {
      $macstr .= $mac;
      if(sizeof($macList) > 1 && $mac != end($macList))
        $macstr .= " || ";
    }
//     if ( isset($resultinfo->title)){
//         echo "User : $resultinfo->user "."PACKAGE ". $resultinfo->title."<br>";
//     }
   if ($datawol['len'] != 0){
        echo "<br>";
            echo "<h2 class='replytab' id='wol'>Hide Wan on Lan</h2>";
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
            foreach($datawol['log'] as $line){
                $startsteparray= get_object_vars( $line['date']);
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
    if ( $info['len'] == 0 || $boolterminate == false){
        echo'
            <script type="text/javascript">
            setTimeout(refresh, 120000);
            function  refresh(){
                jQuery( "#formpage" ).submit();
            }
        </script>
        ';
        $result = command_detail($cmd_id);
        $start_date = mktime($result['start_date'][3],
                            $result['start_date'][4],
                            $result['start_date'][5],
                            $result['start_date'][1],
                            $result['start_date'][2],
                            $result['start_date'][0]);
        $start_date = date("Y-m-d H:i:s", $start_date);
        $end_date = mktime(     $result['end_date'][3],
                                $result['end_date'][4],
                                $result['end_date'][5],
                                $result['end_date'][1],
                                $result['end_date'][2],
                                $result['end_date'][0]);
        $end_date = date("Y-m-d H:i:s", $end_date);
        echo "<h2>Please wait (".$result['title'].")</h2>";
        if(isset($info['objectdeploy'][0]['state']) &&
            ( strpos($info['objectdeploy'][0]['state'], "DEPLOYMENT START")!==false ||
              $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT DIFFERED")){
            echo "<br>Preparing deployment. Please wait...";
            echo "<img src='modules/xmppmaster/img/waitting.gif'>";
            echo "<br>";
        }
    }
    if (count($deploymachine != 0)){
        $start_datemsc = mktime( $deploymachine['startdatec'][3],
                                 $deploymachine['startdatec'][4],
                                 $deploymachine['startdatec'][5],
                                 $deploymachine['startdatec'][1],
                                 $deploymachine['startdatec'][2],
                                 $deploymachine['startdatec'][0]);

        $start_datemsc = date("Y-m-d H:i:s", $start_datemsc);

        $start_date_plan_msc = mktime(  $deploymachine['startdateh'][3],
                                        $deploymachine['startdateh'][4],
                                        $deploymachine['startdateh'][5],
                                        $deploymachine['startdateh'][1],
                                        $deploymachine['startdateh'][2],
                                        $deploymachine['startdateh'][0]);
        $start_date_plan_msc = date("Y-m-d H:i:s", $start_date_plan_msc);

        $end_date_plan_msc = mktime($deploymachine['enddateh'][3],
                                    $deploymachine['enddateh'][4],
                                    $deploymachine['enddateh'][5],
                                    $deploymachine['enddateh'][1],
                                    $deploymachine['enddateh'][2],
                                    $deploymachine['enddateh'][0]);
        $end_date_plan_msc = date("Y-m-d H:i:s", $end_date_plan_msc);

            echo "<br>";
            echo "<h2 class='replytab' id='detailmach'>"._T("Hide Machine Details","xmppmaster")."</h2>";
            echo "<div id='titledetailmach'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td style="width: 210px;">';
                                echo '<span style="padding-left: 32px;">'._T("Machine","xmppmaster").'</span>';
                            echo '</td>';

                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Ip Machine","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Mac Address","xmppmaster").'</span>';
                            echo '</td>';
                        echo "</tr>";
                    echo "</thead>";
                    echo "<tbody>";
                        echo "<tr>";
                            echo "<td>";
                                echo $hostname;
                            echo "</td>";

                            echo "<td>";
                                echo $otherinfos[0]->ipmachine;
                            echo "</td>";
                            echo "<td>";
                                echo $macstr;
                            echo "</td>";
                        echo "</tr>";
                    echo "</tbody>";
                echo "</table>";
                echo "</div>";
                echo '<br>';
                echo "<br>";
            echo "<h2 class='replytab' id='detailpack'>"._T("Hide Package Details","xmppmaster")."</h2>";
            echo "<div id='titledetailpack'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td style="width:250 ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Creator","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Name","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Folder","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: 300px;">';
                                echo '<span style=" padding-left: 32px;">'._T("Creation Date","xmppmaster").'</span>';
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
                                echo $deploymachine['package_id'];
                            echo "</td>";
                            echo "<td>";
                                echo $start_datemsc;
                            echo "</td>";
                        echo "</tr>";
                    echo "</tbody>";
                echo "</table>";
                echo "</div>";
            echo '<br>';
            echo "<h2 class='replytab' id='deployplan'>"._T("Hide Deployment plan","xmppmaster")."</h2>";
            echo "<div id='titledeployplan'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td style="width:250 ;">';
                                echo '<span style=" padding-left: 32px;">'._T("User","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Start Date","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Stop Date","xmppmaster").'</span>';
                            echo '</td>';
                        echo "</tr>";
                    echo "</thead>";
                    echo "<tbody>";
                        echo "<tr>";
                            echo "<td>";
                                echo $deploymachine['connect_as'];
                            echo "</td>";
                            echo "<td>";
                            echo $start_date_plan_msc;
                            echo "</td>";
                            echo "<td>";
                                echo $end_date_plan_msc;
                            echo "</td>";
                        echo "</tr>";
                    echo "</tbody>";
                echo "</table>";
                echo "</div>";
                echo '<br>';
        }

    if ( $info['len'] != 0)
    {
        if(isset($info['objectdeploy'][0]['state']) &&
            (   strpos($info['objectdeploy'][0]['state'], "DEPLOYMENT START")!==false ||
                $info['objectdeploy'][0]['state'] ==  "DEPLOYMENT DIFFERED")){
            if ( !$boolterminate && !isset($_POST['bStop'])){
                if (!isset($_SESSION[$info['objectdeploy'][0]['sessionid']])){
                    $f = new ValidatingForm();
                    $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
                    $f->addButton("bStop","Stop Deploy");
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
        $formateddate = substr($scalardate, 0,4).'-'.substr($scalardate, 4,2).'-'.substr($scalardate, 6,2).' '.substr($scalardate, 9);
        echo "<div>";
            echo '<H2 style="align=center;">Start deployment : '.$formateddate."</H2>";
        echo "</div>";
        if (isset($infoslist)){
            if ( $info['len'] != 0){
        $jidmachine = $info['objectdeploy'][0]['jidmachine'];
        $jid_relay = $info['objectdeploy'][0]['jid_relay'];
            echo "<br>";
            echo "<h2 class='replytab'id='xmppinfo'>"._T("Hide xmpp information","xmppmaster")."</h2>";
            echo "<div id='titlexmppinfo'>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
            echo "<thead>";
                echo "<tr>";
                    echo '<td  style="width : 120px;">';
                        echo '<span style=" padding-left: 32px;">'._T("jid machine","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td>';
                        echo '<span style=" padding-left:0px;">'._T("jid Relay server","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                    echo '<span style=" padding-left: 32px;">'._T("ip machine","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">'._T("ip relayserver","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">'._T("ip master","xmppmaster").'</span>';
                    echo '</td>';
                echo "</tr>";
            echo "</thead>";
            echo "<tbody>";
                echo "<td>";
                    echo $jidmachine;
                echo "</td>";
                echo "<td>";
                echo '<span  style="padding-left:10px;">';
                    echo $jid_relay;
                echo "</span>";
                echo "</td>";
                echo "<td>";
                echo '<span  style="padding-left:10px;">';
                    echo $ipmachine;
                echo "</span>";
                echo "</td>";
                echo "<td>";
                echo '<span  style="padding-left:10px;">';
                    echo $iprelay;
                echo "</span>";
                echo "</td>";
                echo "<td>";
                echo '<span  style="padding-left:10px;">';
                    echo $ipmaster;
                echo "</span>";
                echo "</td>";
            echo "</tr>";
        echo "</tbody>";
        echo "</table>";
        echo "</div>";
    }
            echo "<br>";
            echo "<h2 class='replytab'  id='dependency'>"._T("Hide Package and Dependency","xmppmaster")."</h2>";
            echo "<div id='titledependency'>";
                echo '<table class="listinfos" cellspacing="0" cellpadding="5">';
                    echo "<thead>";
                        echo "<tr>";
                            echo '<td style="width: 210px;">';
                                echo '<span style=" padding-left: 32px;">'._T("Name","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Software","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Version","xmppmaster").'</span>';
                            echo '</td>';
                            echo '<td style="width: ;">';
                                echo '<span style=" padding-left: 32px;">'._T("Description","xmppmaster").'</span>';
                            echo '</td>';
                        echo "</tr>";
                    echo "</thead>";
            foreach (range( 0, count($infoslist)-1) as $index){
                $inf=$infoslist[$index];
                echo "<tbody>";
                    echo "<tr>";
                        echo "<td>";
                        echo $inf->name;
                        echo "</td>";
                        echo "<td>";
                        echo $inf->software;
                        echo "</td>";
                        echo "<td>";
                            echo $inf->version;
                        echo "</td>";
                        echo "<td>";
                            echo $inf->description;
                        echo "</td>";
                    echo "</tr>";
                echo "</tbody>";
            }
            echo "</table>";
            echo "</div>";
            echo '<br>';
        }
        echo "<br>";
        echo "<h2 class='replytab id='phase'>"._T("Hide Deployment phases","xmppmaster")."</h2>";
        echo "<div id='titlephase'>";
        echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
            echo "<thead>";
                echo "<tr>";
                    echo '<td  style="width : 120px;">';
                        echo '<span style=" padding-left: 32px;">'._T("START","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td>';
                        echo '<span style=" padding-left:0px;">'._T("STEP","xmppmaster").'</span>';
                    echo '</td>';
                    echo '<td style="width: ;">';
                        echo '<span style=" padding-left: 32px;">'._T("DESCRIPTION","xmppmaster").'</span>';
                    echo '</td>';
                echo "</tr>";
            echo "</thead>";
                echo "<tbody>";
        foreach($infodeploy['log'] as $line){
            $scalardate = get_object_vars($info['objectdeploy'][0]['start'])['scalar'];
            $formateddate = substr($scalardate, 0,4).'-'.substr($scalardate, 4,2).'-'.substr($scalardate, 6,2).' '.substr($scalardate, 9);
            $startsteparray= get_object_vars( $line['date']);
            $datestartstep = date("Y-m-d H:i:s", $startsteparray['timestamp']);
            echo '<tr class="alternate">';
                echo "<td>";
                    echo $formateddate;
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
                              "actionsuccescompletedend" =>"Deployment terminated successfully. Clean package",
                              "actioncleaning"  =>"Clean downloaded package",
                              "actionrestartbot" => "Restart agent",
                              "actionrestart" => "Restart Machine",
                              "action_unzip_file" => "unzip file",
                              "action_set_environ" => "Initializes environment variables",
                              "action_no_operation" => "no action",
        );
    if (isset($descriptorslist)){
        echo "<br>";
        echo "<h2 class='replytab' id='result'>Hide Deployment result</h2>
        <div id='titleresult'>";
        echo "<pre style='  box-shadow: 6px 6px 0px black;
                            border-radius: 20px / 10px;
                            border-left: 2px solid black;
                            border-right: 2px solid black;
                            border-top: 2px solid black;
                            padding: 10px 10px 5px 10px;'>";
        foreach (range( 0, count($descriptorslist)-1) as $index1){
            $arraylist= $descriptorslist[$index1];
            echo "<div>";
            echo "<span class='replytab' style='color : blue; font: italic bold 12px/30px Georgia, serif;'>Hide Result " . $infoslist[$index1]->name."</span>";
            echo "<div>";
            foreach (range( 0, count($arraylist)-1) as $index){
                $step=$arraylist[$index];
                if (array_key_exists($step->action, $actionsname)) {
                    $actions = $actionsname[$step->action];
                }
                else{
                    $actions = ltrim(str_replace("_"," ",substr($step->action,6)));
                    echo $step->action;
                }
                $color="red";
                echo "<br>";
                if (isset($step->completed) && $actions != "ERROR"){
                    echo '<h3 style="color:green;">STEP'." <strong>".$step->step. " [". $actions. "]</strong>" ."". "  </h3>";
                    $color="green";
                }

                if (isset($step->completed)){
                    echo '<div class="shadow"
                                style="  color:'.$color.';
                                        display: none;
                                            padding:0 10px;">';
                    foreach($step as $keystep => $infostep){
                        if ($keystep != "step" and $keystep != "action" and  $keystep != "completed"){
                            if( strstr($keystep, "resultcommand")) {
                            echo "<pre>";
                                //echo nl2br($infostep);
                                echo $keystep." :".$infostep."<br>";
                            echo "</pre>";
                            }
                            else{
                                if (is_object ($infostep)) {

                                    echo $keystep;
                                    echo "<br>";
                                    echo "<ul>";
                                    foreach(get_object_vars ($infostep) as $key0 => $valu0){
                                        if ($key0 =='') break;
                                        echo'<li>'.$key0.'=>'.$valu0 .'</li>';
                                    }
                                    echo "</ul>";
                                }
                                else{
                                    echo $keystep." :".$infostep."<br>";
                                }
                            }
                        }
                    }
                }
                else{
                    echo '<div class="shadow" style="  color:blue; display: none;
                                        font-size:10px;
                                        font-style: italic;
                                        padding:0 10px;">';
                    foreach($step as $keystep => $infostep){
                        if ($keystep != "step" and $keystep != "action" and  $keystep != "completed")
                            echo $keystep." :".$infostep."<br>";
                        }
                }
                    echo "</div>";
            }
            echo"</div>";
        }
            echo "</pre>";
            echo"</div>";
    }
    if (isset($otherinfos[0]->environ) && count((array)$otherinfos[0]->environ) == 1){
        if ( $info['len'] != 0){
            $res = str_replace ( "{'", "'" ,$otherinfos[0]->environ);
            $res = str_replace ( "'}", "'" ,$res);
            $res = str_replace ( "  ", " " ,$res);
            $res = str_replace ( "  ", " " ,$res);
            $res = str_replace ( "  ", " " ,$res);
            $res = str_replace ( "': '", "' : '" ,$res);
            $res = str_replace ( "', '", "' , '" ,$res);
            $res = str_replace ( "\\\\", "\\" ,$res);
            $res = str_replace ( "C:\\", "C:\\\\" ,$res);
            $res = explode ( "' , '" , $res);
            echo "<br>";
            echo "<h2 class='replytab' id='titleenv' >"._T("Hide Environment","xmppmaster")."</h2>";
            echo "<div id='env'>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="2" border="1">';
            echo "<thead>";
                echo "<tr>";
                    echo '<td  style="width : 120px;">';
                        echo '<span style=" padding-left: 32px;">"._T("key","xmppmaster")."</span>';
                    echo '</td>';
                    echo '<td>';
                        echo '<span style=" padding-left:0px;">"._T("value","xmppmaster")."</span>';
                    echo '</td>';
                echo "</tr>";
            echo "</thead>";
            echo "<tbody>";
            foreach ($res as $ll){
                    $ff =  explode ( "' : '" , $ll);
                    echo "<tr>";
                    echo "<td>";
                    echo trim($ff[0],"'");
                    echo "</td>";
                    echo "<td>";
                    echo '<span  style="padding-left:10px;">';
                    echo trim($ff[1],"'");
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

    $tab="";
?>
<form id="formpage" action="<? echo $_SERVER['PHP_SELF']; ?>" METHODE="GET" >
    <input type="hidden" name="tab" value ="<? echo $tab; ?>" >
    <input type="hidden" name="module" value ="<? echo $module; ?>" >
    <input type="hidden" name="submod" value ="<? echo $submod; ?>" >
    <input type="hidden" name="action" value ="<? echo $action; ?>" >
    <input type="hidden" name="uuid" value ="<? echo $uuid; ?>" >
    <input type="hidden" name="hostname" value ="<? echo $hostname; ?>" >
    <input type="hidden" name="gid" value ="<? echo $gid; ?>" >
    <input type="hidden" name="cmd_id" value ="<? echo $cmd_id; ?>" >
    <input type="hidden" name="login" value ="<? echo $login; ?>" >
    <input type="hidden" name="mach" value ="1" >
</form>
<script type="text/javascript">
    function hideid(id){
        jQuery("#"+ id).hide();
        a = jQuery("#"+"title"+id).text();
        if (a.search( 'Show' ) != -1){
            a = a.replace("Show ", "Hide ");
        }
        else{
            a = a.replace("Hide ", "Show ");
        }
        jQuery("#"+"title"+id).text(a);
    }
    //hidden table by default.decommente pour hide by default
    hideid("env");
    // hideid("wol");
    // hideid("result");
    // hideid("detailmach");
    // hideid("detailpack");
    // hideid("deployplan");
    // hideid("xmppinfo");
    // hideid("dependency");
    // hideid("phase");
      jQuery( "h3" ).click(function() {
        jQuery(this).css('background-color','white')
        jQuery(this).next('div').toggle();
        });
        jQuery( ".replytab" ).click(function() {
            a = jQuery(this).text();
            if (a.search( 'Show' ) != -1){
                a = a.replace("Show ", "Hide ");
            }
            else{
                a = a.replace("Hide ", "Show ");
            }
            jQuery(this).text(a);
            jQuery(this).next('div').toggle();
        });
</script>
<?
if (isset($_GET['gr_cmd_id'] )  || $datawol['len'] != 0){
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
