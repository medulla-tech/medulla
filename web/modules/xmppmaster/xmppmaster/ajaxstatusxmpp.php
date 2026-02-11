<?php
/*
 * (c) 2015-2021 Siveo, http://www.siveo.net
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

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1') {
    $status = "";
    $LastdeployINsecond = 3600 * 24;
    echo "<h2>" . _T("Current tasks (last 24 hours)") . "</h2>";
    $arraydeploy = xmlrpc_get_deploy_by_user_with_interval($_GET['login'], $status, $LastdeployINsecond, $start, $end, $filter, "command") ;
    $arraynotdeploy = xmlrpc_get_deploy_inprogress_by_team_member($_GET['login'], $LastdeployINsecond, $start, $end, $filter);
} else {
    $LastdeployINsecond = 3600 * 2160;
    echo "<h2>" . _T("Past tasks (last 3 months)") ."</h2>";
  $arraydeploy = xmlrpc_get_deploy_by_user_finished( $_GET['login'] ,
                                                     $LastdeployINsecond,
                                                     $start,
                                                     $end,
                                                     $filter,
                                                     "command") ;
}

if (isset($arraydeploy['total_of_rows'])) {
    $arraydeploy['lentotal'] = $arraydeploy['total_of_rows'];
    if (isset($arraynotdeploy['total'])) {
        $arraydeploy['lentotal'] += $arraynotdeploy['total'];
    }
}

$tab = xmlrpc_get_conrainte_slot_deployment_commands($arraydeploy['tabdeploy']['command']);

$arrayname = array();
$arraytitlename = array();
$arraystate = array();
$params = array();
$logs   = array();
$startdeploy = array();
$endcmd = array();
$startcmd = array();
$tolmach = array();
$successmach = array();
$errormach = array();
$abortmachuser = array();
$processmachr = array();
$reloads = array();

$contrainte = array();

// Display contrainte in title
// foreach ($arraydeploy['tabdeploy']['command'] as $dd=>$ss)
// {
//     if ($tab[$arraydeploy['tabdeploy']['command'][$dd]] != "") {
//         $arraydeploy['tabdeploy']['state'][$dd] = '<span title="'._T('Deployment Interval Constraint','xmppmaster')." ".$tab[$arraydeploy['tabdeploy']['command'][$dd]].'">'.$arraydeploy['tabdeploy']['state'][$dd]."</span>";
//     }
// }
// or avec second line pour la contrainte
foreach ($arraydeploy['tabdeploy']['command'] as $dd => $ss) {
    if ($tab[$arraydeploy['tabdeploy']['command'][$dd]] != "") {
        $arraydeploy['tabdeploy']['state'][$dd] = $arraydeploy['tabdeploy']['state'][$dd].'<br><span title="'._T("Deployment Interval Constraint", "xmppmaster"). '" class="constraint-text">'._T("Constraint: ", "xmppmaster").$tab[$arraydeploy['tabdeploy']['command'][$dd]]."</span>";
    }
}

foreach($arraydeploy['tabdeploy']['start'] as $ss) {
    if (gettype($ss) == "string") {
        $startdeploy[] = $ss;
    }
}
$arraydeploy['tabdeploy']['start'] = $startdeploy;

foreach($arraydeploy['tabdeploy']['endcmd'] as $ss) {
    $ee =  get_object_vars($ss);
    $endcmd[] = gmdate("Y-m-d H:i:s", $ee['timestamp']);
}
$arraydeploy['tabdeploy']['endcmd'] = $endcmd;

foreach($arraydeploy['tabdeploy']['startcmd'] as $ss) {
    $ee =  get_object_vars($ss);
    $startcmd[] = gmdate("Y-m-d H:i:s", $ee['timestamp']);
}
$arraydeploy['tabdeploy']['startcmd'] = $startcmd;


$logAction = new ActionItem(
    _("View deployment details"),
    "viewlogs",
    "audit",
    "computer",
    "xmppmaster",
    "xmppmaster"
);

$previous = (isset($_GET['previous'])) ? htmlentities($_GET['previous']) : "";
$reloadAction = new ActionPopupItem(
    _("Restart deployment"),
    "popupReloadDeploy&previous=".$previous,
    "reload",
    "",
    "xmppmaster",
    "xmppmaster"
);


for ($i = 0;$i < safeCount($arraydeploy['tabdeploy']['start']);$i++) {
    //$infomachine = xmlrpc_getdeployfromcommandid($arraydeploy['tabdeploy']['command'][$i], $arraydeploy['tabdeploy']['inventoryuuid'][$i]);

    $param = array();
    $param['uuid'] = $arraydeploy['tabdeploy']['inventoryuuid'][$i];
    $param['hostname'] = $arraydeploy['tabdeploy']['host'][$i];
    $param['gid'] = $arraydeploy['tabdeploy']['group_uuid'][$i];
    $param['cmd_id'] = $arraydeploy['tabdeploy']['command'][$i];
    $param['login'] = $arraydeploy['tabdeploy']['login'][$i];
    $param['title'] = $arraydeploy['tabdeploy']['title'][$i];
    $param['start'] = $arraydeploy['tabdeploy']['start'][$i];
    $param['endcmd'] = $arraydeploy['tabdeploy']['endcmd'][$i];
    $param['startcmd'] = $arraydeploy['tabdeploy']['startcmd'][$i];
    $param['sessionid'] = $arraydeploy['tabdeploy']['sessionid'][$i];
    $logs[] = $logAction;
    $reloads[] = $reloadAction;
    $params[] = $param;
}

$lastcommandid = get_array_last_commands_on_cmd_id_start_end($arraydeploy['tabdeploy']['command']);
$statarray = xmlrpc_getarraystatbycmd($arraydeploy['tabdeploy']['command']);
$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$groupname = getInfosNameGroup($arraydeploy['tabdeploy']['group_uuid']);

$index = 0;
foreach($arraydeploy['tabdeploy']['group_uuid'] as $groupid) {
    $error = false;
    if(($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT DIFFERED" ||
        strpos($arraydeploy['tabdeploy']['state'][$index], "DEPLOYMENT START") !== false) &&
            (strtotime($arraydeploy['tabdeploy']['endcmd'][$index]) - time()) < 0) {
        $error = true;
        $arraydeploy['tabdeploy']['state'][$index] = "<span class='status-group-error'>DEPLOY ERROR TIMEOUT</span>";
    }
    $result = xmlrpc_getstatdeploy_from_command_id_and_title(
        $arraydeploy['tabdeploy']['command'][$index],
        $arraydeploy['tabdeploy']['title'][$index]
    );
    $done = 0;
    $aborted = 0;
    $inprogress = 0;

    //Calculate globals stats
    foreach($result as $key => $value) {
        if($key != 'totalmachinedeploy') {
            if(preg_match('#abort|success|error|status#i', $key)) {
                $done += $value;
            } else {
                $inprogress += $value;
            }

            if(preg_match('#^abort#i', $key) && $key != 'totalmachinedeploy') {
                $aborted += $value;
            }
        }

    }

    $totalmachinedeploy = $result['totalmachinedeploy'];
    $deploymentsuccess = $result['deploymentsuccess'];
    $deploymenterror = (isset($result['deploymenterror'])) ? $result['deploymenterror'] : 0;
    $tolmach[] = $totalmachinedeploy;
    $inprogressPercent = round(($inprogress / $totalmachinedeploy) * 100, 1);
    $processmachr[] = $inprogress.' ('.$inprogressPercent.'%)';
    $successPercent = round(($deploymentsuccess / $totalmachinedeploy) * 100, 1);
    $successmach[] = $deploymentsuccess.' ('.$successPercent.'%)';
    $errorPercent = round((($deploymenterror + $result['errorunknownerror']) / $totalmachinedeploy) * 100, 1);
    $errormach[] = ($deploymenterror + $result['errorunknownerror']).' ('.$errorPercent.'%)';
    $abortedPercent = round(($aborted / $totalmachinedeploy) * 100, 1);
    $abortmachuser[] = $aborted.' ('.$abortedPercent.'%)';
    if($groupid) {
        if (isset($arraydeploy['tabdeploy']['group_uuid'][$index])) {
            $namegrp = $groupname[$arraydeploy['tabdeploy']['group_uuid'][$index]]['name'];
        } else {
            $namegrp = "";
        }

        if($totalmachinedeploy == 0) {
            $progressrate = 0;
        } else {
            $progressrate = round(($done / $totalmachinedeploy) * 100, 2);
            $progressrate = ($progressrate > 100) ? 100 : $progressrate;
        }
        $successrate = round(($deploymentsuccess / $totalmachinedeploy) * 100, 2);

        // Determine icon class based on status
        $iconClass = 'icon-inline';
        if ($progressrate == 0 || ($progressrate == 100 && $successrate == 0)) {
            $iconClass .= ' icon-error';
        } else if ($progressrate == 100 && $successrate == 100) {
            $iconClass .= ' icon-success';
        } else if ($progressrate == 100 && $successrate > 0 && $successrate < 100) {
            $iconClass .= ' icon-partial';
        }

        // Set title with appropriate icon class
        if ($convergence[$arraydeploy['tabdeploy']['command'][$index]] != 0) {
            $arraytitlename[] = "<img class='".$iconClass."' src='img/other/convergence.svg'/>" . $arraydeploy['tabdeploy']['title'][$index];
        } else {
            $arraytitlename[] = "<img class='".$iconClass."' src='img/other/package.svg'/>" . $arraydeploy['tabdeploy']['title'][$index];
        }

        switch(intval($progressrate)) {
            case $progressrate <= 10:
                $color = "#ff0000";
                break;
            case $progressrate <= 20:
                $color = "#ff3535";
                break;
            case $progressrate <= 30:
                $color = "#ff5050";
                break;
            case $progressrate <= 40:
                $color = "#ff8080";
                break;
            case $progressrate <  50:
                $color = "#ffA0A0";
                break;
            case $progressrate <=  60:
                $color = "#c8ffc8";
                break;
            case $progressrate <= 70:
                $color = "#97ff97";
                break;
            case $progressrate <= 80:
                $color = "#64ff64";
                break;
            case $progressrate <=  90:
                $color = "#2eff2e";
                break;
            case $progressrate > 90:
                $color = "#00ff00";
                break;
        }
        if ($progressrate == 0) {
            $arraystate[] = "<span class='status-group-error'>".$progressrate."%"."</span>" ;
        } else {
            if ($progressrate == 100) {
                if($successrate == 0) {
                    $arraystate[] = '<span class="status-group-error">'._T('GROUP ERROR', 'xmppmaster').'</span>';
                } elseif($successrate > 0 && $successrate < 100) {
                    $arraystate[] = '<span class="status-group-partial">'._T('GROUP PARTIAL SUCCESS', 'xmppmaster').'</span>';
                } else {
                    $arraystate[] = '<span class="status-group-success">'._T('GROUP FULL SUCCESS', 'xmppmaster').'</span>';
                }
            } else {
                $arraystate[] = "<span style='background-color:".$color.";'>".$progressrate."%"."</span>" ;
            }
        }
        //'<progress max="'.$stat['nbmachine'].'" value="'.$stat['nbdeploydone'].'" form="form-id"></progress>';
        if (!isset($groupname[$groupid]['name'])) {
            $arrayname[] = _T("This group doesn't exist", "xmppmaster");
        } else {
            $arrayname[] = "<span class='text-underline'><img class='icon-inline' src='img/other/machinegroup.svg'/>" . $groupname[$groupid]['name']."</span>";
        }
    } else {
        // Determine icon class based on deployment state
        $iconClass = 'icon-inline';
        if ($arraydeploy['tabdeploy']['state'][$index] == "DEPLOYMENT ERROR") {
            $iconClass .= ' icon-error';
            $arraystate[] = "<span class='status-group-error'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
        } else {
            $iconClass .= ' icon-success';
            $arraystate[] = "<span class='status-group-success'>".$arraydeploy['tabdeploy']['state'][$index]."</span>";
        }
        $arraytitlename[] = "<img class='".$iconClass."' src='img/other/package.svg'/>" . $arraydeploy['tabdeploy']['title'][$index];
        $arrayname[] = "<img class='icon-inline' src='img/other/machine_down.svg'/> " . $arraydeploy['tabdeploy']['host'][$index];
    }
    $index++;
}

if(isset($arraynotdeploy)) {
    foreach($arraynotdeploy['elements'] as $id => $deploy) {
        $param = [
        'cmd_id' => $deploy['cmd_id'],
        'login' => $deploy['login'],
        'gid' => $deploy['gid'],
        'uuid' => $deploy['uuid_inventory']];
        $logs[] = $logAction;
        $params[] = $param;

        $arraytitlename[] = '<img class="icon-inline" src="img/other/package.svg"/> '.$deploy['package_name'];

        $name = "";
        if($deploy['gid'] != "") {
            $name = getInfosNameGroup($deploy['gid']);
            $name = $name[$deploy['gid']]['name'];
            $name = '<img class="icon-inline" src="img/other/machinegroup.svg"/> '.$name;
        //echo '<a href="main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=grouptablogs&uuid=&hostname=&gid='.$deploy['gid'].'&cmd_id='.$deploy['cmd_id'].'&login='.$deploy['login'].'">'.$deploy['package_name'].'</a><br />';
        } else {
            $name = $deploy['machine_name'];
            // Check machine presence to use correct icon
            $name = '<img class="icon-inline" src="img/other/machine_down.svg"/> '.$name;
        }
        $arrayname[] = $name;

        $date = (array)$deploy['date_start'];
        $arraydeploy['tabdeploy']['start'][] = substr($date['scalar'], 0, 4).'-'.substr($date['scalar'], 4, 2).'-'.substr($date['scalar'], 6, 2).' '.substr($date['scalar'], 9);
        //TODO
        if ($deploy['deployment_intervals'] != "") {
            $arraystate[] = '<span class="status-pending">Pending<br><span class="constraint-text">'._T("Constraint: ", "xmppmaster").
            $deploy['deployment_intervals'].'</span></span>';
        } else {
            $arraystate[] = '<span class="status-pending">Pending</span>';
        }
        $tolmach[] = $deploy['nb_machines'];
        $processmachr[] = '0 (0%)';
        $successmach[] = '0 (0%)';
        $errormach[] = '0 (0%)';
        $abortmachuser[] = '0 (0%)';
        $arraydeploy['tabdeploy']['login'][] = $deploy['login'];
        $reloads[] = $reloadAction;
    }
}
$n = new OptimizedListInfos($arraytitlename, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($arrayname, _T("Target", "xmppmaster"));
$n->addExtraInfo($arraydeploy['tabdeploy']['start'], _T("Start date", "xmppmaster"));
$n->addExtraInfo($arraystate, _T("Progress / Status", "xmppmaster"));
$n->addExtraInfo($tolmach, _T("Total Machines", "xmppmaster"));
$n->addExtraInfo($processmachr, _T("In progress", "xmppmaster"));
$n->addExtraInfo($successmach, _T("Success", "xmppmaster"));
$n->addExtraInfo($errormach, _T("Error", "xmppmaster"));
$n->addExtraInfo($abortmachuser, _T("Aborted", "xmppmaster"));
$n->addExtraInfo($arraydeploy['tabdeploy']['login'], _T("User", "xmppmaster"));
//$n->setTableHeaderPadding(0);
$n->setItemCount($arraydeploy['lentotal']);
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($logs);
$n->addActionItemArray($reloads);
//function AjaxNavBar($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "", $paginator = false) {

$n->setParamInfo($params);
// $n->start = isset($_GET['start'])?$_GET['start']:0;
// $n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage);
$n->start = 0;
$n->end = $arraydeploy['lentotal'];

$n->display();
echo "<br>";
?>
