<?
/*
 * (c) 2015-2019 Siveo, http://www.siveo.net
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
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');


global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);


if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1'){
  $status="";
  $LastdeployINsecond = 3600*24;
  echo "<h2>" . _T("Deployments Launched on Offline Items (last 24 hours)") . "</h2>";
}
else {
  $LastdeployINsecond = 3600*2160;
  echo "<h2>" . _T("Deployments Launched on Offline Items (last 3 months)") . "</h2>";
}


//$lastcommandid = get_array_last_commands_on_cmd_id_start_end($arraydeploy['tabdeploy']['command']);
//$statarray = xmlrpc_getarraystatbycmd($arraydeploy['tabdeploy']['command']);
//$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
//$groupname = getInfosNameGroup($arraydeploy['tabdeploy']['group_uuid']);
$index = 0;

$arraynotdeploy = xmlrpc_getnotdeploybyuserrecent($_GET['login'], $LastdeployINsecond, $start, $end, $filter);

$notd_machinesname = [];
$notd_packagename = [];
$notd_cmdstart = [];
$notd_state = [];
$notd_nb_machines = [];
$notd_logins = [];
$notd_datestart = [];
$notd_logs = [];
$params = [];


foreach($arraynotdeploy['elements'] as $id=>$deploy)
{
  $params[] = [
    'cmd_id'=>$deploy['cmd_id'],
    'login'=>$deploy['login'],
    'gid'=>$deploy['gid'],
    'uuid'=>$deploy['uuid_inventory']];
  $notd_packagename[] = '<img style="position:relative;top : 5px;" src="modules/msc/graph/images/install_package.png" /> '.$deploy['package_name'];
  //$notd_packagename[] = $deploy['package_name'];
  $date = (array)$deploy['date_start'];
  $notd_datestart [] = date("Y-m-d H:i:s",$date['timestamp']);
  $notd_state[] = '<span style="font-weight: bold; color : Orange;">DEPLOYMENT NOT LAUNCHED</span>';
  $notd_nb_machines[] = $deploy['nb_machines'];
  $notd_logins[] = $deploy['login'];

  $name = "";
  if($deploy['gid'] != "")
  {
    $name = getInfosNameGroup($deploy['gid']);
    $name = $name[$deploy['gid']]['name'];
    $name = '<img style="position:relative;top : 5px;" src="img/machines/icn_groupsList.gif"/> '.$name;
    //echo '<a href="main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=grouptablogs&uuid=&hostname=&gid='.$deploy['gid'].'&cmd_id='.$deploy['cmd_id'].'&login='.$deploy['login'].'">'.$deploy['package_name'].'</a><br />';
    $logAction = new ActionItem(_("detaildeploy"),
                                    "viewlogs",//Action
                                    "logfile",//class
                                    "",
                                    "xmppmaster",//submod
                                    "xmppmaster",
                                    "grouptablogs");
  }

  else
  {
    $name = $deploy['machine_name'];
    $name = '<img style="position:relative;top : 5px;" src="img/machines/icn_machinesList.gif"/> '.$name;
    $logAction = new ActionItem(_("detaildeploy"),
                                    "viewlogs",//Action
                                    "logfile",//class
                                    "",
                                    "xmppmaster",//submod
                                    "xmppmaster",
                                    "grouptablogs");//module
  }
  $notd_machinesname[] = $name;

  $notd_logs[] = $logAction;
}

$m = new OptimizedListInfos( $notd_packagename, _T("Deployment", "xmppmaster"));
$m->setCssClass("package2");
$m->disableFirstColumnActionLink();
$m->addExtraInfo( $notd_machinesname, _T("Target", "xmppmaster"));
$m->addExtraInfo( $notd_datestart, _T("Start date", "xmppmaster"));
$m->addExtraInfo( $notd_nb_machines, _T("Total Machines", "xmppmaster"));
$m->addExtraInfo( $notd_logins,_T("User", "xmppmaster"));
$m->setItemCount($arraynotdeploy['total']);
$m->setNavBar(new AjaxNavBar($arraynotdeploy['total'], $filter, "updateSearchParamformRunning_notd"));
$m->addActionItemArray($notd_logs);
$m->setParamInfo($params);
$m->start = 0;
$m->end = $arraynotdeploy['total'];
$m->display();
echo '<br /><br /><br />';
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
