<?php
/**
 * (c) 2017 Siveo, http://http://www.siveo.net
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
 * file viewgrouplogs.in.php
 */
//jfkjfk
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
echo '
<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.line-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.bar-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>';

$nbdeploy = 0;
$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment [ group",'xmppmaster')." ". $group->getName()."]");
$p->setSideMenu($sidemenu);
$p->display();

$resultfrommsc = xmlrpc_getstatbycmd($cmd_id);
$total_machine_from_msc  = $resultfrommsc['nbmachine'];
$nb_machine_deployer_from_msc     = $resultfrommsc['nbdeploydone'];
$nb_deployer_machine_yet_from_msc = $total_machine_from_msc - $total_machine_from_msc;

$convergenceonpackage = is_commands_convergence_type($cmd_id);
$command_detail = command_detail($cmd_id);

$lastcommandid = get_last_commands_on_cmd_id($cmd_id);
$start_date = mktime(   $lastcommandid['start_date'][3],
                        $lastcommandid['start_date'][4],
                        $lastcommandid['start_date'][5],
                        $lastcommandid['start_date'][1],
                        $lastcommandid['start_date'][2],
                        $lastcommandid['start_date'][0]);

$resultfromdeploy = xmlrpc_getstatdeployfromcommandidstartdate(   $cmd_id,
                                                        date("Y-m-d H:i:s", $start_date));
$total_machine_from_deploy     = $resultfromdeploy['totalmachinedeploy'];
$machine_error_from_deploy     = $resultfromdeploy['machineerrordeploy'];
$machine_success_from_deploy   = $resultfromdeploy['machinesuccessdeploy'];
$machine_process_from_deploy   = $resultfromdeploy['machineprocessdeploy'];
$machine_wol_from_deploy       = $totalmachinedeploy-($machineerrordeploy + $machinesuccessdeploy + $machineprocessdeploy);


$end_date = mktime(     $lastcommandid['end_date'][3],
                        $lastcommandid['end_date'][4],
                        $lastcommandid['end_date'][5],
                        $lastcommandid['end_date'][1],
                        $lastcommandid['end_date'][2],
                        $lastcommandid['end_date'][0]);
$timestampnow = time();
echo "<br>";

$start_deploy = 0;
$end_deploy   = 0;
if ($timestampnow > $start_date){
    $start_deploy = 1;
}

if ($timestampnow > ($end_date)){
    $end_deploy = 1;
};

$terminate = 0;
$deployinprogress = 0;
echo "Deployment programming between [".date("Y-m-d H:i:s", $start_date)." and ".date("Y-m-d H:i:s", $end_date)."]";
if ($convergenceonpackage !=0 ){
    echo "<img style='position:relative;top : 5px;' src='modules/msc/graph/images/install_convergence.png'/>";
}
echo "<br>";


function urlredirect_group_for_deploy($typegroup, $g_id, $login_deploy , $cmddeploy_id ){
    $urlRedirect1 = urlStrRedirect("base/computers/createMachinesStaticGroupdeploy&gid=".$g_id."&login=".$login_deploy."&cmd_id=".$cmddeploy_id."&type=".$typegroup);
    return $urlRedirect1;
}

$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");

#jfk
if (!isset($_GET['refresh'])){
    $_GET['refresh'] = 1;
}

if (isset($_GET['gid'])){
    $countmachine = getRestrictedComputersListLen( array('gid' => $_GET['gid']));
    $_GET['nbgrp']=$countmachine;
}
$nbsuccess = 0;
foreach ($info['objectdeploy'] as $val)
{
   $_GET['id']  .= $val['inventoryuuid']."@@";
   $_GET['ses'] .= $val['sessionid']."@@";
   $_GET['hos'] .= explode("/", $val['host'])[1]."@@";
   $_GET['sta'] .=  $val['state']."@@";
   if ($val['state'] == "DEPLOYMENT SUCCESS"){
        $nbsuccess ++;
   }
}
if (isset($countmachine) && ($info['len'] == $countmachine)){
    $terminate = 1;
    $deployinprogress = 0;
}

