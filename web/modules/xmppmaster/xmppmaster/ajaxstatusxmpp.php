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
require("modules/dyngroup/includes/includes.php");
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
}
else {
  $LastdeployINsecond = 3600*2160;
  echo "<h2>" . _T("Past tasks (last 3 months)") ."</h2>";
  $arraydeploy = xmlrpc_getdeploybyuserpast( $_GET['login'] ,$LastdeployINsecond, $start, $end, $filter) ;
}

if (isset($arraydeploy['total_of_rows']))
{
  $arraydeploy['lentotal'] = $arraydeploy['total_of_rows'];
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
$êrrormach=array();
$timeoutmach=array();
$abortmachuser = array();
$processmachr = array();

// $dd = xmlrpc_getstatbycmd(3);
foreach( $arraydeploy['tabdeploy']['start'] as $ss){
    if (gettype($ss) == "string"){
        $startdeploy[]=$ss;
    }
}

$logAction = new ActionItem(_("detaildeploy"),"viewlogs","logfile","computer", "xmppmaster", "xmppmaster");

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

$index = 0;
foreach($arraydeploy['tabdeploy']['group_uuid'] as $groupid){
    $error = False;
    if(($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT START" ||
        $arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT DIFFERED") &&
            (get_object_vars($arraydeploy['tabdeploy']['endcmd'][$index])['timestamp']- time()) < 0){
        $error = True;
        $arraydeploy['tabdeploy']['state'][$index] = "<span style='font-weight: bold; color : red;'>DEPLOY ERROR TIMEOUT</span>";
    }

    $lastcommandid = get_last_commands_on_cmd_id($arraydeploy['tabdeploy']['command'][$index]);
    $start_date = date("Y-m-d H:i:s", mktime( $lastcommandid['start_date'][3],
                              $lastcommandid['start_date'][4],
                              $lastcommandid['start_date'][5],
                              $lastcommandid['start_date'][1],
                              $lastcommandid['start_date'][2],
                              $lastcommandid['start_date'][0]));

        $result = xmlrpc_getstatdeployfromcommandidstartdate($arraydeploy['tabdeploy']['command'][$index], $start_date);

        $total_machine_from_deploy     = $result['totalmachinedeploy'];
        $machine_error_from_deploy     = $result['machineerrordeploy'];
        $machine_success_from_deploy   = $result['machinesuccessdeploy'];
        $machine_process_from_deploy   = $result['machineprocessdeploy'];
        $machine_abort_from_deploy     = $result['machineabortdeploy'];

        $stat = xmlrpc_getstatbycmd($arraydeploy['tabdeploy']['command'][$index]);
        $total_machine_from_msc  = $stat['nbmachine'];
        // from msc
        $machine_timeout_from_deploy   = xmlrpc_get_count_timeout_wol_deploy($arraydeploy['tabdeploy']['command'][$index], $start_date);
        $resultfrommsc = xmlrpc_getstatbycmd($arraydeploy['tabdeploy']['command'][$index]);
        $total_machine_from_msc  = $resultfrommsc['nbmachine'];

        $wol = ( $total_machine_from_msc - ( $total_machine_from_deploy + $machine_timeout_from_deploy ));

        $processmachr[] = $machine_process_from_deploy;
        $tolmach[] = $total_machine_from_msc;
        $wolmach[]=$wol;
        $successmach[]=$machine_success_from_deploy;
        $êrrormach[]=$machine_error_from_deploy;
        $timeoutmach[]=$machine_timeout_from_deploy;
        $abortmachuser[] = $machine_abort_from_deploy;

    if($groupid){

        if (isset($arraydeploy['tabdeploy']['group_uuid'][$index])){
            $countmachine = getRestrictedComputersListLen( array('gid' => $arraydeploy['tabdeploy']['group_uuid'][$index]));
            $namegrp = getPGobject($arraydeploy['tabdeploy']['group_uuid'][$index], true)->getName();
        }
        else{
            $countmachine = "";
            $namegrp = "";
        }
        //recherche information de deployement sur ce groupe.
        if ( is_commands_convergence_type($arraydeploy['tabdeploy']['command'][$index]) != 0 ){
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
            $arraystate[] = "<span style='background-color:".$color." ;'>".$sucess."%"."</span>" ;
        }
        //'<progress max="'.$stat['nbmachine'].'" value="'.$stat['nbdeploydone'].'" form="form-id"></progress>';
        $group = new Group($groupid, true, true);
        if ($group->exists == False) {
            $arrayname[] ="This group doesn't exist";
        }
        else {
            $arrayname[] = "<span style='text-decoration : underline;'><img style='position:relative;top : 5px;'src='img/machines/icn_groupsList.gif'/>" . $group->getName()."</span>";
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

$n = new OptimizedListInfos( $arraytitlename, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $arrayname, _T("Target", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("Start date", "xmppmaster"));
$n->addExtraInfo( $arraystate, _T("Status", "xmppmaster"));
$n->addExtraInfo( $tolmach, _T("Total Machines", "xmppmaster"));
$n->addExtraInfo( $processmachr, _T("In progress", "xmppmaster"));
$n->addExtraInfo( $successmach, _T("Success", "xmppmaster"));
$n->addExtraInfo( $êrrormach, _T("Error", "xmppmaster"));
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
