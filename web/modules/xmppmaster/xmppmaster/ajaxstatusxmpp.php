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
$wolmach=array();
$successmach=array();
$errormach=array();
$timeoutmach=array();
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

        $result = xmlrpc_getstatdeployfromcommandidstartdate($arraydeploy['tabdeploy']['command'][$index],
                                                             $lastcommandid[$index]['startdate']);

        $total_machine_from_deploy     = $result['totalmachinedeploy'];
        $machine_error_from_deploy     = $result['machineerrordeploy'];
        $machine_success_from_deploy   = $result['machinesuccessdeploy'];
        $machine_process_from_deploy   = $result['machineprocessdeploy'];
        $machine_abort_from_deploy     = $result['machineabortdeploy'];
        // from msc
        $machine_timeout_from_deploy   = xmlrpc_get_count_timeout_wol_deploy($arraydeploy['tabdeploy']['command'][$index], $start_date);

        $total_machine_from_msc  =  $statarray['nbmachine'][$arraydeploy['tabdeploy']['command'][$index]];

        $wol = ( $total_machine_from_msc - ( $total_machine_from_deploy + $machine_timeout_from_deploy ));

        $processmachr[] = $machine_process_from_deploy;
        $tolmach[] = $total_machine_from_msc;
        $wolmach[]=$wol;
        $successmach[]=$machine_success_from_deploy;
        $errormach[]=$machine_error_from_deploy;
        $timeoutmach[]=$machine_timeout_from_deploy;
        $abortmachuser[] = $machine_abort_from_deploy;

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
        $nb_machine_deployer_avec_timeout_deploy = $machine_timeout_from_deploy + $total_machine_from_msc;
        $evolution  = round(($nb_machine_deployer_avec_timeout_deploy / $total_machine_from_msc) * 100,2);


        if( $result['totalmachinedeploy'] == 0){
            $sucess = 0;
        }
        else{
            $sucess = round(($result['machinesuccessdeploy'] / $total_machine_from_msc) * 100, 2);
        }

            switch(intval($sucess)){
                case $sucess <= 10:
                    $color = "#ff0000";
                    break;
                case $sucess <= 20:
                    $color = "#ff3535";
                    break;
                case $sucess <= 30:
                    $color = "#ff5050";
                    break;
                case $sucess <= 40:
                    $color = "#ff8080";
                    break;
                case $sucess <  50:
                    $color = "#ffA0A0";
                    break;
                case $sucess <=  60:
                    $color = "#c8ffc8";
                    break;
                case $sucess <= 70:
                    $color = "#97ff97";
                    break;
                case $sucess <= 80:
                    $color = "#64ff64";
                    break;
                case $sucess <=  90:
                    $color = "#2eff2e";
                    break;
                case $sucess >90:
                    $color = "#00ff00";
                    break;
            }
        if ($sucess == 0){
            $arraystate[] = "<span style='font-weight: bold; color : red;'>".$sucess."%"."</span>" ;
        }else{
            if ($sucess == 100) {
                $arraystate[] = "<span style='font-weight: bold; color: green ;'>DEPLOY SUCCESS FULL</span>" ;
            }
            else{
                $arraystate[] = "<span style='background-color:".$color." ;'>".$sucess."%"."</span>" ;
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
    $wolmach[] = 0;
    $wolmach[] = 0;
    $timeoutmach[] = 0;
    $abortmachuser[] = 0;
    $arraydeploy['tabdeploy']['login'][] = $deploy['login'];
}

$n = new OptimizedListInfos( $arraytitlename, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $arrayname, _T("Target", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("Start date", "xmppmaster"));
$n->addExtraInfo( $arraystate, _T("Status", "xmppmaster"));
$n->addExtraInfo( $tolmach, _T("Total Machines", "xmppmaster"));
$n->addExtraInfo( $processmachr, _T("In progress", "xmppmaster"));
$n->addExtraInfo( $successmach, _T("Success", "xmppmaster"));
$n->addExtraInfo( $errormach, _T("Error", "xmppmaster"));
$n->addExtraInfo( $wolmach, _T("Waiting Wol", "xmppmaster"));
$n->addExtraInfo( $timeoutmach, _T("Timed out", "xmppmaster"));
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
