<?
/**
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

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);

$etat="";
$LastdeployINsecond = 3600*72;
echo "<h2>Current and past tasks</h2>";
$arraydeploy = xmlrpc_getdeploybyuserrecent( $_GET['login'] ,$etat, $LastdeployINsecond, $start, "", $filter) ;
$arrayname = array();
$arraytitlename = array();
$arraystate = array();
$params = array();
$logs   = array();
$startdeploy = array();
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
    if($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT START" && (get_object_vars($arraydeploy['tabdeploy']['endcmd'][$index])['timestamp']- time()) < 0){
        $error = True;
        $arraydeploy['tabdeploy']['state'][$index] = "<span style='font-weight: bold; color : red;'>DEPLOY ERROR TIMEOUT</span>";
    }

    if($groupid){

        if (isset($arraydeploy['tabdeploy']['group_uuid'][$index])){
            $countmachine = getRestrictedComputersListLen( array('gid' => $arraydeploy['tabdeploy']['group_uuid'][$index]));
            $namegrp = getPGobject($arraydeploy['tabdeploy']['group_uuid'][$index], true)->getName();
        }
        else{
            $countmachine = "";
            $namegrp = "";
        }
        $stat = xmlrpc_getstatbycmd($arraydeploy['tabdeploy']['command'][$index]);
        //recherche information de deployement sur ce groupe.
        $lastcommandid = get_last_commands_on_cmd_id($arraydeploy['tabdeploy']['command'][$index]);
        if ( is_commands_convergence_type($arraydeploy['tabdeploy']['command'][$index]) != 0 ){
            $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_convergence.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        }else{
            $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_package.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        }
        $start_date = date("Y-m-d H:i:s", mktime( $lastcommandid['start_date'][3],
                              $lastcommandid['start_date'][4],
                              $lastcommandid['start_date'][5],
                              $lastcommandid['start_date'][1],
                              $lastcommandid['start_date'][2],
                              $lastcommandid['start_date'][0]));
        $result = xmlrpc_getstatdeployfromcommandidstartdate($arraydeploy['tabdeploy']['command'][$index], $start_date);

        if( $result['totalmachinedeploy'] == 0){
            $sucess = 0;
        }
        else{
            $sucess = round(($result['machinesuccessdeploy'] / $result['totalmachinedeploy']) * 100, 2);
        }
        switch($sucess){
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

        $arraystate[] = "<span style='background-color:".$color." ;'>".$sucess."%"."</span>" ;
        //'<progress max="'.$stat['nbmachine'].'" value="'.$stat['nbdeploydone'].'" form="form-id"></progress>';
        $group = new Group($groupid, true, true);
        if ($group->exists == False) {
            $arrayname[] ="This group doesn't exist";
        }
        else {
            $arrayname[] = "<img style='position:relative;top : 5px;'src='img/machines/icn_groupsList.gif'/> " . $group->getName();
        }
    }
    else{
        $arraytitlename[] = "<img style='position:relative;top : 5px;'src='modules/msc/graph/images/install_package.png'/>" . $arraydeploy['tabdeploy']['title'][$index];
        $arrayname[] = "<img style='position:relative;top : 5px;'src='img/machines/icn_machinesList.gif'/> " . $arraydeploy['tabdeploy']['host'][$index];
        $arraystate[]="<span style='font-weight: bold; color : green;'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
    }
    $index++;
}

$n = new OptimizedListInfos( $arraytitlename, _T("Deployment", "xmppmaster"));
$n->addExtraInfo( $arrayname, _T("Target", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("Start date", "xmppmaster"));
$n->addExtraInfo( $arraystate, _T("Status", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['login'],_T("User", "xmppmaster"));
$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);
$n->addActionItemArray($logs);

$n->setTableHeaderPadding(0);
$n->setParamInfo($params);
$n->start = $start;
$n->end = $end;
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter));

print "<br/><br/>";

$n->display();
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
