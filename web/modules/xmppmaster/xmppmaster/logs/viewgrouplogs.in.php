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

$stat = xmlrpc_getstatbycmd($cmd_id);
$ddd = get_first_commands_on_cmd_id($cmd_id);
$start_date = mktime( $ddd['start_date'][3],  $ddd['start_date'][4], $ddd['start_date'][5], $ddd['start_date'][1], $ddd['start_date'][2], $ddd['start_date'][0]);
$end_date = mktime( $ddd['end_date'][3],  $ddd['end_date'][4], $ddd['end_date'][5], $ddd['end_date'][1], $ddd['end_date'][2], $ddd['end_date'][0]);
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
echo "<br>";



function urlredirect_group_for_deploy($typegroup, $g_id, $login_deploy , $cmddeploy_id ){
    $urlRedirect1 = urlStrRedirect("base/computers/createMachinesStaticGroupdeploy&gid=".$g_id."&login=".$login_deploy."&cmd_id=".$cmddeploy_id."&type=".$typegroup);
    return $urlRedirect1;
}
/*
    function urlredirect_group_for_deploy(){
    return $urlRedirect1;
}*/
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
   if ($val['state'] == "END SUCESS"){
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

    echo'<br><progress max="'.$stat['nbmachine'].'" value="'.$stat['nbdeploydone'].'" form="form-id"></progress>';
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
else{

   // if ($terminate != 0){
        echo'
            <script type="text/javascript">
            console.log("hello");
                setTimeout(refresh, 10000);
                function  refresh(){
                        location.reload()
                }
            </script>
            ';
    //}
}

$group->prettyDisplay();
?>


<?
        if (isset($countmachine)){
            if ($info['len'] > $countmachine){
                $info['len'] = $countmachine;
        }
        if ($nbsuccess > $countmachine){
                $nbsuccess = $countmachine;
        }
        echo ' <div>';
        echo'<div style="float:left;" id="holder"></div>';
        echo '<div style="float:left;">';
                echo "<br>";
                echo "Number of machines in the deployment group. : ".$stat['nbmachine'];
                echo "<br>";
                echo "Number of machines in the group. : ".$countmachine;
                echo "<br>";
                echo "Number of machines being deployed : ". $info['len'];
                echo "<br>";
                echo "Number of deployments that succeeded : ". $nbsuccess;
                echo "<br>";
                $sucessdeploy = $nbsuccess / $countmachine * 100;
                $machinedeploy = $info['len'] / $countmachine;
                $machinewokonlan = (1 - $machinedeploy) * 100;
                $machinedeploy = $machinedeploy * 100;
                echo " Succes : ".round($sucessdeploy, 2)."%";
                echo "<br>";
                echo " Machine deploy in group : ".round($machinedeploy, 2)."%";
                echo "<br>";
                echo " Machine where we tried an WOL: ".round($machinewokonlan, 2)."%";
                echo "<br>";
                $nbdeploy = $info['len'];
                $nberror = $nbdeploy - $nbsuccess;
            echo "</div>";
         echo ' </div>';
    }

    ?>
   
    <?
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
            case "END SUCESS":
                $uuidsuccess[] = $val['inventoryuuid'];
                break;
            case "END ERROR":
                $uuiderror[] = $val['inventoryuuid'];
                break;
            case "STARDEPLOY":
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
                    echo 'datadeploy.push('.$machinesucess.');';
                    echo 'legend.push("%%.%% - Machines deploy in sucess");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machinesucess",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#2EFE2E");';
                }
                if ($machineerror > 0){
                    echo 'datadeploy.push('.$machineerror.');';
                    echo 'legend.push("%%.%% - Machines deploy in error");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machineerror",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#FE2E64");';
                }
                if ($machineinprocess > 0){
                    echo 'datadeploy.push('.$machineinprocess.');';
                    echo 'legend.push("%%.%% - Machines deploy in process");';
                    echo 'href.push("'.urlredirect_group_for_deploy("machineprocess",$_GET['gid'],$_GET['login'],$cmd_id).'");';
                    echo 'color.push("#2E9AFE");';
                }
                if ($machinewol > 0){
                    echo 'datadeploy.push('.$machinewol.');';
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
        padding: 1px 3px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("img/common/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}


progress {
  width: 400px;
  height: 9px;
  margin:-5px;
  background-color: #ffffff;   /* Couleur de fond */
  border-style: solid;   /* Style de la bordure  */
  border-width: 1px;   /* Epaisseur de la bordure  */
  border-color: #dddddd;   /* Couleur de la bordure  */
  padding: 3px 3px 3px 3px;   /* Espace entre les bords et le contenu : haut droite bas gauche  */
}
 
progress::-webkit-progress-bar {
    background: #f3f3f3 ;
}

progress::-webkit-progress-value {
     Background: #ef9ea9;
}

</style>
