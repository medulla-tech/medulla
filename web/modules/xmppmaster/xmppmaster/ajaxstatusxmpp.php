<?
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
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
 * file ajaxstatusxmpp.php
 */
 require_once("modules/dyngroup/includes/xmlrpc.php");
//require("modules/dyngroup/includes/includes.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
?>

<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1'){
  $status="";
  $LastdeployINsecond = 3600*24;
  echo "<h2>" . _T("Current tasks (last 24 hours)") . "</h2>";
  $arraydeploy = xmlrpc_getdeploybyuserrecent( $_GET['login'] ,$status, $LastdeployINsecond, $start, $end, $filter) ;
  $arraynotdeploy = xmlrpc_getnotdeploybyuserrecent($_GET['login'], $LastdeployINsecond, $start, $end, $filter);
}
else {
  $LastdeployINsecond = 3600*2160;
  echo "<h2>" . _T("Past tasks (last 3 months)") ."</h2>";
  $arraydeploy = xmlrpc_getdeploybyuserpast( $_GET['login'] ,$LastdeployINsecond, $start, $end, $filter) ;
}

if (isset($arraydeploy['total_of_rows']))
{
  $arraydeploy['lentotal'] = $arraydeploy['total_of_rows'];
  if (isset($arraynotdeploy['total']))
  {
    $arraydeploy['lentotal'] += $arraynotdeploy['total'];
  }
}
$arrayname = array();
$arraytitlename = array();
$arraystate = array();
$params = array();
$logs   = array();
$startdeploy = array();
$tolmach=array();
$successmach=array();
$errormach=array();
$abortmachuser = array();
$processmachr = array();

// $dd = xmlrpc_getstatbycmd(3);
foreach( $arraydeploy['tabdeploy']['start'] as $ss){
    if (gettype($ss) == "string"){
        $startdeploy[]=$ss;
    }
}

$logAction = new ActionItem(_("detaildeploy"),
                                "viewlogs",
                                "logfile",
                                "computer",
                                "xmppmaster",
                                "xmppmaster");

$arraydeploy['tabdeploy']['start'] = $startdeploy;

for ($i=0;$i< count( $arraydeploy['tabdeploy']['start']);$i++){
    $param=array();
    $param['uuid']= $arraydeploy['tabdeploy']['inventoryuuid'][$i];
    $param['hostname']=$arraydeploy['tabdeploy']['host'][$i];
    $param['gid']=$arraydeploy['tabdeploy']['group_uuid'][$i];
    $param['cmd_id']=$arraydeploy['tabdeploy']['command'][$i];
    $param['login']=$arraydeploy['tabdeploy']['login'][$i];
    $logs[] = $logAction;
    $params[] = $param;
}

