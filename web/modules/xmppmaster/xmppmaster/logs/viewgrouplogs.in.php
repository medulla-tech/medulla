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

$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment [ group",'xmppmaster')." ". $group->getName()."]");
$p->setSideMenu($sidemenu);
$p->display();


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
if ($timestampnow > ($end_date + 900)){
    $end_deploy = 1;
};


$terminate = 0;
$deployinprogress = 0;
echo "Deployment programming between [".date("Y-m-d H:i:s", $start_date)." and ".date("Y-m-d H:i:s", $end_date)."]";
echo "<br>";

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
    echo "START DEPLOY From <span>".($timestampnow - $start_date)."</span> s";
    echo "<br>";
    if ($end_deploy || $terminate == 1){
        echo "DEPLOY TERMINATE";
        $terminate = 1;
        $deployinprogress = 0;
        echo "<br>";
    }else{
        echo "DEPLOY  in Progress";
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
//     $_GET['refresh'] = $_GET['refresh'] + 1;
    if ($terminate == 0){
        echo'
            <script type="text/javascript">
                setTimeout(refresh, 10000);
                function  refresh(){
                        location.reload()
                }
            </script>
            ';
   }
}

$group->prettyDisplay();

if (isset($countmachine)){
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
        echo " Succes : ".$sucessdeploy."%";
        echo "<br>";
        echo " Machine deploy in group : ".$machinedeploy."%";
        echo "<br>";
        echo " Machine or we tried an WOL: ".$machinewokonlan."%";
        echo "<br>";
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
</style>
