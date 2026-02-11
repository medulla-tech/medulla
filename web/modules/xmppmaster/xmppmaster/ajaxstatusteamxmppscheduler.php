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
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);

$arraydeploy = xmlrpc_get_deploy_xmpp_teamscheduler( $_GET['login'] , $start, $end, $filter);
$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$etat="";
$LastdeployINsecond = 3600 * 72;
echo "<h2>" . _T("Planned tasks") . "</h2>";
$login   = array();
$startdeploy = array();
$enddeploy= array();
function convtostringdate($data){
    if (is_array($data) && safeCount($data) == 9){
        return date("Y-m-d H:i:s", mktime( $data[3],
                        $data[4],
                        $data[5],
                        $data[1],
                        $data[2],
                        $data[0]));
    }elseif(is_object ($data) && xmlrpc_get_type($data) == "datetime" ){
        return convtostringdate($data->timestamp);
    }elseif(is_string($data)){
        return $data;
    }elseif( is_numeric($data) || is_int($data)){
        return gmdate("Y-m-d H:i:s", $data);
    }else{
    return "error date";}
}

foreach( $arraydeploy['tabdeploy']['start'] as $start_date){
    $startdeploy[] = convtostringdate($start_date);
    $enddeploy[] = convtostringdate($end_date);
    }

foreach( $arraydeploy['tabdeploy']['command'] as $ss){
   $arraydeploy['tabdeploy']['login'][]=xmlrpc_loginbycommand($ss);
}
$deletecommand = new ActionItem(_("Delete deploy"),
                                "index",
                                "delete",
                                "audit",
                                "xmppmaster",
                                "xmppmaster");
$logAction = new ActionItem(_("View deployment details"),
                                "viewlogs",
                                "audit",
                                "computer",
                                "xmppmaster",
                                "xmppmaster");


$rescheduleAction = new ActionPopupItem(_T("Reschedule", "xmppmaster"),
                                        "rechedulercmd",
                                        "edit",
                                        "computer",
                                        "xmppmaster",
                                        "xmppmaster");

// delete_command
$arraytitlename=array();
$delete=array();
$logs=array();
$replanifie=array();
$params=array();
$arraytargetname=array();

$index = 0;
$deployment_intervals=array();
foreach($arraydeploy['tabdeploy']['groupid'] as $groupid){
    $param=array();
    $param['uuid']= $arraydeploy['tabdeploy']['inventoryuuid'][$index];
    $param['hostname']=$arraydeploy['tabdeploy']['host'][$index];
    $param['groupid']=$groupid;
    $param['cmd_id']=$arraydeploy['tabdeploy']['command'][$index];
    $param['login']=$arraydeploy['tabdeploy']['login'][$index];
    $param['nbmachine']=$arraydeploy['tabdeploy']['nbmachine'][$index];
    $param['macadress']=$arraydeploy['tabdeploy']['macadress'][$index];
    $param['pathpackage']=$arraydeploy['tabdeploy']['pathpackage'][$index];
    $param['title']=$arraydeploy['tabdeploy']['title'][$index];
    $param['creator']=$arraydeploy['tabdeploy']['creator'][$index];
    $param['titledeploy']=$arraydeploy['tabdeploy']['titledeploy'][$index];
    $param['deployment_intervals']=$arraydeploy['tabdeploy']['deployment_intervals'][$index];
    $param['start_date']=$startdeploy[$index];
    $param['end_date']=$enddeploy[$index];
    $param['postaction']="delete";
    $params[] = $param;
    $delete[] = $deletecommand;
    $logs[] = $logAction;
    $replanifie[] =  $rescheduleAction;
    if($groupid){
        $groupname = getPGobject($arraydeploy['tabdeploy']['groupid'][$index], true)->getName();
        $arraytargetname[] = "<img class='icon-inline' src='img/other/machinegroup.svg'/> " . $groupname ;
    }
    else{
        // Check machine presence to use correct icon
        $machineUuid = $arraydeploy['tabdeploy']['inventoryuuid'][$index];
        $arraytargetname[] = "<img class='icon-inline' src='img/other/machine_down.svg'/> " . $arraydeploy['tabdeploy']['host'][$index] ;
    }
    $index++;
}


if((isset($arraydeploy['tabdeploy']['journee']))){
    foreach($arraydeploy['tabdeploy']['journee'] as $key => $value){
        if ($value == 1){
            $style='class="text-darkblue"';
        }else
        {
            $style='';
        }
        if ($arraydeploy['tabdeploy']['deployment_intervals'][$key] != ""){
            $deployment_intervals = _T("deployment intervals contraints", "xmppmaster")." ".$arraydeploy['tabdeploy']['deployment_intervals'][$key];
        }else
        {
            $deployment_intervals = _T("No deployment intervals contraint", "xmppmaster");
        }

        $arraydeploy['tabdeploy']['title'][$key]= sprintf('<span %s title="%s " > %s </span>',
                                                            $style,
                                                    $deployment_intervals = _T("No deployment intervals contraint", "xmppmaster"));


        $arraydeploy['tabdeploy']['title'][$key]= sprintf('<span %s title="%s " > %s </span>',
                                                            $style,
                $deployment_intervals,
                                                            $arraydeploy['tabdeploy']['title'][$key] );
        if ($convergence[$arraydeploy['tabdeploy']['command'][$key]] != 0 ){
            $arraydeploy['tabdeploy']['title'][$key]= "<img class='icon-inline' src='img/other/convergence.svg'/>" . $arraydeploy['tabdeploy']['title'][$key];
            }else{
                $arraydeploy['tabdeploy']['title'][$key]= "<img class='icon-inline' src='img/other/package.svg'/>" . $arraydeploy['tabdeploy']['title'][$key];
            }
    }
}
$arraydeploy['tabdeploy']['start'] = $startdeploy;
$n = new OptimizedListInfos($arraydeploy['tabdeploy']['title'], _T("Deployment", "xmppmaster"));
$n->addExtraInfo( $arraytargetname, _T("Target", "xmppmaster"));
$n->addExtraInfo( $startdeploy, _T("Start date", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['creator'], _T("User", "xmppmaster"));

$n->disableFirstColumnActionLink();
$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter, "updateSearchParamformRunning1"));
$n->addActionItemArray($replanifie);
$n->addActionItemArray($logs);
$n->addActionItemArray($delete);
$n->setTableHeaderPadding(0);

$n->setParamInfo($params);
// $n->start = $start;
// $n->end = $end;
$n->start = 0;
$n->end = $arraydeploy['lentotal'];

print "<br/>";

$n->display();

?>
