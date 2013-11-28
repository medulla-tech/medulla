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
require_once("functions.php"); # for return_icon
require_once("utilities.php"); # for pretty bw display
require_once("mscoptions_xmlrpc.php"); # to read msc.ini

class CommandOnHost {

    function CommandOnHost($coh) {
        $statusTable = getStatusTable();
        $this->db_coh = get_commands_on_host($coh);
        $this->db_cmd = command_detail($this->db_coh['fk_commands']);
        $this->values = array(
            array(_T('Host', 'msc'), $this->db_coh['host'], 1),
            array(_T('Command name', 'msc'), $this->db_cmd['title'], 1),
            array(_T('Start date', 'msc'), _toDate($this->db_cmd['start_date']), 1),
            array(_T('End date', 'msc'), _toDate($this->db_cmd['end_date']), 1),
                //array(_T('Current State', 'msc'), $statusTable[$this->db_coh['current_state']], 1),
                //array(_T('awoken', 'msc'), _plusIcon($this->db_coh['awoken']), 1),
                /* array(_T('uploaded', 'msc'), _plusIcon($this->db_coh['uploaded']), 1),
                  array(_T('executed', 'msc'), _plusIcon($this->db_coh['executed']), 1),
                  array(_T('deleted', 'msc'), _plusIcon($this->db_coh['deleted']), 1),
                  array(_T('inventoried', 'msc'), _plusIcon($this->db_coh['inventoried']), 1),
                  array(_T('rebooted', 'msc'), _plusIcon($this->db_coh['rebooted']), 1),
                  array(_T('halted', 'msc'), _plusIcon($this->db_coh['halted']), 1) */
        );
    }

    function display() {
        $n = new ListInfos(array_map("_names", $this->values), _T('Name', 'msc'));
        $n->addExtraInfo(array_map("_values", $this->values), _T('Value', 'msc'));
        //$n->addActionItem($objActionItem)
        //$n->setRowsPerPage(count($this->values));
        $n->setRowsPerPage();
        $n->drawTable(0);
        print "<br/>";
    }

