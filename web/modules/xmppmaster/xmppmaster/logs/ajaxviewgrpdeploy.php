<?php
/*
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
//require("modules/base/computers/localSidebar.php");
require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
?>
<script src="jsframework/d3/d3.js"></script>
<style>
    li.groupshare a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/dyngroup/img/share.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
    }
</style>
<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

extract($_GET);

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = (isset($_GET['start']))? $_GET['start']: 0;
$end   = (isset($_GET['end'])?$_GET['end']+$maxperpage:$maxperpage);

function urlredirect_group_for_deploy($typegroup, $g_id, $login_deploy , $cmddeploy_id ){
    $urlRedirect1 = urlStrRedirect("base/computers/createMachinesStaticGroupdeploy&gid=".$g_id."&login=".$login_deploy."&cmd_id=".$cmddeploy_id."&type=".$typegroup);
    return $urlRedirect1;
}

$nbdeploy = 0;
$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment [ group",'xmppmaster')." ". $group->getName()."]");
$p->setSideMenu($sidemenu);
$p->display();

//FROM MSC BASE
// search nbmachinegroupe in group, and nbdeploydone already deployed from mmc
$resultfrommsc = xmlrpc_getstatbycmd($cmd_id, $filter, $start, $end);

$MSC_nb_mach_grp_for_deploy  = $resultfrommsc['nbmachine'];
$MSC_nb_mach_grp_done_deploy     = $resultfrommsc['nbdeploydone'];
//$nb_deployer_machine_yet_from_msc = $MSC_nb_mach_grp_for_deploy - $MSC_nb_mach_grp_for_deploy;

$bool_convergence_grp_on_package_from_msc = is_commands_convergence_type($cmd_id, $filter, $start, $end);
// $command_detail = command_detail($cmd_id);


// search from msc table CommandsOnHost
$lastcommandid = get_last_commands_on_cmd_id_start_end($cmd_id, $filter, $start, $end);
$start_date =  $lastcommandid['start_dateunixtime'];
$end_date = $lastcommandid['end_dateunixtime'];
$timestampnow = time();

//$uuids = xmlrpc_get_msc_listuuid_commandid($cmd_id, $filter, 0, 10000);
$uuids = xmlrpc_get_msc_listuuid_commandid($cmd_id, $filter, -1, -1);
$uuids_list = $uuids['list'];



$re = xmlrpc_get_machine_for_id($uuids_list, $filter, $start, $maxperpage);
$info_from_machines = $re["listelet"];
$count = $re['total'];
//FROM XMPPMASTER
$resultfromdeploy = xmlrpc_getstatdeployfromcommandidstartdate( $cmd_id,
                                                                date("Y-m-d H:i:s",
                                                                $start_date));

$total_machine_from_deploy     = $resultfromdeploy['totalmachinedeploy'];
$machine_error_from_deploy     = $resultfromdeploy['machineerrordeploy'];
$machine_success_from_deploy   = $resultfromdeploy['machinesuccessdeploy'];
$machine_process_from_deploy   = $resultfromdeploy['machineprocessdeploy'];
$machine_abort_from_deploy     = $resultfromdeploy['machineabortdeploy'];

// from msc
$machine_timeout_from_deploy   = xmlrpc_get_count_timeout_wol_deploy( $cmd_id,
                                                                date("Y-m-d H:i:s",
                                                                $start_date));

$machine_wol_from_deploy       = $total_machine_from_deploy-($machine_success_from_deploy + $machine_success_from_deploy + $machine_process_from_deploy + $machine_timeout_from_deploy);

$terminate = 0;
$deployinprogress = 0;

$waiting = $MSC_nb_mach_grp_for_deploy - ($total_machine_from_deploy + $machine_timeout_from_deploy);

// $evolution
if ($waiting == 0 && $machine_process_from_deploy == 0 ){
    $terminate = 1;
}
echo "<br><br><br><br><br>";

$start_deploy = 0;
$end_deploy   = 0;
if ($timestampnow > $start_date){
    $start_deploy = 1;
}

if ($timestampnow > ($end_date)){
    $end_deploy = 1;
};

// This command gets associated group of cmd_id
$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");
echo "Deployment schedule: ".date("Y-m-d H:i:s", $start_date)." -> ".date("Y-m-d H:i:s", $end_date)."<br>";
$statsyncthing  = xmlrpc_stat_syncthing_transfert($_GET['gid'],$_GET['cmd_id'] );
    if ($statsyncthing['package'] == ""){
        echo _T("Syncthing sharing done or non-existant");
    }else{
echo "<div style='width :100%; color:blue;'>";
    echo "<table><tr><td>";
    echo'
            <table>
            <tr>
                <th >'. _T("Syncthing share", "xmppmaster"). '</th>
                <th >'. _T("Number of machines", "xmppmaster"). '</th>
                <th >'. _T("transfert", "xmppmaster"). '</th>
            </tr>
            <tr>
                <td rowspan="2">';
                            echo _T("Share name", "xmppmaster")." : ". $statsyncthing['package'];
                            echo '<br />';
                            echo _T("Number of participants", "xmppmaster")." : ".$statsyncthing['nbmachine'];
                            echo '<br />';
                            echo _T("Transfer progress", "xmppmaster")." : ".$statsyncthing['progresstransfert'].' %';
                            echo '<br />';
                echo '</td>';

                $entete = "";
                foreach ( $statsyncthing['distibution']['data_dist'] as $arrayval){
                    echo $entete ."
                            <td>$arrayval[1]</td>
                            <td>$arrayval[0]%</td>
                        </tr>";
                        if ($entete==""){$entete = "<tr>";}
                }

                echo '</table>';
        echo "</td>
        <td>
        <input id='buttontransfertsyncthing' class='btn btn-primary' type='button' value='show transfert'></td>
        </td>
        </tr>
        </table>";

    echo "<div>";
        echo "<div id='tablesyncthing'>";
?>
        <table id="tablelog" width="100%" border="1" cellspacing="0" cellpadding="1" class="listinfos">
                <thead>
                    <tr>
                        <th style="width: 12%;"><?php echo _('cluster list'); ?></th>
                        <th style="width: 7%;"><?php echo _('cluster nb ars'); ?></th>
                        <th style="width: 7%;"><?php echo _('machine'); ?></th>
                        <th style="width: 7%;"><?php echo _('progress'); ?></th>
                        <th style="width: 7%;"><?php echo _('start'); ?></th>
                        <th style="width: 7%;"><?php echo _('end'); ?></th>
                    </tr>
                </thead>
            </table>
<?php
        echo "</div>";
    echo "</div>";
    echo "<Hr>";
    echo '</div>';
}
?>
<script type="text/javascript">
    function searchlogs(url){
                            jQuery('#tablelog').DataTable({
                            'retrieve': true,
                            "iDisplayLength": 5,
                            "dom": 'rt<"bottom"fp><"clear">',
                            'order': [[ 0, "desc" ]]
                        } )
                            .ajax.url(
                                url
                            )
                            .load();
    }

    jQuery(function(){
        searchlogs("modules/xmppmaster/xmppmaster/ajaxsyncthingmachineless.php?grp=<?php echo $_GET['gid']; ?>&cmd=<?php echo $cmd_id ?>")
    } );

jQuery( "#tablesyncthing" ).hide();
var levelshow = 0;
jQuery( "#buttontransfertsyncthing" ).click(function() {
    //jQuery( "#tablesyncthing" ).toggle();

    if (levelshow == 0){
        jQuery( "#tablesyncthing" ).show();
        levelshow = 1;
    }else{
        document.location.reload();
    }
});
    </script>

<?php
if ($info['len'] != 0){
    $result=$info['objectdeploy'][0]['result'];

    $resultatdeploy =json_decode($result, true);
    $host=$info['objectdeploy'][0]['host'];
    $jidmachine=$info['objectdeploy'][0]['jidmachine'];
    $jid_relay=$info['objectdeploy'][0]['jid_relay'];
}

if ($bool_convergence_grp_on_package_from_msc !=0 ){
    echo "<img style='position:relative;top : 5px;' src='modules/msc/graph/images/install_convergence.png'/>";
}
echo "<br>";

if (isset($resultatdeploy['infoslist'][0]['packageUuid'])){
    echo "Package : ".$resultatdeploy['infoslist'][0]['name']." [". $resultatdeploy['infoslist'][0]['packageUuid']."]";
    echo "<br>";
}

if (!isset($_GET['refresh'])){
    $_GET['refresh'] = 1;
}
if (isset($_GET['gid'])){
    $countmachine = getRestrictedComputersListLen( array('gid' => $_GET['gid']));
    $_GET['nbgrp']=$countmachine;
}
$nbsuccess = 0;
$_GET['id']=isset($_GET['id']) ? $_GET['id'] : "";
$_GET['ses']=isset($_GET['ses']) ? $_GET['ses'] : "";
$_GET['hos']=isset($_GET['hos']) ? $_GET['hos'] : "";
$_GET['sta']=isset($_GET['sta']) ? $_GET['sta'] : "";

foreach ($info['objectdeploy'] as $val)
{
   $_GET['id']  .= $val['inventoryuuid']."@@";
   $_GET['ses'] .= $val['sessionid']."@@";
   $hostlocal = explode("/", $val['host']);

   $hostlocal1 = isset($hostlocal[1]) ? $hostlocal[1] : "";

   $_GET['sta'] .=  $val['state']."@@";
   if ($val['state'] == "DEPLOYMENT SUCCESS"){
        $nbsuccess ++;
   }
}
// if (isset($countmachine) && ($info['len'] == $countmachine)){
//     $terminate = 1;
//     $deployinprogress = 0;
// }


//start deployement status
echo "<div>";
    if ( $start_deploy){
        echo "<br>";
        if ($end_deploy || $terminate == 1){
            echo "<h2>"._T("Deployment completed","xmppmaster")."</h2>";
            $terminate = 1;
            $deployinprogress = 0;
            echo "<br>";
        }else{
            echo "<h2>"._T("Deployment in progress","xmppmaster")."</h2>";
            echo _T("Started since","xmppmaster")." <span>".($timestampnow - $start_date)."</span> s";
            $deployinprogress = 1;
        }
    }
    else{
        echo _T("WAITING FOR START ","xmppmaster").date("Y-m-d H:i:s", $start_date);
    }

        //if ($deployinprogress ){
    if($terminate == 0){
        $f = new ValidatingForm();
        $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
        $f->addButton("bStop", _T("Abort Deployment", 'xmppmaster'));
        $f->display();
    }
    echo "<br>";

        $nb_machine_deployer_avec_timeout_deploy = $machine_timeout_from_deploy + $MSC_nb_mach_grp_done_deploy;
        $evolution  = round(($nb_machine_deployer_avec_timeout_deploy / $MSC_nb_mach_grp_for_deploy) * 100,2);
        $deploymachine = $machine_success_from_deploy + $machine_error_from_deploy;
        echo '<div class="bars">';
            echo '<span style="width: 200px;">';
                echo'<progress class="mscdeloy" data-label="50% Complete" max="'.$MSC_nb_mach_grp_for_deploy.'" value="'.$nb_machine_deployer_avec_timeout_deploy .'" form="form-id"></progress>';
            echo '</span>';
        echo'<span style="margin-left:10px">Deployment '.$evolution.'%</span>';

        $wol = ( $MSC_nb_mach_grp_for_deploy - ( $total_machine_from_deploy + $machine_timeout_from_deploy ));
        echo "<br><br>"._T("Number of machines in the group","xmppmaster")." : ".$MSC_nb_mach_grp_for_deploy;
        echo "<br>"._T("Number of current deployments","xmppmaster")." : ". $deploymachine;
        echo "<br>"._T("Number of deployments in timeout","xmppmaster").": ". $machine_timeout_from_deploy;
        echo "<br>"._T("Deployment summary","xmppmaster").":";
        echo "<table><tr>";
        echo "<td>"._T("Success","xmppmaster")."</td>
            <td>"._T("Error","xmppmaster")."</td>
            <td>"._T("In progress","xmppmaster")."</td>
            <td>"._T("Waiting","xmppmaster")."</td>
            <td>"._T("Timed out","xmppmaster")."</td>
            <td>"._T("Aborted","xmppmaster")."</td>";
        echo "</tr>
        <tr>";
        echo "<td>".$machine_success_from_deploy."</td>
            <td>".$machine_error_from_deploy."</td>
            <td>".$machine_process_from_deploy."</td>
            <td>".$wol."</td>
            <td>".$machine_timeout_from_deploy."</td>
            <td>".$machine_abort_from_deploy."</td>";
        echo "</tr></table>";
    echo '</div>';
      echo'<div  style="float:left; margin-left:200px;height: 120px" id="holder"></div>';
    echo "<br>";
    if ($info['len'] != 0){
    //     $uuid=$info['objectdeploy'][0]['inventoryuuid'];
    //     $state=$info['objectdeploy'][0]['state'];
    //     $start=get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
    //     $result=$info['objectdeploy'][0]['result'];
    //
    //     $resultatdeploy =json_decode($result, true);
    //     $host=$info['objectdeploy'][0]['host'];
    //     $jidmachine=$info['objectdeploy'][0]['jidmachine'];
    //     $jid_relay=$info['objectdeploy'][0]['jid_relay'];

        $datestart =  date("Y-m-d H:i:s", $start_date);
        $timestampstart = strtotime($datestart);
        $timestampnow = time();
        $nbsecond = $timestampnow - $timestampstart;

        if (isset($resultatdeploy['descriptor']['info'])){
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
    if($terminate == 0){
            echo'
                <script type="text/javascript">
                //console.log("hello");
                    setTimeout(refresh, 120000);
                    function  refresh(){
                            location.reload()
                    }
                </script>
                ';
    }

//fin deployement status
echo "</div>";
// group includ computers_list.php
// les parametres get sont utilisés par computers_list pour l'appel de ajaxComputersList qui compose l'appel a list_computers
// mmc/modules/base/includes/computers_list.inc.php

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

    $other            = count ( $uuiddefault );
    $machinesucess    = count ( $uuidsuccess );
    $machineerror     = count ( $uuiderror );
    $machineinprocess = count ( $uuidprocess );

  $status = [];
  foreach ($info['objectdeploy'] as  $val){
      $status[$val['inventoryuuid']] = $val['state'];

      switch($val['state']){
          case "DEPLOYMENT SUCCESS":
              $uuidsuccess[] = $val['inventoryuuid'];
              break;
          case "DEPLOYMENT ERROR":
              $uuiderror[] = $val['inventoryuuid'];
              break;
          case "DEPLOYMENT START":
          case "DEPLOYMENT START (REBOOT)":
          case "DEPLOYMENT DIFFERED":
              $uuidprocess[] = $val['inventoryuuid'];
              break;
          default:
              $uuiddefault[] = $val['inventoryuuid'];
      }
      $uuidall[] = $val['inventoryuuid'];
  }
  $params = [];
  foreach($info_from_machines[0] as $key => $value)
  {
      if(isset($status['UUID'.$value]))
        $info_from_machines[7][] = $status['UUID'.$value];
      $info_from_machines[8][] = 'UUID'.$value;
      $params[] = [
        'displayName' => $info_from_machines[2][$key],
        'cn' => $info_from_machines[1][$key],
        'type' => $info_from_machines[4][$key],
        'objectUUID' => 'UUID'.$value,
        'entity' => $info_from_machines[6][$key],
        'owner' => $info_from_machines[5][$key],
        'user' => $_GET['login'],
        'os' => $info_from_machines[3][$key],
        'status' => isset($info_from_machines[7][$key]) ? $info_from_machines[7][$key] : "",
        'gid' => $_GET['gid'],
        'gr_cmd_id' => $_GET['cmd_id'],
        'gr_login' => $_GET['login'],
      ];
  }

  $presencemachinexmpplist = xmlrpc_getPresenceuuids($info_from_machines[8]);
  foreach($info_from_machines[8] as $key => $value)
  {
    $info_from_machines[9][] = ($presencemachinexmpplist[$value] == "1") ? 'machineNamepresente' : 'machineName';
  }
    echo"<br><br><br>";
  $n = new OptimizedListInfos($info_from_machines[1], _T("Machine Name", "xmppmaster"));
  $n->setCssClass("package");
  $n->addExtraInfo($info_from_machines[2], _T("Description", "glpi"));
  $n->addExtraInfo($info_from_machines[3], _T("Operating System", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[7], _T("Status", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[4], _T("Type", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[5], _T("Last User", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[6], _T("Entity", "glpi"));

  $action_log = new ActionItem(_T("Deployment Detail", 'xmppmaster'),"viewlogs","logfile",
  "logfile","xmppmaster", "xmppmaster");
  $n->setParamInfo($params);
  $n->addActionItemArray($action_log);
  $n->setMainActionClasses($info_from_machines[9]);
  $n->setItemCount($count);
  $n->setNavBar(new AjaxNavBar($count, $filter));
  $n->start = 0;
  $n->end = $count;
  $n->display();
  echo '
  <script src="modules/xmppmaster/graph/js/chart.js"></script>
  <script>

      var u = "";
      var r = "";
      var datas = new Array();';

          if ($machine_success_from_deploy > 0){
            echo 'datas.push({"label":"Success", "value":'.$machine_success_from_deploy.', "color": "#2EFE2E", "href":"'.urlredirect_group_for_deploy("machinesucess",$_GET['gid'], $_GET['login'], $cmd_id).'"});';
          }
          if ($machine_error_from_deploy > 0){
            echo 'datas.push({"label":"Error", "value":'.$machine_error_from_deploy.', "color": "#FE2E64", "href":"'.urlredirect_group_for_deploy("machineerror",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($machine_process_from_deploy > 0){
            echo 'datas.push({"label":"In progress", "value":'.$machine_process_from_deploy.', "color": "#2E9AFE", "href":"'.urlredirect_group_for_deploy("machineprocess",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($wol > 0){
            echo 'datas.push({"label":"Waiting (WOL sent)", "value":'.$wol.', "color": "#DBA901", "href":"'.urlredirect_group_for_deploy("machinewol",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($machine_timeout_from_deploy > 0){
          echo 'datas.push({"label":"Timed out", "value":'.$machine_timeout_from_deploy.', "color": "#FF4500", "href":"'.urlredirect_group_for_deploy("machinewol",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($machine_abort_from_deploy > 0){
            echo 'datas.push({"label":"Aborted", "value":'.$machine_abort_from_deploy.', "color": "#ff5050", "href":"'.urlredirect_group_for_deploy("machineabort",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          echo'
          chart("holder", datas);
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
.bars1{
    width:650px;
    float:left;
}
</style>
