<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
require_once("modules/msc/includes/html.inc.php");
require_once("modules/msc/includes/widgets.inc.php");
require_once("modules/msc/includes/functions.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/command_history.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$DISPLAY_TABLE = TRUE;

$filter = $_GET["filter"];
if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;

$uuid = isset($_GET['uuid']) ? $_GET['uuid'] : '';
$gid = isset($_GET['gid']) ? $_GET['gid'] : '';
$history = isset($_GET['history']) ? $_GET['history'] : '';
$tab = isset($_GET['tab']) ? $_GET['tab'] : '';

$areCommands = False;

if (isset($_GET["commands"])) {
    setCommandsFilter($_GET["commands"]);
}

if ($uuid) {

    $hostname = $_GET['hostname'];
    if (strlen($_GET['bundle_id']) or strlen($_GET['cmd_id'])) {
        $_params = array('uuid' => $uuid, 'cmd_id' => $_GET['cmd_id'], 'b_id' => $_GET['bundle_id'], 'min' => $start, 'max' => $start + $maxperpage, 'filt' => $filter);
        if ($history == 1 || $history == 0)
            $_params['finished'] = $history;
        list($count, $cmds) = displayLogs($_params);
    } else {
        $_params = array('uuid' => $uuid, 'min' => $start, 'max' => $start + $maxperpage, 'filt' => $filter);
        if ($history == 1 || $history == 0)
            $_params['finished'] = $history;
        list($count, $cmds) = displayLogs($_params);
        $areCommands = True;
    }
    $action = "viewLogs";
} elseif ($gid) { # FIXME: same thing to do on groups
    if ($_GET['cmd_id']) {
        $_params = array('gid' => $gid, 'b_id' => quickGet('bundle_id'), 'cmd_id' => $_GET['cmd_id'], 'min' => $start, 'max' => $start + $maxperpage, 'filt' => $filter);
        if ($history == 1 || $history == 0)
            $_params['finished'] = $history;
        if (isset($_GET['cbx_state']))
            $_params['state'] = $_GET['cbx_state'];
        list($count, $cmds) = displayLogs($_params);
    } else {
        $_params = array('gid' => $gid, 'b_id' => $_GET['bundle_id'], 'min' => $start, 'max' => $start + $maxperpage, 'filt' => $filter);
        if ($history == 1 || $history == 0)
            $_params['finished'] = $history;
        list($count, $cmds) = displayLogs($_params);
        $areCommands = True;
    }
    $action = "viewLogs";


    $sum_running = intval($cmds[0][0]['sum_running']);
    $sum_done = intval($cmds[0][0]['sum_done']);
    $sum_failed = intval($cmds[0][0]['sum_failed']);
    $sum_stopped = intval($cmds[0][0]['sum_stopped']);
    $sum_overtimed = intval($cmds[0][0]['sum_overtimed']);
}


$a_cmd = array();
$a_date = array();
$a_enddates = array();
$a_current = array();
$a_percent = array();
$params = array();

/* available buttons */
$actionplay = new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers");
$actionpause = new ActionPopupItem(_T("Pause", "msc"), "msctabspause", "pause", "msc", "base", "computers");
$actiondelete = new ActionPopupItem(_T("Delete", "msc"), "delete", "delete", "msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers");
$actionstatus = new ActionPopupItem(_T("Status", "msc"), "msctabsstatus", "status", "msc", "base", "computers");
$actionstatus->setWidth("400");
$actiondetails = new ActionItem(_T("Details", "msc"), "viewLogs", "display", "msc", "msc", "logs");
$actionempty = new EmptyActionItem();

$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();
$a_status = array();
$a_step_state = array();
$a_progression = array();
$a_delete = array();

$n = null;

if ($areCommands) { // display several commands
    foreach ($cmds as $cmd) { //iterate over each command
        $coh_id = $cmd[1];
        $coh = $cmd[3];
        $cmd = $cmd[0];
        if ($history == '')
            $p = array('tab' => $tab, 'hostname' => $hostname, 'uuid' => $uuid, 'from' => 'msc|logs|viewLogs', 'gid' => $gid);
        else
            $p = array('tab' => $tab, 'hostname' => $hostname, 'uuid' => $uuid, 'from' => 'base|computers|groupmsctabs|grouptablogs', 'gid' => $gid);
        ### gathering command components ###
        if (strlen($cmd['bundle_id']) and !strlen($_GET['cmd_id'])) { // BUNDLE case
            $p['bundle_id'] = $cmd['bundle_id'];
            if (strlen($_GET['bundle_id'])) {
                $p['cmd_id'] = $cmd['id'];
                $a_cmd[] = $cmd['title'];
            } else {
                $bundle = bundle_detail($cmd['bundle_id']);
                if ($bundle[0] == null) {
                    new NotifyWidgetFailure(_T("Can't get bundle for the requested id", "msc"));
                } else {
                    $bundle = $bundle[0];
                    if (!strlen($bundle['title'])) {
                        $a_cmd[] = sprintf(_T("Bundle #%s", "msc"), $cmd['bundle_id']);
                    } else {
                        $a_cmd[] = $bundle['title'];
                    }
                }
            }
        } elseif (!strlen($cmd['bundle_id']) and !strlen($gid)) { // SINGLE COMMAND case
            $a_cmd[] = $cmd['title'];
            $p['cmd_id'] = $cmd['id'];
            $p['coh_id'] = $coh_id;
        } else {
            $a_cmd[] = $cmd['title'];
            $p['cmd_id'] = $cmd['id'];
        }

        if (
                (strlen($uuid) and strlen($cmd['bundle_id']) and !strlen($_GET['bundle_id'])) or
                (strlen($gid) and !strlen($_GET['cmd_id']))
        ) {
            if (!$history) {
                if (strlen($cmd['bundle_id']) and !strlen($_GET['bundle_id'])) {
                    $status = get_command_on_bundle_status($cmd['bundle_id']);
                } elseif (strlen($gid)) {
                    $status = get_command_on_group_status($cmd['id']);
                }
            }
            $icons = state_tmpl_macro($status);
            $icons['play'] == '' ? $a_start[] = $actionempty : $a_start[] = $actionplay;
            $icons['stop'] == '' ? $a_stop[] = $actionempty : $a_stop[] = $actionstop;
            $icons['pause'] == '' ? $a_pause[] = $actionempty : $a_pause[] = $actionpause;
            $a_current[] = '';
        } else {
            if ($coh['current_state'] == 'scheduled' && $cmd['max_connection_attempt'] != $coh['attempts_left']) {
                $coh['current_state'] = 'rescheduled';
            }

            if (isset($statusTable[$coh['current_state']])) {
                $a_current[] = $statusTable[$coh['current_state']];
            } else {
                $a_current[] = $coh['current_state'];
            }
            $p = array('coh_id' => $coh_id, 'cmd_id' => $cmd['id'], 'tab' => $tab, 'uuid' => $uuid, 'hostname' => $hostname, 'from' => 'msc|logs|viewLogs', 'gid' => $gid);
            if (strlen($cmd['bundle_id'])) {
                $p['bundle_id'] = $cmd['bundle_id'];
            }
            $icons = state_tmpl($coh['current_state']);
            $icons['play'] == '' ? $a_start[] = $actionempty : $a_start[] = $actionplay;
            $icons['stop'] == '' ? $a_stop[] = $actionempty : $a_stop[] = $actionstop;
            $icons['pause'] == '' ? $a_pause[] = $actionempty : $a_pause[] = $actionpause;
        }
        if (web_def_allow_delete()){
	    $a_delete[] = $actiondelete;
	} else {
	    $a_delete[] = $actionempty;
	}
        $params[] = $p;
        if ($_GET['cmd_id'] && $cmd['id'] == $_GET['cmd_id']) {
            $a_details[] = $actionempty;
            $a_status[] = $actionempty;
        } else {
            $a_details[] = $actiondetails;
            if (!strlen($gid) and !strlen($cmd['bundle_id'])) {
                $a_status[] = $actionempty;
            } else {
                $a_status[] = $actionstatus;
            }
        }
        if (!is_array($cmd['start_date']))
            $a_date[] = _toDate(array(1970, 1, 1, 0, 0, 0));
        else
            $a_date[] = _toDate($cmd['start_date']);

        if (!is_array($cmd['end_date']))
            $a_enddates[] = _toDate(array(1970, 1, 1, 0, 0, 0));
        else
            $a_enddates[] = _toDate($cmd['end_date']);

        $sum_running = $cmd['sum_running'];
        $sum_done = $cmd['sum_done'];
        $sum_failed = $cmd['sum_failed'];
        $sum_stopped = $cmd['sum_stopped'];
        $sum_overtimed = $cmd['sum_overtimed'];
        $total_machines = $sum_running + $sum_done + $sum_failed + $sum_stopped + $sum_overtimed;
        if ($total_machines != 0)
            $done_percent = round(100 * $sum_done / $total_machines) . '%';
        else
            $done_percent = '-';

        // If bundle, no percent
        if (strlen($cmd['bundle_id']) and !strlen($_GET['cmd_id']))
            $done_percent = '-';

	$a_percent[] = $done_percent;

        if (web_def_allow_delete()){
	    $a_delete[] = $actiondelete;
	} else {
	    $a_delete[] = $actionempty;
	}
    }

    $n = new OptimizedListInfos($a_cmd, _T("Command", "msc"));

    $n->addExtraInfo($a_date, _T("Start date", "msc"));
    $n->addExtraInfo($a_enddates, _T("End date", "msc"));
    $n->addExtraInfo($a_percent, _T("Success percent", "msc"));
    // If $a_current is empty, we don't display it
    if (safeCount(array_filter($a_current, 'strlen')))
        $n->addExtraInfo($a_current, _T("Current state", "msc"));

    $n->addActionItemArray($a_details);
    if (!$history) {
        $n->addActionItemArray($a_start);
        //$n->addActionItemArray($a_pause);
        $n->addActionItemArray($a_stop);
    }
    $n->addActionItemArray($a_status);
    $n->addActionItemArray($a_delete);
} else { // display only one command
    $proxies = array();
    $a_client = array();
    $phase_labels = getPhaseLabels();
    $state_labels = getPhaseStatesLabels();
    foreach ($cmds as $cmd) {
        $coh_id = $cmd[1];
        $coh_status = $cmd[2];
        $coh = $cmd[3];
        $pull_mode = $cmd[4]; // $pull_mode contains UUID of machine, else False
        $cmd = $cmd[0];
        if ((isset($_GET['coh_id']) && $coh_id == $_GET['coh_id']) || !isset($_GET['coh_id'])) {
            if ($history) {
                $d = $coh["end_date"];
            } else {
                $d = $coh["next_launch_date"];
            }

            if (!is_array($d))
                $a_date[] = _toDate(array(1970, 1, 1, 0, 0, 0));
            else
                $a_date[] = _toDate($d);

            if ($uuid) {
                $a_client[] = $cmd['title'];
            } else {
                $a_client[] = $coh['host'];
            }
            $proxy_id = $coh['fk_use_as_proxy'];
            $proxy_str = '';
            if ($proxy_id != '') {
                if ($proxies[$proxy_id] == '') {
                    $lp = get_commands_on_host($proxy_id);
                    $proxies[$proxy_id] = $lp['host'];
                }
                $proxy_str = sprintf(_T(', using proxy %s', 'msc'), $proxies[$proxy_id]);
            }

            if ($cmd['proxy_mode'] == 'none') {
                if ($pull_mode) {
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . _T('Pull', 'msc') . '" src="modules/msc/graph/images/proxy/pull.gif"/> ';
                }
                else {
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . _T('Normal', 'msc') . '" src="modules/msc/graph/images/proxy/no_proxy.png"/> ';
                }
            } elseif ($cmd['proxy_mode'] == 'split') {
                if ($coh['order_in_proxy'] == '')
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . sprintf(_T('Multiple, client mode%s', 'msc'), $proxy_str) . '" src="modules/msc/graph/images/proxy/proxy_client.png"/> ';
                else
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . _T('Multiple, server mode', 'msc') . '" src="modules/msc/graph/images/proxy/proxy_server.png"/> ';
            } elseif ($cmd['proxy_mode'] == 'queue') {
                if ($coh['order_in_proxy'] == '')
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . sprintf(_T('Single, client mode%s', 'msc'), $proxy_str) . '" src="modules/msc/graph/images/proxy/proxy_client.png"/> ';
                else
                    $a_mode[] = '<img style="vertical-align: middle;" title="' . _T('Single, server mode', 'msc') . '" src="modules/msc/graph/images/proxy/proxy_server.png"/> ';
            } else {
                $a_mode[] = '<img style="vertical-align: middle;" title="' . _T('Normal', 'msc') . '" src="modules/msc/graph/images/proxy/no_proxy.png"/> ';
            }

            $a_progression[] = '<img style="vertical-align: middle;" title="' . $statusTable[$coh['uploaded']] . '" src="modules/msc/graph/images/status/' . return_icon($coh['uploaded']) . '"/> '
                    .
                    '<img style="vertical-align: middle;" title="' . $statusTable[$coh['executed']] . '" src="modules/msc/graph/images/status/' . return_icon($coh['executed']) . '"/> '
                    .
                    '<img style="vertical-align: middle;" title="' . $statusTable[$coh['deleted']] . '" src="modules/msc/graph/images/status/' . return_icon($coh['deleted']) . '"/> ';

            if ($coh['current_state'] == 'scheduled' && $cmd['max_connection_attempt'] != $coh['attempts_left']) {
                $coh['current_state'] = 'rescheduled';
            }
            // Set current step state array
            $last_phase = FALSE;
            $running = FALSE;
            foreach ($coh['phases'] as $phase) {
                if ($phase['state'] == 'running' && $coh['current_state'] == 'scheduled')
                    $running = TRUE;
                if ($phase['state'] == 'failed' || $phase['state'] == 'ready' || $phase['state'] == 'running') {
                    $a_step_state[] = sprintf('%s (%s)', $phase_labels[$phase['name']], $state_labels[$phase['state']]);
                    $last_phase = FALSE;
                    break;
                }
                $last_phase = $phase;
            }
            if ($last_phase) {
                $a_step_state[] = sprintf('%s (%s)', $phase_labels[$phase['name']], $state_labels[$phase['state']]);
            }

            if (!$running) {
                if (isset($statusTable[$coh['current_state']])) {
                    $global_state = $statusTable[$coh['current_state']];
                } else {
                    $global_state = $coh['current_state'];
                }
                $global_state = sprintf('<img style="vertical-align: middle;" alt="%s" src="modules/msc/graph/images/status/%s"/> &nbsp;&nbsp;', $coh['current_state'], return_icon($coh['current_state'])) . $global_state;
            } else {
                $global_state = sprintf('<img style="vertical-align: middle;" alt="%s" src="modules/msc/graph/images/status/%s"/> &nbsp;&nbsp;%s', 'running', return_icon('running'), _T('Running', 'msc)'));
            }



            $a_current[] = $global_state;
            $p = array('coh_id' => $coh_id, 'cmd_id' => $cmd['id'], 'tab' => $tab, 'uuid' => $uuid, 'hostname' => $coh['host'], 'from' => 'msc|logs|viewLogs', 'gid' => $gid);
            if (strlen($cmd['bundle_id'])) {
                $p['bundle_id'] = $cmd['bundle_id'];
            }

            $params[] = $p;
            $icons = state_tmpl($coh['current_state']);
            $icons['play'] == '' ? $a_start[] = $actionempty : $a_start[] = $actionplay;
            $icons['stop'] == '' ? $a_stop[] = $actionempty : $a_stop[] = $actionstop;
            $icons['pause'] == '' ? $a_pause[] = $actionempty : $a_pause[] = $actionpause;

            if (isset($_GET['coh_id']) && $coh_id == $_GET['coh_id']) {
                $a_details[] = $actionempty;
            } else {
                $a_details[] = $actiondetails;
            }
            if (web_def_allow_delete()){
                $a_delete[] = $actiondelete;
            } else {
	        $a_delete[] = $actionempty;
            }

        }
    }
    # TODO: add the command end timestamp
    if ($history) {
        $datelabel = _T("End date", "msc");
    } else {
        $datelabel = _T("Start date", "msc");
    }

    $n = new OptimizedListInfos($a_mode, _T("Mode", "msc"));
    if ($uuid) {
        $n->addExtraInfo($a_client, _T("Command", "msc"));
    } else {
        $n->addExtraInfo($a_client, _T("Client", "msc"));
    }
    //$n->addExtraInfo($a_date, $datelabel);
    $n->addExtraInfo($a_current, _T("Global State", "msc"));
    //$n->addExtraInfo($a_current, _T("Global State", "msc"));
    $n->addExtraInfo($a_step_state, _T("Current step", "msc"));
    $n->addActionItemArray($a_details);
    if (!$history) {
        $n->addActionItemArray($a_start);
        //$n->addActionItemArray($a_pause);
        $n->addActionItemArray($a_stop);
    }
    $n->addActionItemArray($a_delete);

    $n->col_width = array("30px", "", "", "", "", "");
    $n->setParamInfo($params);
    $n->setTableHeaderPadding(1);
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->start = 0;
    $n->end = $maxperpage;
    $n->disableFirstColumnActionLink();



    if (isset($sum_running)) {

        $pieChart = new raphaelPie('deploy-pie');

        $total = $sum_running + $sum_done + $sum_failed + $sum_stopped + $sum_overtimed;
        $labels = array(
            _T('Running', 'msc') . sprintf(' %d%%  (%d)', 100 * $sum_running / $total, $sum_running),
            _T('Done', 'msc') . sprintf(' %d%% (%d)', 100 * $sum_done / $total, $sum_done),
            _T('Failed', 'msc') . sprintf(' %d%%  (%d)', 100 * $sum_failed / $total, $sum_failed),
            _T('Stopped', 'msc') . sprintf(' %d%%  (%d)', 100 * $sum_stopped / $total, $sum_stopped),
            _T('Overtime', 'msc') . sprintf(' %d%%  (%d)', 100 * $sum_overtimed / $total, $sum_overtimed)
        );


        $pieChart->addData($sum_running, $labels[0], '000-#7991F2-#3D61F2');
        $pieChart->addData($sum_done, $labels[1], '000-#1C9139-#105722');
        $pieChart->addData($sum_failed, $labels[2], '000-#D93D11-#752008');
        $pieChart->addData($sum_stopped, $labels[3], '000-#F2B87E-#ED7D0C');
        $pieChart->addData($sum_overtimed, $labels[4], '000-#919191-#292829');

        $pieChart->legendpos = 'south';
        $pieChart->title = _T('Deploy status', 'msc');

        $mc = new multicol();
        $mc->add($n)
                ->add($pieChart, array('width' => '200px', 'padding' => '30px 0 0 0', 'valign' => 'top'))->display();
        $DISPLAY_TABLE = FALSE;
    }
}

if ($n != null && $DISPLAY_TABLE) {
    $n->setParamInfo($params);
    $n->setTableHeaderPadding(1);
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->start = 0;
    $n->end = $maxperpage;
    $n->disableFirstColumnActionLink();
    $n->display();
}
?>