    function quickDisplay($actions = array(), $params = array()) {
        $statusTable = getStatusTable();
        $n = null;
        $params = array_merge($params, array(
            'cmd_id' => $_GET['cmd_id'],
            'bundle_id' => $_GET['bundle_id'],
            'coh_id' => $_GET['coh_id'],
            'uuid' => $_GET['uuid'],
            'from' => 'msc|logs|consult',
            'tab' => 'tablogs',
            'hostname' => $this->db_coh['host']
                )
        );
        foreach ($this->values as $col) {
            if ($col[2]) {
                if ($n) {
                    $n->addExtraInfo(array($col[1]), $col[0]);
                } else {
                    $n = new ListInfos(array($col[1]), $col[0]);
                }
            }
        }
        $n->setParamInfo(array($params));
        $n->disableFirstColumnActionLink();
        $n->addActionItem(new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers"));
        $n->addActionItem(new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers"));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->col_width = array("50px", "50px", "50px", "50px", "50px", "50px", "50px", "50px", "50px");
        $n->drawTable(0);
        print "<br/>";
    }

}

class Bundle {

    function Bundle($bundle_id) {
        $this->db_bundle = bundle_detail($bundle_id);
        if (!$this->db_cmd) { # use does not have the good permissions
            return false;
        }
    }

    function quickDisplay($actions = array(), $params = array()) {
        if (!$this->db_bundle || $this->db_bundle[0] == null) { # user does not have the good permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return false;
        }
        if (!strlen($this->db_bundle[0]['title'])) {
            $this->db_bundle[0]['title'] = "Bundle #" . $this->db_bundle[0]['id'];
        }

        $bdl_done = $bdl_failed = $bdl_sum_failed = $bdl_running = $bdl_stopped = 0;

        // Counting all commands sum
        foreach ($this->db_bundle[1] as $cmd) {
            $bdl_done += $cmd['sum_done'];
            $bdl_failed += $cmd['sum_failed'];
            $bdl_sum_failed += $cmd['sum_overtimed'];
            $bdl_running += $cmd['sum_running'];
            $bdl_stopped += $cmd['sum_stopped'];
        }

        $bdl_total = $bdl_done + $bdl_failed + $bdl_sum_failed + $bdl_running + $bdl_stopped;
        if ($bdl_total != 0)
            $bdl_percent = intval(100 * $bdl_done / $bdl_total) . '%';
        else
            $bdl_percent = '-';

        $n = new ListInfos(array($this->db_bundle[0]['title']), _T('Bundle', 'msc'));
        $n->addExtraInfo(array(_toDate($this->db_bundle[1][0]['start_date'])), _T('Start date', 'msc'));
        $n->addExtraInfo(array(_toDate($this->db_bundle[1][0]['end_date'])), _T('End date', 'msc'));
        $n->addExtraInfo(array($bdl_percent), _T('Bundle success percent', 'msc'));

        $n->addActionItem(new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers"));
        $n->addActionItem(new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers"));

        $params['title'] = $this->db_bundle[0]['title'];
        $params['bundle_id'] = $this->db_bundle[1][0]['fk_bundle'];
        $params['from'] = 'msc|logs|viewLogs';
        if (isset($_GET['uuid']))
            $params['uuid'] = $_GET['uuid'];
        if (isset($_GET['gid']))
            $params['gid'] = $_GET['gid'];
        //debug($this->db_bundle[1][0]['fk_bundle']);

        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
        print '<br/><br/>';
        return true;
    }

}

class Command {

    function Command($cmd) {
        $this->db_cmd = command_detail($cmd);
        $this->error = false;
        if (!$this->db_cmd) { # use does not have the good permissions
            return false;
        }
        $this->values = array(
            array(_T('Command name', 'msc'), $this->db_cmd['title'], 1),
            //array(_T('Creation date', 'msc'), _toDate($this->db_cmd['creation_date']), 1),
            array(_T('Start date', 'msc'), _toDate($this->db_cmd['start_date']), 1),
            array(_T('End date', 'msc'), _toDate($this->db_cmd['end_date']), 1),
            array(_T('User command creator', 'msc'), $this->db_cmd['creator'], 0),
            array(_T('Execute file', 'msc'), $this->db_cmd['start_file'], 0),
            array(_T('Execution arguments', 'msc'), $this->db_cmd['parameters'], 0),
            array(_T('Start execute file', 'msc'), $this->db_cmd['start_script'], 0),
            array(_T('Start inventory agent', 'msc'), $this->db_cmd['do_inventory'], 0),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'), $this->db_cmd['do_wol'], 0),
            array(_T('Delay between two connections', 'msc'), $this->db_cmd['next_connection_delay'], 0),
            array(_T('Command start date', 'msc'), _toDate($this->db_cmd['start_date']), 0),
            array(_T('Command expiry date', 'msc'), _toDate($this->db_cmd['end_date']), 0),
        );
    }

    function display() {
        if (!$this->db_cmd) { # user do not have the right permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return false;
        }
        $name = array_map("_names", $this->values);
        $value = array_map("_values", $this->values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($this->values));

        $n->drawTable(0);
        print '<br/>';
        return true;
    }

    function quickDisplay($actions = array(), $params = array()) {
        if (!$this->db_cmd) { # user do not have the right permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return false;
        }
        $n = null;
        foreach ($this->values as $col) {
            if ($col[2]) {
                if ($n) {
                    $n->addExtraInfo(array($col[1]), $col[0]);
                } else {
                    $n = new ListInfos(array($col[1]), $col[0]);
                }
            }
        }

        $params = array_merge($params, array(
            'cmd_id' => $_GET['cmd_id'],
            'gid' => $_GET['gid'],
            'from' => 'msc|logs|consult'
                )
        );

        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        // Start/Stop buttons
        $n->addActionItem(new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers"));
        $n->addActionItem(new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers"));
        $n->disableFirstColumnActionLink();
        $n->drawTable(0);
        print '<br/>';
        return true;
    }

}

function my_convert($str) {
    return _T($str, 'msc');
}

function i18nparts($str) {
    if (is_array($str)) {
        return implode(', ', array_map('my_convert', $str));
    } elseif (!empty($str))
        return implode(', ', array_map('my_convert', explode(',', $str)));
    else
        return _T('<i>not set</i>', 'msc');
}

class CommandHistory {

    function CommandHistory($coh_id) {
        // TODO : ch is a list, we have to chose the good one (ie : the most recent date)
        $this->db_ch = get_command_history($coh_id);
        $this->db_coh = get_commands_on_host($coh_id);
        if ($this->db_coh['fk_use_as_proxy'])
            $this->db_lproxy = get_commands_on_host($this->db_coh['fk_use_as_proxy']);
        else
            $this->db_lproxy = NULL;
        $this->db_cmd = command_detail($this->db_coh['fk_commands']);
    }

    function display() {
        // display parameters
        if (!$this->db_cmd) { # use does not have the good permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return;
        }


        if ($this->db_cmd['start_date'])
            if ($this->db_cmd['end_date'])
                $validity = sprintf(_T('<i>from</i> %s <i>to</i> %s', 'msc'), _toDate($this->db_cmd['start_date']), _toDate($this->db_cmd['end_date']));
            else
                $validity = sprintf(_T('<i>from</i> %s', 'msc'), _toDate($this->db_cmd['start_date']));
        else
        if ($this->db_cmd['end_date'])
            $validity = sprintf(_T('<i>to</i> %s', 'msc'), _toDate($this->db_cmd['end_date']));
        else
            $validity = _T('<i>forever</i>', 'msc');

        if ($this->db_cmd['deployment_intervals']) {
            $deploy_interv = str_replace(array('-', ','), array(' - ', ', '), $this->db_cmd['deployment_intervals']);
        } else
            $deploy_interv = _T('<i>whole day</i>', 'msc');

        if ($this->db_cmd['deployment_intervals']) {
            $deploy_interv = str_replace(array('-', ','), array(' - ', ', '), $this->db_cmd['deployment_intervals']);
        } else
            $deploy_interv = _T('<i>whole day</i>', 'msc');

        if ($this->db_coh['next_launch_date'])
            $next_launch_date = _toDate($this->db_coh['next_launch_date']);
        else
        if ($this->db_cmd['start_date'])
            $next_launch_date = _toDate($this->db_cmd['start_date']);
        else
            $next_launch_date = _T('<i>as soon as possible</i>', 'msc');

        if ($this->db_coh['start_date'])
            $start_date = _toDate($this->db_coh['start_date']);
        else
            $start_date = _T('<i>not yet available</i>', 'msc');

        if ($this->db_coh['end_date'])
            $end_date = _toDate($this->db_coh['end_date']);
        else
            $end_date = _T('<i>not yet available</i>', 'msc');

        if ($this->db_coh['last_wol_attempt'])
            $last_wol_attempt = _toDate($this->db_coh['last_wol_attempt']);
        else
            $last_wol_attempt = _T('<i>not available</i>', 'msc');

        if ($this->db_cmd['start_file'])
            if ($this->db_cmd['parameters'])
                $command_line = sprintf(_T('%s %s', 'msc'), $this->db_cmd['start_file'], $this->db_cmd['parameters']);
            else
                $command_line = sprintf(_T('%s <i>(no additional parameter given)</i>', 'msc'), $this->db_cmd['start_file']);
        else
            $command_line = _T('<i>not set</i>', 'msc');

        if ($this->db_coh['order_in_proxy'] == '')
            $proxy_priority = _T('None (Local Proxy Client)', 'msc');
        else
            $proxy_priority = sprintf(_T('%s (Local Proxy Server)', 'msc'), $this->db_coh['order_in_proxy']);

        if ($this->db_cmd['proxy_mode'] == 'split')
            $proxy_mode = _T('Multiple', 'msc');
        elseif ($this->db_cmd['proxy_mode'] == 'queue')
            $proxy_mode = _T('Single with fallback', 'msc');
        elseif ($this->db_cmd['proxy_mode'] == 'none') {
            $proxy_mode = _T('No proxy', 'msc');
            $proxy_priority = _T('None', 'msc');
        } else {
            $proxy_mode = _T('<i>not available</i>', 'msc');
            $proxy_priority = _T('<i>not available</i>', 'msc');
        }

        if ($this->db_lproxy)
            $current_proxy = $this->db_lproxy['host'];
        else
            $current_proxy = _T('<i>not available</i>', 'msc');

        // gettext obfucation
        _T('enable', 'msc');
        _T('disable', 'msc');
        _T('done', 'msc');
        _T('failed', 'msc');
        _T('over_time', 'msc');
        _T('out_of_interval', 'msc');

        // =====================================================================

        function formatLog($hist) {
            $i = 1;
            if (($hist['state'] == 'upload_in_progress') && ($hist['error_code'] == '0') && (array_key_exists('stderr', $hist)) && ($i != count($this->db_ch)) && (strpos($hist['stderr'], 'is available on mirror') !== False)) {
                /*
                  We are displaying which package server was used in push pull
                  mode. We want to keep the led green instead of orange to
                  tell the user that there was no problem.
                 */
                $staticon = history_stat2icon("upload_done");
            } elseif ($hist['state'] == 'wol_failed' && $hist['error_code'] == '2001') {
                $staticon = history_stat2icon("stop");
            } else {
                $staticon = history_stat2icon($hist['state']);
            }
            $history = date("Y-m-d H:i:s", $hist['date']);
            /* Split lines in stdout and stderr */
            if (gettype($hist["stdout"]) != 'array')
                $hist["stdout"] = split("\n", $hist["stdout"]);
            if (gettype($hist["stderr"]) != 'array')
                $hist["stderr"] = split("\n", $hist["stderr"]);
            if (count($hist["stdout"]) > 0 &&
                    !(count($hist["stdout"]) == 1 && $hist["stdout"][0] == '')
            ) {
                $hist["stderr"] = array_merge($hist["stderr"], $hist["stdout"]);
            }
            if (strpos($hist['state'], '_failed') !== False || ($hist['error_code'] > 4501 && $hist['error_code'] < 5000)) {
                $msgs = array(
                    // BIG HUGE TODO: should get base value (230) from the agent (PULSE2_WRAPPER_ERROR_PRECHECK_BASE from consts.py)
                    /* When SSH returns 255, an error occurred while
                      connecting to the host. On some platforms like
                      RHEL 4, buggy SSH returns 1 */
                    255 => _T("Error while connecting to secure agent on this host. Please check network connectivity, and that the secure agent is installed on this host.", 'msc'),
                    /* Known exit codes : killed by signal */
                    200 + 9 => _T("The script was killed by Pulse 2 (timeout ?).", 'msc'),
                    200 + 15 => _T("The script was terminated by Pulse 2.", 'msc'),
                    /* Known exit codes : pre-check */
                    240 + 0 => _T("Something goes wrong while checking client identity.", 'msc'),
                    240 + 1 => _T("The current host name doesn't match the host name from the inventory database.", 'msc'),
                    240 + 2 => _T("The current host IP address doesn't match the IP address from the inventory database.", 'msc'),
                    240 + 3 => _T("The current host MAC address doesn't match the MAC address from the inventory database.", 'msc'),
                    /* Known exit codes :  */
                    4000 + 1 => sprintf(_T("The package '%s' is not available on any mirror.", "msc"), $hist['stderr'][0]),
                    4000 + 2 => sprintf(_T("Can't get files URI for package '%s' on mirror %s.\nPlease check that the package and its files have not been modified since the planning of the command.", "msc"), $hist['stderr'][0], $hist['stderr'][1]),
                    4000 + 3 => sprintf(_T("Can't get files URI for package '%s' on fallback mirror %s.\nPlease check that the package and its files have not been modified since the planning of the command.", "msc"), $hist['stderr'][0], $hist['stderr'][1]),
                    4000 + 4 => sprintf(_T("An error occurred when trying to contact the mirror '%s' : the connection was refused.", "msc"), $hist['stderr'][0]),
                    4000 + 5 => sprintf(_T("An error occurred when trying to contact the fallback mirror '%s' : the connection was refused.", "msc"), $hist['stderr'][0]),
                    4000 + 6 => sprintf(_T("An error occurred when trying to contact the mirror '%s' : the mountpoint doesn't exists.", "msc"), $hist['stderr'][0]),
                    4000 + 7 => sprintf(_T("An error occurred when trying to contact the fallback mirror '%s' : the mountpoint doesn't exists.", "msc"), $hist['stderr'][0]),
                    4500 + 8 => sprintf(_T("Package '%s' is NOT available on primary mirror %s\nPackage '%s' is available on fallback mirror %s", "msc"), $hist['stdout'][0], $hist['stdout'][1], $hist['stdout'][2], $hist['stdout'][3]),
                    4500 + 9 => sprintf(_T("Package '%s' is available on primary mirror %s", "msc"), $hist['stdout'][0], $hist['stdout'][1]),
                );
                if ($hist['error_code'] >= 4001 && $hist['error_code'] < 5000) {
                    $hist["stderr"] = array('');
                }
                if (array_key_exists($hist['error_code'], $msgs)) {
                    $hist['stderr'][] = $msgs[$hist['error_code']];
                }
            }
            $raw_errors = array_map('_colorise', array_filter($hist["stderr"]));
            $purge_errors = array();

            foreach ($raw_errors as $error)
                if (isset($error))
                    array_push($purge_errors, $error);

            return array($history, $purge_errors);
        }

        // =====================================================================
        ### Display command phases ###
        $phases = $this->db_coh['phases'];
        $phase_labels = getPhaseLabels();

        $hidden_phases = array(
            'done'
        );

        $phase_names = array();
        $phase_dates = array();
        $phase_states = array();
        $phase_logs = array();
        $btn_showfull_log = array();

        // Organize logs by phase
        $logs_by_phase = array();

        foreach ($this->db_ch as $entry) {
            // if $logs_by_phase doesnt contain phase key we create it
            if (!isset($logs_by_phase[$entry['phase']]))
                $logs_by_phase[$entry['phase']] = array();
            $logs_by_phase[$entry['phase']][] = $entry;
        }

        $ts_next_launch_time = _toTimestamp($this->db_coh['next_launch_date']);

        foreach ($phases as $phase) {

            // Passing hidden phases
            if (in_array($phase['name'], $hidden_phases))
                continue;

            $phase_names[] = $phase_labels[$phase['name']];
            $phase_states[] = _plusIcon($phase['state']);
            if (count($logs_by_phase[$phase['name']]))
                $formatted_logs = array_map('formatLog', $logs_by_phase[$phase['name']]);
            else {

                if ($ts_next_launch_time > mktime() && ($phase['state'] == 'failed' || $phase['state'] == 'ready')) {
                    $last_try_time = _toDate($this->db_coh['next_launch_date']) . sprintf(' (%s)', _T('next attempt', 'msc'));
                    $ts_next_launch_time = 0;
                } else
                    $last_try_time = '';

                $phase_dates[] = $last_try_time;
                $phase_logs[] = '';

                continue;
            }

            $log = '';
            foreach ($formatted_logs as $onetry_log) {
                // info: $onetry_log == array($history, $log_lines)
                $log .= implode('<br/>', $onetry_log[1]) . '<br/>';
            }

            $text = "<h1>" . _T('Step log', 'msc') . "</h1>";
            $text .= '<div style="height:400px;width:100%;overflow-y:scroll;">';
            $text .= nl2br($log);
            $text .= "</div>";
            $f = new NotifyWidget(FALSE);
            $f->add($text, FALSE);


            $divid = $phase['name'] . '_log';
            printf('<div id="%s" style="display:none">%s</div>', $divid, $f->begin() . $f->content() . $f->end());
            $btn_showfull_log[] = sprintf('<ul class="action"><li class="status"><a title="%s" href="#" onclick="PopupWindow(null, \'\', 300, _centerPlacement,jQuery(\'#%s\').html());return false;"></a></li></ul>', _T('Show log', 'msc'), $divid);

            $last_try = $formatted_logs[count($formatted_logs) - 1][1];

            // If next_launch_date is a later time and this step is failed
            if ($ts_next_launch_time > mktime() && ($phase['state'] == 'failed' || $phase['state'] == 'ready')) {
                $last_try_time = _toDate($this->db_coh['next_launch_date']) . sprintf(' (%s)', _T('next attempt', 'msc'));
                $ts_next_launch_time = 0;
            } else
                $last_try_time = $formatted_logs[count($formatted_logs) - 1][0];

            $phase_dates[] = $last_try_time;

            $log_last_lines = '...<br/>';
            $last_lines_number = 3;

            for ($i = $last_lines_number; $i > 0; $i--)
                if (isset($last_try[count($last_try) - ($i + 1)]))
                    $log_last_lines .= $last_try[count($last_try) - ($i + 1)];

            // if log_last_lines didnt change (no previous line),
            // we return exit code
            // else ''
            if ($log_last_lines == '...<br/>')
                if (isset($last_try[count($last_try) - 1]))
                    $log_last_lines = $last_try[count($last_try) - 1];
                else
                    $log_last_lines = '';

            $phase_logs[] = $log_last_lines;
        }


        //$n = new ListInfos(array_map("_names", $values), _T('<b>Command Overview</b>', 'msc'));
        $n = new ListInfos($phase_names, '<b>' . _T('Step', 'msc') . '</b>', '', '80px');
        //$n->addExtraInfo(array_map("_values", $values), '', '400px');
        $n->addExtraInfo($phase_states, 'State', '20px');
        $n->addExtraInfo($phase_dates, 'Execution time', '120px');
        $n->addExtraInfo($phase_logs, 'Details');
        $n->addExtraInfo($btn_showfull_log, '', '20px');
        $n->setTableHeaderPadding(0);
        $n->setRowsPerPage(20);
        $n->drawTable(0);
        print "<br/>";



        ### Display command environment ###
        $values = array(
            array(_T('Reserved bandwidth', 'msc'), $this->db_cmd['maxbw'] == '0' ? _T('<i>none</i>', 'msc') : prettyOctetDisplay($this->db_cmd['maxbw'], 1024, _T('bit/s', 'msc'))),
            array(_T('Proxy mode', 'msc'), $proxy_mode),
            array(_T('Proxy priority', 'msc'), $proxy_priority),
            array(_T('Scheduler', 'msc'), $this->db_coh['scheduler']),
            array(_T('Current launcher', 'msc'), $this->db_coh['launcher'] == '' ? _T('<i>not available</i>', 'msc') : $this->db_coh['launcher']),
            array(_T('Current proxy', 'msc'), $current_proxy),
        );
        $n = new ListInfos(array_map("_names", $values), _T('<b>Command Environment</b>', 'msc'));
        $n->addExtraInfo(array_map("_values", $values), '', '400px');
        $n->setTableHeaderPadding(0);
        $n->setRowsPerPage(count($values));
        $n->drawTable(0);
        print "<br/>";


        # display command history
        # display log files
        $statusTable = getStatusTable();
        $i = 1;
    }

}

function _values($a) {
    return $a[1];
}

function _names($a) {
    return $a[0];
}

function _colorise($line) {
    if (preg_match_all("|^(.*) ([A-Z]): (.*)$|", $line, $matches)) {
        if (strlen($matches[3][0]) == 0)
            return;

        $date = date(_T("Y-m-d H:i:s", "msc"), $matches[1][0]);
        if ($matches[2][0] == "E") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=red face=sans-serif>';
            $out .= $matches[3][0];
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "C") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=navy face=sans-serif>';
            $out .= join(split('·', $matches[3][0]), ' ');
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "T") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=purple face=sans-serif>';
            $out .= join(split('·', $matches[3][0]), ' ');
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "O") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=green face=sans-serif>';
            $out .= $matches[3][0];
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "P") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=teal face=sans-serif>';
            $out .= join(split('·', $matches[3][0]), ' ');
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "W") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=orange face=sans-serif>';
            $out .= join(split('·', $matches[3][0]), ' ');
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "X") {
            $out .= '<font color=black face=sans-serif>' . sprintf(_T("Exit code : %s", "msc"), $matches[3][0]) . '</font>';
        }
    } else {
        $out .= '<font color=black face=sans-serif>' . $line . '</font>';
    }
    return $out;
}