if ( $start_deploy){
    echo "<br>";
    if ($end_deploy || $terminate == 1){
        echo "<h2>Deployment to complete</h2>";
        $terminate = 1;
        $deployinprogress = 0;
        echo "<br>";
    }else{
        echo "<h2>Deployment in progress</h2>";
        echo "START DEPLOY From <span>".($timestampnow - $start_date)."</span> s";
        $deployinprogress = 1;
    }
}
else{
    echo "WAITING FOR START ".date("Y-m-d H:i:s", $start_date);
}

    if ($deployinprogress ){
        $f = new ValidatingForm();
        $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
        $f->addButton("bStop", _T("Stop Deploy", 'xmppmaster'));
        $f->display();
    }

    $evolution  = round(($nb_machine_deployer_from_msc / $total_machine_from_msc) * 100,2);
    $Success    = round(($machine_success_from_deploy / $total_machine_from_msc) * 100,2);
    $error      = round(($machine_error_from_deploy / $total_machine_from_msc) * 100,2);
    $process    = round(($machine_process_from_deploy / $total_machine_from_msc) * 100,2);
    
    //
    $deploymachine = $machine_success_from_deploy + $machine_error_from_deploy;
    echo '<div class="bars">';
        echo '<span style="width: 200px;">';
            echo'<progress class="mscdeloy" data-label="50% Complete" max="'.$total_machine_from_msc.'" value="'.$nb_machine_deployer_from_msc.'" form="form-id"></progress>';
        echo '</span>';
    echo'<span style="margin-left:10px">deployemt '.$evolution.'%</span>';
    
    $wol = ($total_machine_from_msc-$total_machine_from_deploy);
    echo "<br><br>Number of machines in the deployment group. : ".$total_machine_from_msc;
    echo "<br>Number of machines in the group : ".$countmachine;
    echo "<br>Number of machines being deployed : ". $deploymachine;

    echo "<br>Deploy";
    echo "<table><tr>";
    echo "<td>sucess</td>
        <td>error</td>
        <td>progress</td>
        <td>Waiting</td>";
    echo "</tr>
    <tr>";
    echo "<td>".$machine_success_from_deploy."</td>
        <td>".$machine_error_from_deploy."</td>
        <td>".$machine_process_from_deploy."</td>
        <td>".$wol."</td>";
    echo "</tr></table>";
echo '</div>';
      echo'<div  style="float:left; height: 120px" id="holder"></div>';
echo "<br>";
    if ($info['len'] != 0){
        $uuid=$info['objectdeploy'][0]['inventoryuuid'];
        $state=$info['objectdeploy'][0]['state'];
        $start=get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
        $result=$info['objectdeploy'][0]['result'];

        $resultatdeploy =json_decode($result, true);
        $host=$info['objectdeploy'][0]['host'];
        $jidmachine=$info['objectdeploy'][0]['jidmachine'];
        $jid_relay=$info['objectdeploy'][0]['jid_relay'];

        $datestart =  date("Y-m-d H:i:s", $start);
        $timestampstart = strtotime($datestart);
        $timestampnow = time();
        $nbsecond = $timestampnow - $timestampstart;

       if (isset($resultatdeploy['descriptor']['info'])){
        echo "<br>";
        echo "<h2>Package</h2>";
            echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
                echo "<thead>";
                    echo "<tr>";
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Name</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Software</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Version</span>';
                        echo '</td>';
                        echo '<td style="width: ;">';
                            echo '<span style=" padding-left: 32px;">Description</span>';
                        echo '</td>';
                    echo "</tr>";
                echo "</thead>";
                echo "<tbody>";
                    echo "<tr>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['description'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['name'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['software'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['version'];
                        echo "</td>";
                    echo "</tr>";
                echo "</tbody>";
            echo "</table>";
            echo '<br>';
      }
}

        echo'
            <script type="text/javascript">
            console.log("hello");
                setTimeout(refresh, 10000);
                function  refresh(){
                        location.reload()
                }
            </script>
            ';
echo "<br>";echo "<br>";echo "<br>";echo "<br>";echo "<br>";echo "<br>";echo "<br>";echo "<br>";
$group->prettyDisplay();


        if (isset($countmachine)){
            if ($info['len'] > $countmachine){
                $info['len'] = $countmachine;
        }
        if ($nbsuccess > $countmachine){
                $nbsuccess = $countmachine;
        }
    }

