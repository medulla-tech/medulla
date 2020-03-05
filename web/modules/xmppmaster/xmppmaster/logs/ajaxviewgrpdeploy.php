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

extract($_GET);

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$criterion = isset($_GET['criterion'])?$_GET['criterion']:"";
$filter = ["filter" => $filter, "criterion" => $criterion];
$start = (isset($_GET['start']))? $_GET['start']: 0;
$end   = (isset($_GET['end'])?$_GET['end']+$maxperpage:$maxperpage);

function urlredirect_group_for_deploy($typegroup, $g_id, $login_deploy , $cmddeploy_id ){
    $urlRedirect1 = urlStrRedirect("base/computers/createMachinesStaticGroupdeploy&gid=".$g_id."&login=".$login_deploy."&cmd_id=".$cmddeploy_id."&type=".$typegroup);
    return $urlRedirect1;
}

$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment [ group",'xmppmaster')." ". $group->getName()."]");
$p->display();

//FROM MSC BASE
// search nbmachinegroupe in group, and nbdeploydone already deployed from mmc
$resultfrommsc = xmlrpc_getstatbycmd($cmd_id, $filter, $start, $end);

// The deployment is a convergence
$bool_convergence_grp_on_package_from_msc = is_commands_convergence_type($cmd_id, $filter, $start, $end);

// Get syncthing stats for this deployment
$statsyncthing  = xmlrpc_stat_syncthing_transfert($_GET['gid'],$_GET['cmd_id'] );

// search from msc table CommandsOnHost
$lastcommandid = get_last_commands_on_cmd_id_start_end($cmd_id, $filter, $start, $end);
$start_date =  $lastcommandid['start_dateunixtime'];
$end_date = $lastcommandid['end_dateunixtime'];

$getdeployment = xmlrpc_getdeployment($cmd_id, $filter, $start, $maxperpage);

$re = xmlrpc_get_machine_for_id($getdeployment['datas']['id'], $filter, $start, $maxperpage);
$count = $getdeployment['total'];

// STATS FROM XMPPMASTER DEPLOY
$resultfromdeploy = xmlrpc_getstatdeployfromcommandidstartdate( $cmd_id,  date("Y-m-d H:i:s", $start_date));
// from msc
$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");

$MSC_nb_mach_grp_for_deploy  = $resultfrommsc['nbmachine'];
$MSC_nb_mach_grp_done_deploy     = $resultfrommsc['nbdeploydone'];
$timestampnow = time();
$info_from_machines = $re["listelet"];

$totalmachinedeploy = $resultfromdeploy['totalmachinedeploy'];
$deploymentsuccess  = $resultfromdeploy['deploymentsuccess'];
$deploymenterror    = $resultfromdeploy['deploymenterror'];
$deploymentabort    = $resultfromdeploy['deploymentabort'];
$abortontimeout     = $resultfromdeploy['abortontimeout'];
$abortmissingagent  = $resultfromdeploy['abortmissingagent'];
$abortrelaydown = $resultfromdeploy['abortrelaydown'];
$abortalternativerelaysdown = $resultfromdeploy['abortalternativerelaysdown'];
$abortinforelaymissing = $resultfromdeploy['abortinforelaymissing'];
$errorunknownerror = $resultfromdeploy['errorunknownerror'];
$abortpackageidentifiermissing = $resultfromdeploy['abortpackageidentifiermissing'];
$abortpackagenamemissing = $resultfromdeploy['abortpackagenamemissing'];
$abortpackageversionmissing = $resultfromdeploy['abortpackageversionmissing'];
$abortpackageworkflowerror = $resultfromdeploy['abortpackageworkflowerror'];
$abortdescriptormissing = $resultfromdeploy['abortdescriptormissing'];
$abortmachinedisappeared = $resultfromdeploy['abortmachinedisappeared'];
$deploymentstart = $resultfromdeploy['deploymentstart'];
$wol1 = $resultfromdeploy['wol1'];
$wol2 = $resultfromdeploy['wol2'];
$wol3 = $resultfromdeploy['wol3'];
$waitingmachineonline = $resultfromdeploy['waitingmachineonline'];
$deploymentpending = $resultfromdeploy['deploymentpending'];
$otherstatus = $resultfromdeploy['otherstatus'];