function _toTimestamp($a) {
    $never = array(2031, 12, 31, 23, 59, 59);
    $asap = array(1970, 1, 1, 0, 0, 0);

    if (is_array($a) && (count($a) == 6 || count($a) == 9)) {

        if (count(array_diff(array_slice($a, 0, 6), $never)) == 0)
            return _T('Never', 'msc');

        if (count(array_diff(array_slice($a, 0, 6), $asap)) == 0)
            return _T('As soon as possible', 'msc');

        return mktime($a[3], $a[4], $a[5], $a[1], $a[2], $a[0]);
    } else
        return 0;
}

function _toDate($a, $noneIsAsap = False) {
    $never = array(2031, 12, 31, 23, 59, 59);
    $asap = array(1970, 1, 1, 0, 0, 0);

    if (is_array($a) && (count($a) == 6 || count($a) == 9)) {

        if (count(array_diff(array_slice($a, 0, 6), $never)) == 0)
            return _T('Never', 'msc');

        if (count(array_diff(array_slice($a, 0, 6), $asap)) == 0)
            return _T('As soon as possible', 'msc');

        $parsed_date = mktime($a[3], $a[4], $a[5], $a[1], $a[2], $a[0]);
        return strftime(web_def_date_fmt_msc(), $parsed_date);
    } elseif ($noneIsAsap && !$a) {
        return _T('As soon as possible', 'msc');
    } else { # can't guess if we talk about a date or something else :/
        return _T('<i>undefined</i>', 'msc');
    }
}

function _plusIcon($a) {
    $statusTable = getStatusTable();
    return sprintf('<img title="%s" alt="%s" src="modules/msc/graph/images/status/%s" />', $statusTable[$a], $a, return_icon($a));
}