$lastcommandid = get_array_last_commands_on_cmd_id_start_end($arraydeploy['tabdeploy']['command']);
$statarray = xmlrpc_getarraystatbycmd($arraydeploy['tabdeploy']['command']);
$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$groupname = getInfosNameGroup($arraydeploy['tabdeploy']['group_uuid']);
$index = 0;
foreach($arraydeploy['tabdeploy']['group_uuid'] as $groupid){
    $error = False;
    if(($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT DIFFERED" ||
        strpos($arraydeploy['tabdeploy']['state'][$index], "DEPLOYMENT START")!==false) &&
            (get_object_vars($arraydeploy['tabdeploy']['endcmd'][$index])['timestamp']- time()) < 0){
        $error = True;
        $arraydeploy['tabdeploy']['state'][$index] = "<span style='font-weight: bold; color : red;'>DEPLOY ERROR TIMEOUT</span>";
    }
        $deploydate = (array)$arraydeploy['tabdeploy']['startcmd'][$index];
        $deploydate = substr($deploydate['scalar'], 0, 4).'-'.substr($deploydate['scalar'], 4, 2).'-'.substr($deploydate['scalar'], 6, 2).' '.substr($deploydate['scalar'], 9);
        $result = xmlrpc_getstatdeployfromcommandidstartdate($arraydeploy['tabdeploy']['command'][$index],
                                                             $deploydate);
        $done = 0;
        $aborted = 0;
        $inprogress = 0;

        //Calculate globals stats
        foreach($result as $key => $value){
            if($key != 'totalmachinedeploy'){
                if(preg_match('#abort|success|error|status#i', $key)){
                    $done += $value;
                }
                else{
                    $inprogress += $value;
                }

                if(preg_match('#^abort#i', $key) && $key != 'totalmachinedeploy'){
                    $aborted += $value;
                }
            }

        }

        $totalmachinedeploy = $result['totalmachinedeploy'];

        $processmachr[] = $inprogress;
        $tolmach[] = $totalmachinedeploy;
        $successmach[]=$result['deploymentsuccess'];
        $errormach[]= $result['deploymenterror'] + $result['errorunknownerror'];
        $abortmachuser[] = $aborted;

    if($groupid){

        if (isset($arraydeploy['tabdeploy']['group_uuid'][$index])){
            $namegrp = $groupname[$arraydeploy['tabdeploy']['group_uuid'][$index]]['name'];
        }
        else{
            $namegrp = "";
        }
        //recherche information de deployement sur ce groupe.
        if ($convergence[$arraydeploy['tabdeploy']['command'][$index]] != 0 ){
            $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_convergence.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        }else{
            $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_package.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        }

        if( $totalmachinedeploy == 0){
            $success = 0;
        }
        else{
            $success = round(($done / $totalmachinedeploy) * 100, 2);
            $success = ($success > 100) ? 100 : $success;
        }

            switch(intval($success)){
                case $success <= 10:
                    $color = "#ff0000";
                    break;
                case $success <= 20:
                    $color = "#ff3535";
                    break;
                case $success <= 30:
                    $color = "#ff5050";
                    break;
                case $success <= 40:
                    $color = "#ff8080";
                    break;
                case $success <  50:
                    $color = "#ffA0A0";
                    break;
                case $success <=  60:
                    $color = "#c8ffc8";
                    break;
                case $success <= 70:
                    $color = "#97ff97";
                    break;
                case $success <= 80:
                    $color = "#64ff64";
                    break;
                case $success <=  90:
                    $color = "#2eff2e";
                    break;
                case $success >90:
                    $color = "#00ff00";
                    break;
            }
        if ($success == 0){
            $arraystate[] = "<span style='font-weight: bold; color : red;'>".$success."%"."</span>" ;
        }else{
            if ($success == 100) {
                $arraystate[] = "<span style='font-weight: bold; color: green ;'>DEPLOY SUCCESS FULL</span>" ;
            }
            else{
                $arraystate[] = "<span style='background-color:".$color." ;'>".$success."%"."</span>" ;
            }
        }
        //'<progress max="'.$stat['nbmachine'].'" value="'.$stat['nbdeploydone'].'" form="form-id"></progress>';
        if (! isset($groupname[$groupid]['name']))
        {
            $arrayname[] = "This group doesn't exist";
        }
        else {
            $arrayname[] = "<span style='text-decoration : underline;'><img style='position:relative;top : 5px;'src='img/machines/icn_groupsList.gif'/>" . $groupname[$groupid]['name']."</span>";
        }
    }
    else{
        $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_package.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        $arrayname[] = "<img style='position:relative;top : 5px;'src='img/machines/icn_machinesList.gif'/> " . $arraydeploy['tabdeploy']['host'][$index];
        if ($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT ERROR")
        {
            $arraystate[]="<span style='font-weight: bold; color : red;'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
        }
        else{
            $arraystate[]="<span style='font-weight: bold; color : green;'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
        }
    }
    $index++;
}

foreach($arraynotdeploy['elements'] as $id=>$deploy)
{
    $param = [
    'cmd_id'=>$deploy['cmd_id'],
    'login'=>$deploy['login'],
    'gid'=>$deploy['gid'],
    'uuid'=>$deploy['uuid_inventory']];
    $logs[] = $logAction;
    $params[] = $param;

    $arraytitlename[] = '<img style="position:relative;top : 5px;" src="modules/msc/graph/images/install_package.png" /> '.$deploy['package_name'];

    $name = "";
    if($deploy['gid'] != "")
    {
        $name = getInfosNameGroup($deploy['gid']);
        $name = $name[$deploy['gid']]['name'];
        $name = '<img style="position:relative;top : 5px;" src="img/machines/icn_groupsList.gif"/> '.$name;
        //echo '<a href="main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=grouptablogs&uuid=&hostname=&gid='.$deploy['gid'].'&cmd_id='.$deploy['cmd_id'].'&login='.$deploy['login'].'">'.$deploy['package_name'].'</a><br />';
      }

    else
    {
        $name = $deploy['machine_name'];
        $name = '<img style="position:relative;top : 5px;" src="img/machines/icn_machinesList.gif"/> '.$name;
    }
    $arrayname[] = $name;

    $date = (array)$deploy['date_start'];
    $arraydeploy['tabdeploy']['start'][] = date("Y-m-d H:i:s",$date['timestamp']);
    //TODO
    $arraystate[] = '<span style="font-weight: bold; color : orange;">Offline</span>';
    $tolmach[] = $deploy['nb_machines'];
    $processmachr[] = 0;
    $successmach[] = 0;
    $errormach[] = 0;
    $abortmachuser[] = 0;
    $arraydeploy['tabdeploy']['login'][] = $deploy['login'];
}

$n = new OptimizedListInfos( $arraytitlename, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $arrayname, _T("Target", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("Start date", "xmppmaster"));
$n->addExtraInfo( $arraystate, _T("Progress / Status", "xmppmaster"));
$n->addExtraInfo( $tolmach, _T("Total Machines", "xmppmaster"));
$n->addExtraInfo( $processmachr, _T("In progress", "xmppmaster"));
$n->addExtraInfo( $successmach, _T("Success", "xmppmaster"));
$n->addExtraInfo( $errormach, _T("Error", "xmppmaster"));
$n->addExtraInfo( $abortmachuser, _T("Aborted", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['login'],_T("User", "xmppmaster"));
//$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($logs);
 //function AjaxNavBar($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "", $paginator = false) {

$n->setParamInfo($params);
// $n->start = isset($_GET['start'])?$_GET['start']:0;
// $n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage);
$n->start = 0;
$n->end = $arraydeploy['lentotal'];

$n->display();
echo "<br>";
?>
<style>
progress {
  width: 100px;
  height: 9px;
  margin:-5px;
  background-color: #ffffff;
  border-style: solid;
  border-width: 1px;
  border-color: #dddddd;
  padding: 3px 3px 3px 3px;
}

progress::-webkit-progress-bar {
    background: #f3f3f3 ;
}

progress::-webkit-progress-value {
     Background: #ef9ea9;
}

</style>
