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
 * file ajaxteamconvergence.php
 */
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');

global $conf;

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


$maxperpage = $conf["global"]["maxperpage"];
$filter     = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start      = isset($_GET['start']) ? $_GET['start'] : 0;
$end        = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1') {
    $status = "";
    $LastdeployINsecond = 3600 * 24;
    $arraydeploy = xmlrpc_getdeploybyteamuserrecent_for_convergence($_GET['login'], $status, $LastdeployINsecond, $start, $end, $filter);
    $arraynotdeploy = xmlrpc_getnotdeploybyteamuserrecent($_GET['login'], $LastdeployINsecond, $start, $end, $filter);
} else {
    $LastdeployINsecond = 3600 * 2160;
    echo "<h2>" . _T("Past tasks (last 3 months)") . "</h2>";
    $arraydeploy = xmlrpc_get_deploy_by_team_finished($_GET['login'], $LastdeployINsecond, $start, $end, $filter);
}

if (isset($arraydeploy['total_of_rows'])) {
    $arraydeploy['lentotal'] = $arraydeploy['total_of_rows'];
    if (isset($arraynotdeploy['total'])) {
        $arraydeploy['lentotal'] += $arraynotdeploy['total'];
    }
}

$tab = xmlrpc_get_conrainte_slot_deployment_commands($arraydeploy['tabdeploy']['command']);

$arrayname      = array();
$arraytitlename = array();
$arraystate     = array();
$params         = array();
$logs           = array();
$startdeploy    = array();
$endcmd         = array();
$startcmd       = array();
$tolmach        = array();
$successmach    = array();
$errormach      = array();
$abortmachuser  = array();
$processmachr   = array();


foreach ($arraydeploy['tabdeploy']['command'] as $dd => $ss) {
    if (!empty($tab[$arraydeploy['tabdeploy']['command'][$dd]])) {
        $arraydeploy['tabdeploy']['state'][$dd] .= '<br><span title="'
            . _T("Deployment Interval Constraint", "xmppmaster")
            . '" class="constraint-text">'
            . _T("Constraint: ", "xmppmaster")
            . $tab[$arraydeploy['tabdeploy']['command'][$dd]] . "</span>";
    }
}

foreach ($arraydeploy['tabdeploy']['start'] as $ss) {
    if (gettype($ss) == "string") {
        $startdeploy[] = $ss;
    }
}
$arraydeploy['tabdeploy']['start'] = $startdeploy;

foreach ($arraydeploy['tabdeploy']['endcmd'] as $ss) {
    if (is_array($ss)) {
        $ee = $ss;
    } elseif (is_object($ss)) {
        $ee = get_object_vars($ss);
    } else {
        continue;
    }
    $endcmd[] = gmdate("Y-m-d H:i:s", $ee['timestamp']);
}
$arraydeploy['tabdeploy']['endcmd'] = $endcmd;

foreach ($arraydeploy['tabdeploy']['start'] as $ss) {
    if (is_array($ss)) {
        $ee = $ss;
    } elseif (is_object($ss)) {
        $ee = get_object_vars($ss);
    } else {
        continue;
    }
    $startcmd[] = gmdate("Y-m-d H:i:s", $ee['timestamp']);
}
$arraydeploy['tabdeploy']['startcmd'] = $startcmd;

$previous = isset($_GET['previous']) ? $_GET['previous'] : null;

$actionParams = array();
foreach ($arraydeploy['tabdeploy']['command'] as $index => $command_id) {
    $logs[] = new ActionItem(
        _("View deployment details"),
        "viewlogs",
        "audit",
        "",
        "xmppmaster",
        "xmppmaster"
    );

    $actionParams[] = array(
        "cmd_id"      => $command_id,
        "gid"         => $arraydeploy['tabdeploy']['group_uuid'][$index],
        "convergence" => '1',
        "previous"    => $previous
    );
    $machineDetails = json_decode($arraydeploy['tabdeploy']['machine_details_json'][$index], true);
    if (!empty($machineDetails)) {
        foreach ($machineDetails as $details) {
        }
    }
}

