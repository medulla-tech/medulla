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

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

if (isset($_GET['currenttasks']) && $_GET['currenttasks'] == '1') {
    $status = "";
    $convergence = True;
    $LastdeployINsecond = 3600 * 24;
    $arraydeploy = xmlrpc_get_deploy_convergence($_GET['login'], "", $start, $end, $filter, "convergence");

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
$edit = array();
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

$filter = "";
$start = "0";
$maxperpage = "10";

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

    $edit[] = new ActionItem(
        _T("Convergence", "msc"),
        "convergence",
        "edit",
        "msc",
        "base",
        "computers"
    );

    // Title cleaning to obtain the name of the package
    $line = $arraydeploy['tabdeploy']['title'][$index] ?? '';
    $lineWithoutPrefix = preg_replace('/^(Uninstall )?Convergence on\s*/i', '', $line);
    // Remove tag -@convergence@-
    $lineWithoutTag = preg_replace('/\s*-@convergence@-\s*/i', '', $lineWithoutPrefix);
    // Remove date and time
    $lineWithoutDateTime = preg_replace('/\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*/', ' ', $lineWithoutTag);

    $titleClean = trim($lineWithoutDateTime);

    // PID recovery corresponding to the title cleaned
    $path = xmlrpc_get_pkg_path($titleClean); // New Function
    $pid = $path ? ltrim($path, '/') : '';

    $parentId = xmlrpc_get_convergence_parent_group_id($arraydeploy['tabdeploy']['group_uuid'][$index]);

    // Get the status of the convergence
    $status = xmlrpc_getConvergenceStatusByCommandId($command_id); // New Function
    $rawStatus = $status['/package_api_get1'][$pid];

    switch ($rawStatus) {
        case 1:
            $actionConvergenceText = _T('Active', 'msc');
            $statusparam = 1; // Actif
            $reloads[] = new ActionItem(
                _("Reschedule Convergence"),
                "rescheduleconvergence",
                "reload",
                "convergenceg",
                "xmppmaster",
                "xmppmaster"
            );
            break;
        case 0:
            $actionConvergenceText = _T('Inactive', 'msc');
            $statusparam = 2; // Inactif
            $reloads[] = new EmptyActionItem1(
                _("Reschedule Convergence"),
                "rescheduleconvergence",
                "reloadg",
                "convergenceg",
                "xmppmaster",
                "xmppmaster"
            );
            break;
        default:
            $statusparam = 0; // Not available
            $actionConvergenceText = _T('Not available', 'msc');
            break;
    }

    $actionParams[] = array(
        "actionconvergenceint"  => $statusparam,
        "actionconvergence"     => $actionConvergenceText,
        "cmd_id"                => $command_id,
        "convergence"           => 1,
        "editConvergence"       => $statusparam,
        "papi"                  => '',
        "from"                  => "base|computers|groupmsctabs|tablogs",
        "gid"                   => $parentId,
        "name"                  => $titleClean,
        "pid"                   => $pid,
        "previous"              => $previous,
    );

    $machineDetails = $arraydeploy['tabdeploy']['machine_details_json'][$index] ?? null;
    if ($machineDetails) {
        $machineDetails = json_decode($machineDetails, true);
        if (!empty($machineDetails)) {
            foreach ($machineDetails as $details) {
                $host = $details['host'] ?? 'Unknown';
                $state = $details['state'] ?? 'Unknown';
            }
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
$groupname = getDisplayGroupName($arraydeploy['tabdeploy']['group_uuid']); // New Function
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

        $editAction = new ActionItem(
            _T("Convergence", "msc"),
            "convergence",
            "edit",
            "msc",
            "base",
            "computers"
        );
        $edit[] = $editAction;

        $arraytitlename[] = '<img class="icon-inline" src="img/other/package.svg"/> ' . $deploy['package_name'];

        $name = "";
        if ($deploy['gid'] != "") {
            $nameInfo = getInfosNameGroup($deploy['gid']);
            $name = isset($nameInfo[$deploy['gid']]['name']) ? $nameInfo[$deploy['gid']]['name'] : $deploy['machine_name'];
            $name = '<img class="icon-inline" src="img/other/machinegroup.svg"/> ' . $name;
        } else {
            $name = '<img class="icon-inline" src="img/other/machine_down.svg"/> ' . $deploy['machine_name'];
        }
        $arrayname[] = $name;

        $date = (array)$deploy['date_start'];
        $arraydeploy['tabdeploy']['start'][] = substr($date['scalar'], 0, 4) . '-' . substr($date['scalar'], 4, 2) . '-' . substr($date['scalar'], 6, 2) . ' ' . substr($date['scalar'], 9);
        if ($deploy['deployment_intervals'] != "") {
            $arraystate[] = '<span class="status-pending">Pending<br><span class="constraint-text">' . _T("Constraint: ", "xmppmaster") .
                $deploy['deployment_intervals'] . '</span></span>';
        } else {
            $arraystate[] = '<span class="status-pending">Pending</span>';
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
    $lineWithoutTag = preg_replace('/\s*-@convergence@-\s*/i', '', $line);
    $lineWithoutDateTime = preg_replace('/\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*/', ' ', $lineWithoutTag);
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
$n->addActionItemArray($edit);
$n->addActionItemArray($reloads);

$n->start = 0;
$n->end = $arraydeploy['lentotal'];

$n->display();
echo "<br>";
?>
