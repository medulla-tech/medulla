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
require("modules/dyngroup/includes/includes.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);

$etat="";
$LastdeployINsecond = 3600*72;
//print_r($_GET);
echo "<h2>deploy log machine";
$arraydeploy = xmlrpc_getdeploybymachinerecent( $_GET['uuid'] ,"", $LastdeployINsecond, $start, $end, $filter);
print_r($arraydeploy);
$arrayname = array();
$arraytitlename = array();
$arraystate = array();
$params = array();
$logs   = array();
$startdeploy = array();
foreach( $arraydeploy['tabdeploy']['start'] as $ss){
    if (gettype($ss) == "string"){
        $startdeploy[]=$ss;
    }
}

$logAction =new ActionItem(_("detaildeploy"),"viewlogs","logfile","computer", "xmppmaster", "xmppmaster");

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
        $arraytitlename[] = "<span style='color : blue;'>(GRP  : ".$arraydeploy['tabdeploy']['len'][$index] . ") ".$arraydeploy['tabdeploy']['title'][$index]."</span>";
        $arraystate[]="";
        $group = new Group($groupid, true, true);
        if ($group->exists == False) {
            $arrayname[] ="This group doesn't exist";
        } 
        else {
            $arrayname[] = $group->getName();
        }
    }
    else{
        $arraytitlename[] = "<span style='color : green;'>( Mach : ) ".$arraydeploy['tabdeploy']['title'][$index]."</span>";
        $arrayname[] = $arraydeploy['tabdeploy']['host'][$index];
        $arraystate[]="<span style='font-weight: bold; color : green;'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
    }
    $index++;
}

$n = new OptimizedListInfos( $arraytitlename, _T("Deployment", "xmppmaster"));
$n->addExtraInfo( $arrayname, _T("Name", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("Start", "xmppmaster"));
$n->addExtraInfo( $arraystate, _T("State", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['pathpackage'],_T("Package", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['login'],_T("User", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lenquery']);

$n->addActionItemArray($logs);
$n->setCssClass("machineName");

$n->setTableHeaderPadding(0);
$n->setParamInfo($params);
$n->start = $start;
$n->end = $end;
$n->setNavBar(new AjaxNavBar($arraydeploy['lenquery'], $filter));

print "<br/><br/>";

$n->display();
?>