if ($info['len'] != 0){
    $gr   = getRestrictedComputersList(0,-1, array('gid' =>$gid));
    $uuidgr = array();
    $uuidsuccess = array();
    $uuiderror = array();
    $uuidprocess = array();
    $uuiddefault = array();
    $uuidall = array();
    $uuidwol = array();

    foreach ($gr as $key => $val){
        $uuidgr[] =  $key;
    }

    foreach ($info['objectdeploy'] as  $val){

        switch($val['state']){
            case "DEPLOYMENT SUCCESS":
                $uuidsuccess[] = $val['inventoryuuid'];
                break;
            case "DEPLOYMENT ERROR":
                $uuiderror[] = $val['inventoryuuid'];
                break;
            case "DEPLOYMENT START":
                $uuidprocess[] = $val['inventoryuuid'];
                break;
            default:
                $uuiddefault[] = $val['inventoryuuid'];
        }
        $uuidall[] = $val['inventoryuuid'];
    }
    $other            = count ( $uuiddefault );
    $machinesucess    = count ( $uuidsuccess );
    $machineerror     = count ( $uuiderror );
    $machineinprocess = count ( $uuidprocess );
    $machinewol       = $stat['nbmachine']-$stat['nbdeploydone'];

        echo '
        <script>
            var u = "";
            var r = "";
            window.onload = function () {
                var datadeploy = new Array();
                var legend = new Array();
                var href = new Array();
                var color = new Array();
                ';

                if ($machinesucess > 0){
                    echo 'datadeploy.push('.$machine_success_from_deploy.');';
                    echo 'legend.push("%%.%% - Machines deploy in sucess");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machinesucess",$_GET['gid'], $_GET['login'], $cmd_id).'");';
                    echo 'color.push("#2EFE2E");';
                }
                if ($machineerror > 0){
                    echo 'datadeploy.push('.$machine_error_from_deploy.');';
                    echo 'legend.push("%%.%% - Machines deploy in error");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machineerror",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#FE2E64");';
                }
                if ($machineinprocess > 0){
                    echo 'datadeploy.push('.$machine_process_from_deploy.');';
                    echo 'legend.push("%%.%% - Machines deploy in process");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machineprocess",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#2E9AFE");';
                }
                if ($machinewol > 0){
                    echo 'datadeploy.push('.$machine_wol_from_deploy.');';
                    echo 'legend.push("%%.%% - Waiting for machine start (WOL send).");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machinewol",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#DBA901");';
                }
                echo'
                r = Raphael("holder"),
                    pie = r.piechart(100, 60, 50, datadeploy, 
                        {   legend: legend,
                            legendpos: "est", 
                            href: href,
                            colors: color
                        }
                    );

                r.text(210, 50, "Deploy Machines").attr({ font: "20px sans-serif" });

                pie.hover(function () {
                    u = this;                 // My Code   
                    u.onclick = clickEvent;   //  hook to the function 
                this.sector.stop();
                    this.sector.scale(1.1, 1.1, this.cx, this.cy);  // Scale slice 

                    if (this.label) {                               // Scale button and bolden text 
                        this.label[0].stop();
                        this.label[0].attr({ r: 7.5 });
                        this.label[1].attr({ "font-weight": 800 });
                    }
                }, function () {
                    this.sector.animate({ transform: \'s1 1 \' + this.cx + \' \' + this.cy }, 500, "bounce");


                    if (this.label) {
                        this.label[0].animate({ r: 5 }, 1500, "bounce");
                        this.label[1].attr({ "font-weight": 400 });
                    }
                });

            };
            function clickEvent(){
                console.log("Clicked!")
            }
        </script>';
    }
  
 
    
?>
<style> 
li.remove_machine a {
        /*padding: 1px 3px 5px 20px;*/
       /* margin: 0 0px 0 0px;*/
        background-image: url("img/common/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

progress{
    border-color: #ffffff;
    background-color: #009ea9; 
}
progress.mscdeloy{
    width: 390px; 
    background-color: #00f3f3; 
}

progress::-webkit-progress-bar {
    background: #00f3f3 ;
}

progress::-webkit-progress-value {
     Background: #009ea9;
}
progress::-moz-progress-bar {
  background-color:blue;
}


.bars{
    width: 400px;
    float:left;
}
</style>
