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
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
global $conf;
$maxperpage = $conf["global"]["maxperpage"];


$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['end']:$maxperpage-1);
$arraydeploy= xmlrpc_get_deployxmppscheduler( $_GET['login'] , $start, $end, $filter);
$etat="";
$LastdeployINsecond = 3600 * 72;
echo "<h2>".$_GET['login']."</h2>";

$login   = array();
$startdeploy = array();

foreach( $arraydeploy['tabdeploy']['start'] as $ss){
   $startdeploy[]="$ss[0]-$ss[1]-$ss[2] $ss[3]:$ss[4]:$ss[5]";
}
foreach( $arraydeploy['tabdeploy']['command'] as $ss){
   $login[]=xmlrpc_loginbycommand($ss);
}


$arraydeploy['tabdeploy']['start'] = $startdeploy;
$n = new OptimizedListInfos( $arraydeploy['tabdeploy']['host'], _T("Host name", "xmppmaster"));
$n->addExtraInfo( $startdeploy, _T("start", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['pathpackage'], _T("package", "xmppmaster"));
$n->addExtraInfo( $arraydeploy['tabdeploy']['creator'], _T("login", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);
$n->setCssClass("machineName");
$n->setTableHeaderPadding(0);
$n->start = $start;
$n->end = $end;
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter));
print "<br/>"; 

$n->display();

?>
