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
$arraydeploy= xmlrpc_get_deployxmppscheduler( $_GET['login'] , $start, $end, $filter);
$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$etat="";
$LastdeployINsecond = 3600 * 72;
echo "<h2>" . _T("Planned tasks") . "</h2>";
$login   = array();
$startdeploy = array();

$enddeploy = array();
foreach( $arraydeploy['tabdeploy']['start'] as $start_date){
  $startdeploy[] = date("Y-m-d H:i:s", mktime( $start_date[3],
                        $start_date[4],
                        $start_date[5],
                        $start_date[1],
                        $start_date[2],
                        $start_date[0]));
}

foreach( $arraydeploy['tabdeploy']['end'] as $start_date){
  $enddeploy[] = date("Y-m-d H:i:s", mktime( $start_date[3],
                        $start_date[4],
                        $start_date[5],
                        $start_date[1],
                        $start_date[2],
                        $start_date[0]));
}


foreach( $arraydeploy['tabdeploy']['command'] as $ss){
   $login[]=xmlrpc_loginbycommand($ss);
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
// delete_command
$arraytitlename=array();
$delete=array();
$logs=array();
$params=array();
$arraytargetname=array();
$index = 0;
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
    $param['postaction']="delete";
    $params[] = $param;
    $delete[] = $deletecommand;
    $logs[] = $logAction;
    if($groupid){
        $groupname = getPGobject($arraydeploy['tabdeploy']['groupid'][$index], true)->getName();
        $arraytargetname[] = "<img style='position:relative;top : 5px;'src='img/other/machinegroup.svg' width='25' height='25'/> " . $groupname ;
    }
    else{
        $arraytargetname[] = "<img style='position:relative;top : 5px;'src='img/other/machine_down.svg' width='25' height='25'/> " . $arraydeploy['tabdeploy']['host'][$index] ;
    }
    $index++;
}

$notdeployment_intervals = _T("No deployment intervals contraint", "xmppmaster");

foreach($arraydeploy['tabdeploy']['journee'] as $key => $value){
  if ($value == 1){
      $deployment_intervals = _T("deployment intervals contraints", "xmppmaster");
      $arraydeploy['tabdeploy']['title'][$key]= sprintf('<span style="color:darkblue" title="%s %s" > %s </span>',$deployment_intervals, $arraydeploy['tabdeploy']['deployment_intervals'][$key], $arraydeploy['tabdeploy']['title'][$key] );
  }else{

       $arraydeploy['tabdeploy']['title'][$key]=sprintf('<span title="%s" > %s </span>',$notdeployment_intervals, $arraydeploy['tabdeploy']['title'][$key]);
  }
  if ($convergence[$arraydeploy['tabdeploy']['command'][$key]] != 0 ){
           $arraydeploy['tabdeploy']['title'][$key]= "<img style='position:relative;top : 5px;'src='img/other/convergence.svg' width='25' height='25'/>" . $arraydeploy['tabdeploy']['title'][$key];
        }else{
             $arraydeploy['tabdeploy']['title'][$key]= "<img style='position:relative;top : 5px;'src='img/other/package.svg' width='25' height='25'/>" . $arraydeploy['tabdeploy']['title'][$key];
        }
/*
  if ($arraydeploy['tabdeploy']['groupid'][$key] != "")
  {//group

  }*/
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
