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
 * file ajaxconvergence.php
 */
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1') {
    $status = "";
    $convergence = True;
    $LastdeployINsecond = 3600 * 24;
    echo "<h2>" . _T("Current tasks (last 24 hours)") . "</h2>";
    $arraydeploy = xmlrpc_get_deploy_convergence($_GET['login'], $LastdeployINsecond, $start, $end, $filter, "command");

    $arraynotdeploy = xmlrpc_get_deploy_inprogress_by_team_member($_GET['login'], $LastdeployINsecond, $start, $end, $filter);
} else {
    echo "<h2>" . _T("Past tasks (last 3 months)") ."</h2>";
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

foreach ($arraydeploy['tabdeploy']['command'] as $dd => $ss) {
    if ($tab[$arraydeploy['tabdeploy']['command'][$dd]] != "") {
        $arraydeploy['tabdeploy']['state'][$dd] = $arraydeploy['tabdeploy']['state'][$dd].'<br><span title="'._T("Deployment Interval Constraint", "xmppmaster"). '" style="opacity: 0.5;font-size: x-small;color:  Gray;">'._T("Constraint: ", "xmppmaster").$tab[$arraydeploy['tabdeploy']['command'][$dd]]."</span>";
    }
}

foreach($arraydeploy['tabdeploy']['start'] as $ss) {
    if (gettype($ss) == "string") {
        $startdeploy[] = $ss;
    }
}

$arraydeploy['tabdeploy']['start'] = $startdeploy;

foreach($arraydeploy['tabdeploy']['endcmd'] as $ss) {
    if (is_array($ss)) {
        $ee = $ss;
    } else {
        $ee = get_object_vars($ss);
    }
    $endcmd[] = gmdate("Y-m-d H:i:s", $ee['timestamp']);
}
$arraydeploy['tabdeploy']['endcmd'] = $endcmd;

foreach($arraydeploy['tabdeploy']['start'] as $ss) {
    if (is_array($ss)) {
        $ee = $ss;
    } else {
        $ee = get_object_vars($ss);
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

    $reloads[] = new ActionItem(
        _("Reschedule Convergence"),
        "rescheduleconvergence",
        "reload",
        "",
        "xmppmaster",
        "xmppmaster"
    );

    $actionParams[] = array(
        "cmd_id" => $command_id,
        "gid"    => $arraydeploy['tabdeploy']['group_uuid'][$index],
        "convergence" => '1',
        "previous" => $previous,
    );
    $machineDetails = json_decode($arraydeploy['tabdeploy']['machine_details_json'][$index], true);
    if (!empty($machineDetails)) {
        foreach ($machineDetails as $details) {
            $host = $details['host'] ?? 'Unknown';
            $state = $details['state'] ?? 'Unknown';
        }
    }
}

for ($i = 0; $i < safeCount($arraydeploy['tabdeploy']['start']); $i++) {
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
    $params[] = $param;
}

$lastcommandid = get_array_last_commands_on_cmd_id_start_end($arraydeploy['tabdeploy']['command']);
$statarray = xmlrpc_getarraystatbycmd($arraydeploy['tabdeploy']['command']);
$convergence = is_array_commands_convergence_type($arraydeploy['tabdeploy']['command']);
$groupname = getInfosNameGroup($arraydeploy['tabdeploy']['group_uuid']);
$index = 0;

foreach ($arraydeploy['tabdeploy']['group_uuid'] as $index => $groupid) {
    $error = false;

    $machineDetails = json_decode($arraydeploy['tabdeploy']['machine_details_json'][$index], true);

    $done = 0;
    $aborted = 0;
    $inprogress = 0;

    if (!empty($machineDetails)) {
        foreach ($machineDetails as $details) {
            $host = $details['host'] ?? 'Unknown';
            $state = $details['state'] ?? 'Unknown';
            $jid_machine = $details['jid_machine'] ?? 'Unknown';
            $jid_relay = $details['jid_relay'] ?? 'Unknown';
            $sessionid = $details['sessionid'] ?? 'Unknown';

            if ($state === "DEPLOYMENT DIFFERED" || strpos($state, "DEPLOYMENT START") !== false) {
                if ((strtotime($arraydeploy['tabdeploy']['endcmd'][$index]) - time()) < 0) {
                    $error = true;
                    echo "Erreur pour le host {$host}: DEPLOY ERROR TIMEOUT\n";
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

    if ($progressrate == 0) {
        $arraystate[] = "<span style='font-weight: bold; color : red;'>{$progressrate}%</span>";
    } elseif ($progressrate == 100) {
        if ($successPercent == 0) {
            $arraystate[] = '<span style="font-weight: bold; color: red;">' . _T('GROUP ERROR', 'xmppmaster') . '</span>';
        } elseif ($successPercent > 0 && $successPercent < 100) {
            $arraystate[] = '<span style="font-weight: bold; color: orange;">' . _T('GROUP PARTIAL SUCCESS', 'xmppmaster') . '</span>';
        } else {
            $arraystate[] = '<span style="font-weight: bold; color: green;">' . _T('GROUP FULL SUCCESS', 'xmppmaster') . '</span>';
        }
    } else {
        $arraystate[] = "<span style='background-color:{$color};'>{$progressrate}%</span>";
    }

    $namegrp = $groupname[$groupid]['name'] ?? _T("This group doesn't exist", "xmppmaster");
    $arrayname[] = "<span style='text-decoration: underline;'><img style='position:relative;top: 5px;' src='img/other/machinegroup.svg' width='25' height='25' /> {$namegrp}</span>";

    if ($convergence[$arraydeploy['tabdeploy']['command'][$index]] != 0) {
        $arraytitlename[] = "<img style='position:relative;top: 5px;' src='img/other/convergence.svg' width='25' height='25' /> {$arraydeploy['tabdeploy']['title'][$index]}";
    } else {
        $arraytitlename[] = "<img style='position:relative;top: 5px;' src='img/other/package.svg' width='25' height='25' /> {$arraydeploy['tabdeploy']['title'][$index]}";
    }
}

if (isset($arraynotdeploy)) {
    foreach ($arraynotdeploy['elements'] as $id => $deploy) {
        $param = [
            'cmd_id' => $deploy['cmd_id'],
            'login'  => $deploy['login'],
            'gid'    => $deploy['gid'],
            'uuid'   => $deploy['uuid_inventory'],
            'convergence' => '1',
            'previous' => $previous,
        ];
        $params[] = $param;

        $logAction = new ActionItem(
            _("View deployment details"),
            "viewlogs",
            "audit",
            "",
            "xmppmaster",
            "xmppmaster"
        );
        $logs[] = $logAction;

        $arraytitlename[] = '<img style="position:relative;top:5px;" src="img/other/package.svg" width="25" height="25" /> ' . $deploy['package_name'];

        $name = "";
        if ($deploy['gid'] != "") {
            $nameInfo = getInfosNameGroup($deploy['gid']);
            $name = isset($nameInfo[$deploy['gid']]['name']) ? $nameInfo[$deploy['gid']]['name'] : $deploy['machine_name'];
            $name = '<img style="position:relative;top:5px;" src="img/other/machinegroup.svg" width="25" height="25" /> ' . $name;
        } else {
            $name = '<img style="position:relative;top:5px;" src="img/other/machine_down.svg" width="25" height="25" /> ' . $deploy['machine_name'];
        }
        $arrayname[] = $name;

        $date = (array)$deploy['date_start'];
        $arraydeploy['tabdeploy']['start'][] = substr($date['scalar'], 0, 4) . '-' . substr($date['scalar'], 4, 2) . '-' . substr($date['scalar'], 6, 2) . ' ' . substr($date['scalar'], 9);
        if ($deploy['deployment_intervals'] != "") {
            $arraystate[] = '<span style="font-weight: bold; color: orange;">Pending<br><span style="opacity: 0.5;font-size: x-small;color: Gray;">' . _T("Constraint: ", "xmppmaster") .
                $deploy['deployment_intervals'] . '</span></span>';
        } else {
            $arraystate[] = '<span style="font-weight: bold; color: orange;">Pending</span>';
        }
        $tolmach[] = $deploy['nb_machines'];
        $processmachr[] = '0 (0%)';
        $successmach[] = '0 (0%)';
        $errormach[] = '0 (0%)';
        $abortmachuser[] = '0 (0%)';
        $arraydeploy['tabdeploy']['login'][] = $deploy['login'];
        $reloadAction = new ActionItem(
            _("Reschedule Convergence"),
            "rescheduleconvergence",
            "reload",
            "",
            "xmppmaster",
            "xmppmaster"
        );
        $reloads[] = $reloadAction;
    }
}

$newArrayTitleName = array();
foreach ($arraytitlename as $line) {
    $lineWithoutDateTime = preg_replace('/\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*/', ' ', $line);
    $newArrayTitleName[] = trim($lineWithoutDateTime);
}

$n = new OptimizedListInfos($newArrayTitleName, _T("Deployment", "xmppmaster"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($arrayname, _T("Target", "xmppmaster"));
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
$n->addActionItemArray($reloads);

$n->start = 0;
$n->end = $arraydeploy['lentotal'];

$n->display();
echo "<br>";
?>
<style>
progress {
  width: 100px;
  height: 9px;
  margin:-5px;
  background-color: #ffffff;
  border-style: solid;
  border-width: 1px;
  border-color: #dddddd;
  padding: 3px 3px 3px 3px;
}

progress::-webkit-progress-bar {
    background: #f3f3f3 ;
}

progress::-webkit-progress-value {
     Background: #ef9ea9;
}

</style>
