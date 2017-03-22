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
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);

$etat="";
$LastdeployINsecond = 3600*72;
echo "<h2>Current and past tasks";
//echo "<h2>".$_GET['login']."</h2>";
$arraydeploy = xmlrpc_getdeploybyuserrecent( $_GET['login'] ,$etat, $LastdeployINsecond, $start, "", $filter) ;

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
    $param['gid']="";
    $param['cmd_id']=$arraydeploy['tabdeploy']['command'][$i];
    $param['login']=$arraydeploy['tabdeploy']['login'][$i];
    $logs[] = $logAction;
    $params[] = $param;
}

$n = new OptimizedListInfos( $arraydeploy['tabdeploy'][host], _T("Host name", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['start'], _T("start", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['state'], _T("State", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['pathpackage'],"package");
$n->addExtraInfo( $arraydeploy['tabdeploy']['login'],"login");


$n->disableFirstColumnActionLink();
$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);

$n->addActionItemArray($logs);
$n->setCssClass("machineName");

$n->setTableHeaderPadding(0);
$n->setParamInfo($params);
$n->start = $start;
$n->end = $end;
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter));

print "<br/><br/>"; 

$n->display();
?>