$terminate = 0;
$deployinprogress = 0;

$waiting = $MSC_nb_mach_grp_for_deploy - ($totalmachinedeploy + $abortontimeout);

// $evolution
if ($waiting == 0 && $deploymentstart == 0 ){
    $terminate = 1;
}

$start_deploy = 0;
$end_deploy   = 0;
if ($timestampnow > $start_date){
    $start_deploy = 1;
}

if ($timestampnow > ($end_date)){
    $end_deploy = 1;
};

// This command gets associated group of cmd_id

echo "Deployment schedule: ".date("Y-m-d H:i:s", $start_date)." -> ".date("Y-m-d H:i:s", $end_date)."<br>";
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

if (isset($resultatdeploy['infoslist'][0]['packageUuid'])){
    echo "Package : ".$resultatdeploy['infoslist'][0]['name']." [". $resultatdeploy['infoslist'][0]['packageUuid']."]";
}

if (!isset($_GET['refresh'])){
    $_GET['refresh'] = 1;
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

//start deployement status
echo "<div>";
    if ( $start_deploy){

        if ($end_deploy || $terminate == 1){
            echo "<h2>"._T("Deployment completed","xmppmaster")."</h2>";
            $terminate = 1;
            $deployinprogress = 0;

        }else{
            echo "<h2>"._T("Deployment in progress","xmppmaster")."</h2>";
            echo _T("Started since","xmppmaster")." <span>".($timestampnow - $start_date)."</span> s";
            $deployinprogress = 1;
        }
    }
    else{
        echo _T("WAITING FOR START ","xmppmaster").date("Y-m-d H:i:s", $start_date);
    }


    if($terminate == 0){
        $f = new ValidatingForm();
        $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
        $f->addButton("bStop", _T("Abort Deployment", 'xmppmaster'));
        $f->display();
    }

        $nb_machine_deployer_avec_timeout_deploy = $abortontimeout + $MSC_nb_mach_grp_done_deploy;
        $evolution  = round(($nb_machine_deployer_avec_timeout_deploy / $MSC_nb_mach_grp_for_deploy) * 100,2);
        $deploymachine = $deploymentsuccess + $deploymenterror;
        echo '<div class="bars">';
            echo '<span style="width: 200px;">';
                echo'<progress class="mscdeloy" data-label="50% Complete" max="'.$MSC_nb_mach_grp_for_deploy.'" value="'.$nb_machine_deployer_avec_timeout_deploy .'" form="form-id"></progress>';
            echo '</span>';
        echo'<span style="margin-left:10px">Deployment '.$evolution.'%</span>';

        echo "<br><br>"._T("Number of machines in the group","xmppmaster")." : ".$MSC_nb_mach_grp_for_deploy;
        echo "<br>"._T("Number of current deployments","xmppmaster")." : ". $deploymachine;
        echo "<br>"._T("Number of deployments in timeout","xmppmaster").": ". $abortontimeout;
        echo "<br>"._T("Deployment summary","xmppmaster").":";
        echo "<table><tr>";
        echo "<td>"._T("Success","xmppmaster")."</td>
            <td>"._T("Error","xmppmaster")."</td>
            <td>"._T("In progress","xmppmaster")."</td>
            <td>"._T("Waiting","xmppmaster")."</td>
            <td>"._T("WOL","xmppmaster")."</td>
            <td>"._T("Waiting for Online","xmppmaster")."</td>
            <td>"._T("Timed out","xmppmaster")."</td>
            <td>"._T("Aborted","xmppmaster")."</td>";
        echo "</tr>
        <tr>";
        $inprogress = ( $MSC_nb_mach_grp_for_deploy - ( $totalmachinedeploy + $abortontimeout ));
        $wol = $wol1+$wol2+$wol3;
        echo "<td>".$deploymentsuccess."</td>
            <td>".$deploymenterror."</td>
            <td>".$deploymentstart."</td>
            <td>".$inprogress."</td>
            <td>".$wol."</td>
            <td>".$waitingmachineonline."</td>
            <td>".$abortontimeout."</td>
            <td>".$deploymentabort."</td>";
        echo "</tr></table>";

    echo '</div>';
      echo'<div  style="float:left; margin-left:200px;height: 120px" id="holder"></div>';
    if ($info['len'] != 0){
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
                            echo $resultatdeploy['descriptor']['info']['name'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['software'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['version'];
                        echo "</td>";
                        echo "<td>";
                            echo $resultatdeploy['descriptor']['info']['description'];
                        echo "</td>";
                    echo "</tr>";
                echo "</tbody>";
            echo "</table>";

        }

    }

echo "</div>";
if (isset($countmachine)){
  if ($info['len'] > $countmachine){
    $info['len'] = $countmachine;
  }
  if ($nbsuccess > $countmachine){
    $nbsuccess = $countmachine;
  }
}

if ($info['len'] != 0){
  $uuidsuccess = array();
  $uuiderror = array();
  $uuidprocess = array();
  $uuiddefault = array();

  $status = [];
  foreach ($info['objectdeploy'] as  $val){
      $status[$val['inventoryuuid']] = "";
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
  }
  $params = [];
  foreach($info_from_machines[0] as $key => $value)
  {
      if(isset($status['UUID'.$value]))
        $info_from_machines[7][] = $status['UUID'.$value];
      else
        $info_from_machines[7][] = '<span style="color:red">'._T('OFFLINE','xmppmaster').'</span>';
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
        'status' => isset($info_from_machines[7][$key]) ? $info_from_machines[7][$key] : '<span style="color:red">'._T('OFFLINE','xmppmaster').'</span>',
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

echo '<div style="clear:both"></div>';
if ($count == 0){
echo'
<table class="listinfos" cellspacing="0" cellpadding="5" border="1">
<thead>
    <tr>
        <td style="width: ;"><span style=" padding-left: 32px;">Machine Name</span></td>
        <td style="width: ;"><span style=" ">Description</span></td>
        <td style="width: ;"><span style=" ">Operating System</span></td>
        <td style="width: ;"><span style=" ">Status</span></td>
        <td style="width: ;"><span style=" ">Type</span></td>
        <td style="width: ;"><span style=" ">Last User</span>
        </td><td style="width: ;"><span style=" ">Entity</span>
        </td><td style="text-align: center; width: ;"><span>Actions</span></td>
    </tr>
</thead>
<tbody>
</tbody>
</table>';
}else{
$action_log = new ActionItem(_T("Deployment Detail", 'xmppmaster'),
                                    "viewlogs",
                                    "logfile",
                                    "logfile",
                                    "xmppmaster",
                                    "xmppmaster");
  $n = new OptimizedListInfos($info_from_machines[1], _T("Machine Name", "xmppmaster"));

  $n->addExtraInfo($info_from_machines[2], _T("Description", "glpi"));
  $n->addExtraInfo($info_from_machines[3], _T("Operating System", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[7], _T("Status", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[4], _T("Type", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[5], _T("Last User", "xmppmaster"));
  $n->addExtraInfo($info_from_machines[6], _T("Entity", "glpi"));

  $n->setParamInfo($params);
  $n->addActionItem($action_log);
  $n->setMainActionClasses($info_from_machines[9]);
  $n->setItemCount($count);
  $n->setNavBar(new AjaxNavBar($count, $filter));
  $n->start = 0;
  $n->end = $count;
  $n->display();
}
  echo '
  <script src="modules/xmppmaster/graph/js/chart.js"></script>
  <script>

      var u = "";
      var r = "";
      var datas = new Array();';

          if ($deploymentsuccess > 0){
            echo 'datas.push({"label":"Success", "value":'.$deploymentsuccess.', "color": "#2EFE2E", "href":"'.urlredirect_group_for_deploy("machinesucess",$_GET['gid'], $_GET['login'], $cmd_id).'"});';
          }
          if ($deploymenterror > 0){
            echo 'datas.push({"label":"Error", "value":'.$deploymenterror.', "color": "#FE2E64", "href":"'.urlredirect_group_for_deploy("machineerror",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($deploymentstart > 0){
            echo 'datas.push({"label":"In progress", "value":'.$deploymentstart.', "color": "#2E9AFE", "href":"'.urlredirect_group_for_deploy("machineprocess",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($inprogress > 0){
            echo 'datas.push({"label":"Waiting", "value":'.$inprogress.', "color": "#DBA901", "href":"'.urlredirect_group_for_deploy("machinewol",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($wol > 0){
            echo 'datas.push({"label":"WOL", "value":'.$wol.', "color": "#db9201", "href":"'.urlredirect_group_for_deploy("machinewol",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortontimeout > 0){
          echo 'datas.push({"label":"Timed out", "value":'.$abortontimeout.', "color": "#FF4500", "href":"'.urlredirect_group_for_deploy("abortontimeout",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($deploymentabort > 0){
            echo 'datas.push({"label":"Aborted", "value":'.$deploymentabort.', "color": "#ff5050", "href":"'.urlredirect_group_for_deploy("machineabort",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($waitingmachineonline > 0){
            echo 'datas.push({"label":"Waiting for Online ", "value":'.$waitingmachineonline.', "color": "#8f01db", "href":"'.urlredirect_group_for_deploy("machinewaitingonline",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if($abortalternativerelaysdown > 0){
            echo 'datas.push({"label":"Abort alternative relays down ", "value":'.$abortalternativerelaysdown.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortalternativerelaysdown",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortrelaydown > 0){
            echo 'datas.push({"label":"Abort relay down ", "value":'.$abortrelaydown.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortrelaydown",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortmissingagent > 0){
            echo 'datas.push({"label":"Abort missing agent ", "value":'.$abortmissingagent.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortmissingagent",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortinforelaymissing > 0){
            echo 'datas.push({"label":"Abort info for relay missing ", "value":'.$abortinforelaymissing.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortinforelaymissing",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($errorunknownerror > 0){
            echo 'datas.push({"label":"Error unknown error ", "value":'.$errorunknownerror.', "color": "#db1701", "href":"'.urlredirect_group_for_deploy("errorunknownerror",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortpackageidentifiermissing > 0){
            echo 'datas.push({"label":"Abort package identifier missing ", "value":'.$abortpackageidentifiermissing.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortpackageidentifiermissing",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortpackagenamemissing > 0){
            echo 'datas.push({"label":"Abort package name missing ", "value":'.$abortpackagenamemissing.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortpackagenamemissing",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortpackageversionmissing > 0){
            echo 'datas.push({"label":"Abort package version missing ", "value":'.$abortpackageversionmissing.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortpackageversionmissing",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortpackageworkflowerror > 0){
            echo 'datas.push({"label":"Abort package workflow error ", "value":'.$abortpackageworkflowerror.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortpackageworkflowerror",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortdescriptormissing > 0){
            echo 'datas.push({"label":"Abort descriptor missing ", "value":'.$abortdescriptormissing.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortdescriptormissing",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($abortmachinedisappeared > 0){
            echo 'datas.push({"label":"Abort machine disappeared ", "value":'.$abortmachinedisappeared.', "color": "#db6701", "href":"'.urlredirect_group_for_deploy("abortmachinedisappeared",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($deploymentpending > 0){
            echo 'datas.push({"label":"Deployment pending ", "value":'.$deploymentpending.', "color": "#8f01db", "href":"'.urlredirect_group_for_deploy("deploymentpending",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          if ($otherstatus > 0){
            echo 'datas.push({"label":"Other status ", "value":'.$otherstatus.', "color": "#8f01db", "href":"'.urlredirect_group_for_deploy("otherstatus",$_GET['gid'],$_GET['login'],$cmd_id).'"});';
          }
          $otherstatus = $resultfromdeploy['otherstatus'];



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
