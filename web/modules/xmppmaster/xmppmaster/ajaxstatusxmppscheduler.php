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

$etat="";
$LastdeployINsecond = 3600 * 72;
//echo "<h2>".$_GET['login']."</h2>";
echo "<h2>Planned tasks</h2>";
$login   = array();
$startdeploy = array();

foreach( $arraydeploy['tabdeploy']['start'] as $start_date){
  $startdeploy[] = date("Y-m-d H:i:s", mktime( $start_date[3],
                        $start_date[4],
                        $start_date[5],
                        $start_date[1],
                        $start_date[2],
                        $start_date[0]));
}
foreach( $arraydeploy['tabdeploy']['command'] as $ss){
   $login[]=xmlrpc_loginbycommand($ss);
}

$deletecommand = new ActionItem(_("Delete deploy"), "index", "delete", "audit", "xmppmaster", "xmppmaster");
// delete_command
$arraytitlename=array();
$delete=array();
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
    if($groupid){
        $groupname = getPGobject($arraydeploy['tabdeploy']['groupid'][$index], true)->getName();
        $arraytargetname[] = "<img style='position:relative;top : 5px;'src='img/machines/icn_groupsList.gif'/> " . $groupname ;
    }
    else{
        $arraytargetname[] = "<img style='position:relative;top : 5px;'src='img/machines/icn_machinesList.gif'/> " . $arraydeploy['tabdeploy']['host'][$index] ;
    }
    $index++;
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
$n->addActionItemArray($delete);
$n->setTableHeaderPadding(0);

$n->setParamInfo($params);
$n->start = $start;
$n->end = $end;

print "<br/>";

$n->display();

?>