for ($i = 0; $i < safeCount($arraydeploy['tabdeploy']['start']); $i++) {
    $param = array();
    $param['uuid']      = $arraydeploy['tabdeploy']['inventoryuuid'][$i];
    $param['hostname']  = $arraydeploy['tabdeploy']['host'][$i];
    $param['gid']       = $arraydeploy['tabdeploy']['group_uuid'][$i];
    $param['cmd_id']    = $arraydeploy['tabdeploy']['command'][$i];
    $param['login']     = $arraydeploy['tabdeploy']['login'][$i];
    $param['title']     = $arraydeploy['tabdeploy']['title'][$i];
    $param['start']     = $arraydeploy['tabdeploy']['start'][$i];
    $param['endcmd']    = $arraydeploy['tabdeploy']['endcmd'][$i];
    $param['startcmd']  = $arraydeploy['tabdeploy']['startcmd'][$i];
    $param['sessionid'] = $arraydeploy['tabdeploy']['sessionid'][$i];
    $params[] = $param;
}

$lastcommandid = get_array_last_commands_on_cmd_id_start_end($arraydeploy['tabdeploy']['command']);
$statarray     = xmlrpc_getarraystatbycmd($arraydeploy['tabdeploy']['command']);
$convergence   = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$groupname     = getDisplayGroupName($arraydeploy['tabdeploy']['group_uuid']);
$index = 0;
foreach ($arraydeploy['tabdeploy']['group_uuid'] as $index => $groupid) {
    $machineDetails = json_decode($arraydeploy['tabdeploy']['machine_details_json'][$index], true);
    $done = 0; $aborted = 0; $inprogress = 0;
    if (!empty($machineDetails)) {
        foreach ($machineDetails as $details) {
            $state = $details['state'] ?? 'Unknown';
            if ($state === "DEPLOYMENT DIFFERED" || strpos($state, "DEPLOYMENT START") !== false) {
                if ((strtotime($arraydeploy['tabdeploy']['endcmd'][$index]) - time()) < 0) {
                    echo "Error for host {$details['host']}: DEPLOY ERROR TIMEOUT\n";
                }
            }
            if (strpos($state, "ABORT") !== false) {
                $aborted++;
            } elseif (strpos($state, "SUCCESS") !== false) {
                $done++;
            } else {
                $inprogress++;
            }
        }
    }
    $totalmachinedeploy = $arraydeploy['tabdeploy']['nb_machines'][$index] ?? 0;
    $tolmach[] = $totalmachinedeploy;
    $inprogressPercent = ($totalmachinedeploy > 0) ? round(($inprogress / $totalmachinedeploy) * 100, 1) : 0;
    $processmachr[] = "{$inprogress} ({$inprogressPercent}%)";
    $successPercent = ($totalmachinedeploy > 0) ? round(($done / $totalmachinedeploy) * 100, 1) : 0;
    $successmach[] = "{$done} ({$successPercent}%)";
    $abortedPercent = ($totalmachinedeploy > 0) ? round(($aborted / $totalmachinedeploy) * 100, 1) : 0;
    $abortmachuser[] = "{$aborted} ({$abortedPercent}%)";
    $progressrate = ($totalmachinedeploy > 0) ? round(($done / $totalmachinedeploy) * 100, 2) : 0;
    $color = match (true) {
        $progressrate <= 10 => "#ff0000",
        $progressrate <= 20 => "#ff3535",
        $progressrate <= 30 => "#ff5050",
        $progressrate <= 40 => "#ff8080",
        $progressrate <= 50 => "#ffA0A0",
        $progressrate <= 60 => "#c8ffc8",
        $progressrate <= 70 => "#97ff97",
        $progressrate <= 80 => "#64ff64",
        $progressrate <= 90 => "#2eff2e",
        default => "#00ff00",
    };
    // Determine icon class based on status
    $iconClass = 'icon-inline';
    if ($progressrate == 0) {
        $iconClass .= ' icon-error';
        $arraystate[] = "<span class='status-group-error'>{$progressrate}%</span>";
    } elseif ($progressrate == 100) {
        if ($successPercent == 0) {
            $iconClass .= ' icon-error';
            $arraystate[] = '<span class="status-group-error">' . _T('GROUP ERROR', 'xmppmaster') . '</span>';
        } elseif ($successPercent > 0 && $successPercent < 100) {
            $iconClass .= ' icon-partial';
            $arraystate[] = '<span class="status-group-partial">' . _T('GROUP PARTIAL SUCCESS', 'xmppmaster') . '</span>';
        } else {
            $iconClass .= ' icon-success';
            $arraystate[] = '<span class="status-group-success">' . _T('GROUP FULL SUCCESS', 'xmppmaster') . '</span>';
        }
    } else {
        $arraystate[] = "<span style='background-color:{$color};'>{$progressrate}%</span>";
    }
    $namegrp = $groupname[$groupid] ?? _T("This group doesn't exist", "xmppmaster");
    $arrayname[] = "<span class='text-underline'><img class='icon-inline' src='img/other/machinegroup.svg'/> {$namegrp}</span>";
    if ($convergence[$arraydeploy['tabdeploy']['command'][$index]] != 0) {
        $arraytitlename[] = "<img class='{$iconClass}' src='img/other/convergence.svg'/> {$arraydeploy['tabdeploy']['title'][$index]}";
    } else {
        $arraytitlename[] = "<img class='{$iconClass}' src='img/other/package.svg'/> {$arraydeploy['tabdeploy']['title'][$index]}";
    }
}

if(isset($arraynotdeploy))
{
  foreach($arraynotdeploy['elements'] as $id=>$deploy)
  {
      $param = [
      'cmd_id'=>$deploy['cmd_id'],
      'login'=>$deploy['login'],
      'gid'=>$deploy['gid'],
      'uuid'=>$deploy['uuid_inventory']];
      $logs[] = $logAction;
      $params[] = $param;

      $arraytitlename[] = '<img class="icon-inline" src="img/other/package.svg"/> '.$deploy['package_name'];

      $name = "";
      if($deploy['gid'] != "")
      {
          $name = getInfosNameGroup($deploy['gid']);
          $name = $name[$deploy['gid']]['name'];
          $name = '<img class="icon-inline" src="img/other/machinegroup.svg"/> '.$name;
        }

      else
      {
          $name = $deploy['machine_name'];
          $name = '<img class="icon-inline" src="img/other/machine_down.svg"/> '.$name;
      }
      $arrayname[] = $name;

      $date = (array)$deploy['date_start'];
      $arraydeploy['tabdeploy']['start'][] = date("Y-m-d H:i:s",$date['timestamp']);
      //TODO
      $arraystate[] = '<span class="status-pending">Pending</span>';
      $tolmach[] = $deploy['nb_machines'];
      $processmachr[] = '0 (0%)';
      $successmach[] = '0 (0%)';
      $errormach[] = '0 (0%)';
      $abortmachuser[] = '0 (0%)';
      $arraydeploy['tabdeploy']['login'][] = $deploy['login'];
  }
}

$newArrayTitleName = array();
foreach ($arraytitlename as $line) {
    $lineWithoutTag = preg_replace('/\s*-@convergence@-\s*/i', '', $line);
    $lineWithoutDateTime = preg_replace('/\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*/', ' ', $lineWithoutTag);
    $newArrayTitleName[] = trim($lineWithoutDateTime);
}
$n = new OptimizedListInfos( $newArrayTitleName, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($arrayname, _T("Target", "xmppmaster"), "150px");
$n->addExtraInfo($arraystate, _T("Progress / Status", "xmppmaster"));
$n->addExtraInfo($tolmach, _T("Total Machines", "xmppmaster"));
$n->addExtraInfo($processmachr, _T("In progress", "xmppmaster"));
$n->addExtraInfo($successmach, _T("Success", "xmppmaster"));
$n->addExtraInfo($errormach, _T("Error", "xmppmaster"));
$n->addExtraInfo($abortmachuser, _T("Aborted", "xmppmaster"));
$n->addExtraInfo($arraydeploy['tabdeploy']['login'], _T("User", "xmppmaster"));
$n->setItemCount($arraydeploy['lentotal']);
$n->setNavBar(new AjaxNavBar($arraydeploy['lentotal'], $filter, "updateSearchParamformRunning"));
$n->setParamInfo($actionParams);
$n->addActionItemArray($logs);
$n->start = 0;
$n->end = $arraydeploy['lentotal'];

$n->display();
echo "<br>";
?>
