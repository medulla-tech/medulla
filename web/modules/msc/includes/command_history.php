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

class CommandOnHost {
    function CommandOnHost($coh) {
        $statusTable = getStatusTable();
        $this->db_coh = get_commands_on_host($coh);
        #$this->db_cmd = command_detail($this->db_coh['fk_commands']);
        $this->values = array(
            array(_T('Host', 'msc'), $this->db_coh['host'], 1),
            array(_T('current_state', 'msc'), $statusTable[$this->db_coh['current_state']], 1),
            array(_T('uploaded', 'msc'), _plusIcon($this->db_coh['uploaded']), 1),
            array(_T('executed', 'msc'), _plusIcon($this->db_coh['executed']), 1),
            array(_T('deleted', 'msc'), _plusIcon($this->db_coh['deleted']), 1)
        );
    }
    function display() {
        $name = array_map("_names", $this->values);
        $value = array_map("_values", $this->values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($this->values));

        $n->drawTable(0);
    }
    function quickDisplay($actions = array(), $params = array()) {
        $statusTable = getStatusTable();
        $n = null;
        $params = array();
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
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
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
        if (!$this->db_bundle) { # use does not have the good permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return false;
        }
        if (!strlen($this->db_bundle[0]['title'])) {
            $this->db_bundle[0]['title'] = "Bundle #".$this->db_bundle[0]['id'];
        }
        $n = new ListInfos(array($this->db_bundle[0]['title']), _T('Bundle', 'msc'));
        $n->addExtraInfo(array(_toDate($this->db_bundle[0]['creation_date'])), _T('Creation date', 'msc'));
        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
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
            array(_T('Command name', 'msc'),$this->db_cmd['title'], 1),
            array(_T('Creation date', 'msc'),_toDate($this->db_cmd['creation_date']), 1),
            array(_T('User command creator', 'msc'),$this->db_cmd['creator'], 0),
            array(_T('Execute file', 'msc'),$this->db_cmd['start_file'], 0),
            array(_T('Execution arguments', 'msc'),$this->db_cmd['parameters'], 0),
            array(_T('Start execute file', 'msc'),$this->db_cmd['start_script'], 0),
            array(_T('Start inventory agent', 'msc'),$this->db_cmd['do_inventory'], 0),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),$this->db_cmd['do_wol'], 0),
            array(_T('Delay between two connections', 'msc'),$this->db_cmd['next_connection_delay'], 0),
            array(_T('Command start date', 'msc'),_toDate($this->db_cmd['start_date']), 0),
            array(_T('Command expiry date', 'msc'),_toDate($this->db_cmd['end_date']), 0),
        );
    }
    function display() {
        if (!$this->db_cmd) { # use does not have the good permissions
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
        return true;
    }
    function quickDisplay($actions = array(), $params = array()) {
        if (!$this->db_cmd) { # use does not have the good permissions
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
        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
        return true;
    }
}

class CommandHistory {
    function CommandHistory($coh_id) {
        // TODO : ch is a list, we have to chose the good one (ie : the most recent date)
        $this->db_ch = get_command_history($coh_id);
        $this->db_coh = get_commands_on_host($coh_id);
        $this->db_cmd = command_detail($this->db_coh['fk_commands']);
    }
    function display() {
        // display parameters
        if (!$this->db_cmd) { # use does not have the good permissions
            $widget = new RenderedMSCCommandDontExists();
            $widget->display();
            return;
        }

        # FIXME: stolen from ajaxLogsFiler.php, should be factorized
        $a_uploaded ='<img style="vertical-align: middle;" alt="'.$this->db_coh['uploaded'].'" src="modules/msc/graph/images/status/'.return_icon($this->db_coh['uploaded']).'"/> ';
        $a_executed ='<img style="vertical-align: middle;" alt="'.$this->db_coh['executed'].'" src="modules/msc/graph/images/status/'.return_icon($this->db_coh['executed']).'"/> ';
        $a_deleted = '<img style="vertical-align: middle;" alt="'.$this->db_coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon($this->db_coh['deleted']).'"/> ';

        $state = $a_uploaded . $a_executed . $a_deleted;

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


        if ($this->db_cmd['start_file'])
            if ($this->db_cmd['parameters'])
                $command_line = sprintf(_T('%s %s', 'msc'), $this->db_cmd['start_file'], $this->db_cmd['parameters']);
            else
                $command_line = sprintf(_T('%s <i>(no additionnal parameter given)</i>', 'msc'), $this->db_cmd['start_file']);
        else
            $command_line = _T('<i>not set</i>', 'msc');

        // gettext obfucation
        _T('enable', 'msc');
        _T('disable', 'msc');
        $static_values = array(
            array(_T('Command state', 'msc'),                                   $state),
            array('',                                                           ''),
            array(_T('Command name', 'msc'),                                    $this->db_cmd['title']),
            array(_T('Creation', 'msc'),                                        sprintf(_T('<i>on</i> %s <i>by</i> %s', 'msc'), _toDate($this->db_cmd['creation_date']),$this->db_cmd['creator'])),
            array(_T('Validity period', 'msc'),                                 $validity),
            array(_T('Deployment interval', 'msc'),                             $deploy_interv),
            array(_T('Command line to run', 'msc'),                             $command_line),
            array('',                                                           ''),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),   _T($this->db_cmd['do_wol'], 'msc')),
            array(_T('Execute command line ?', 'msc'),                          _T($this->db_cmd['start_script'], 'msc')),
            array(_T('Delete files after a successful execution ?', 'msc'),     _T($this->db_cmd['clean_on_success'], 'msc')),
            array(_T('Do an inventory after a successful execution ?', 'msc'),  _T($this->db_cmd['do_inventory'], 'msc')),
            array(_T('Reboot client after a successful deletion ?', 'msc'),     _T($this->db_cmd['do_reboot'], 'msc')),
            array('',                                                           ''),
            array(_T('Remaining connection attempts', 'msc'),                   $this->db_coh['attempts_left']),
            array(_T('Delay between two attempts (minutes)', 'msc'),             $this->db_cmd['next_connection_delay'] ? $this->db_cmd['next_connection_delay'] : _T('<i>not set</i>', 'msc')),
            array(_T('Next attempt', 'msc'),                                    $next_launch_date),
        );

        $static_name = array_map("_names", $static_values);
        $static_value = array_map("_values", $static_values);

        $n = new ListInfos($static_name, _T('Name', 'msc'));
        $n->addExtraInfo($static_value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($static_values));
        $n->setTableHeaderPadding(1);
        $n->drawTable(0);

        // display files
        $files = array(_T('Transferred files list empty.', 'msc'));
        if ($this->db_cmd["files"]!="" && $this->db_cmd["files"]!=array()) {
            if (gettype($command["files"]) != 'array') {
                $files = explode("\n", $this->db_cmd["files"]);
            } else {
                $files = $this->db_cmd["files"];
            }
        }
        $n = new ListInfos($files, _T('Transferred files list', 'msc'));
        $n->setRowsPerPage(count($files) +1);
        $n->setTableHeaderPadding(1);
        print "<hr/><br/>";
        $n->drawTable(0);
        print "<hr/><br/>";

        # display command history
        # display log files
        $statusTable = getStatusTable();
        foreach ($this->db_ch as $hist) {
            $history = '<img style="vertical-align: middle;" alt="'.$hist['state'].'" src="modules/msc/graph/images/status/'.history_stat2icon($hist['state']).'"/> '.date("Y-m-d H:i:s", $hist['date']).': <b>'.$statusTable[$hist['state']].'</b>';
            if (gettype($hist["stdout"]) != 'array')
                $hist["stdout"] = split("\n", $hist["stdout"]);
            if (gettype($hist["stderr"]) != 'array')
                $hist["stderr"] = split("\n", $hist["stderr"]);
            if (count($hist["stdout"]) > 0 &&
                !(count($hist["stdout"]) == 1 && $hist["stdout"][0] == '')
               ) {
                   $hist["stderr"] = array_merge($hist["stderr"], $hist["stdout"]);
            }
            $raw_errors = array_map('_colorise', array_filter($hist["stderr"]));
            $purge_errors = array();

            foreach ($raw_errors as $error)
                if (isset($error))
                    array_push($purge_errors, $error);

            $n = new ListInfos($purge_errors, $history);

            $n->setTableHeaderPadding(1);
            $n->setRowsPerPage(999); // FIXME: Ugly, should try to find another way to do this
            if (count($hist["stderr"]) > 0  &&
                !(count($hist["stderr"]) == 1 && $hist["stderr"][0] == '')
               ) {
                $n->drawTable(0);
            }
        }
    }
}
function _values($a) { return $a[1]; }
function _names($a) { return $a[0]; }
function _colorise($line) {
    if (preg_match_all("|^(.*) ([ECOXTP]):(.*)$|", $line, $matches)) {
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
        } elseif ($matches[2][0] == "X") {
            $out .= '<font color=black face=sans-serif>' . sprintf(_T("Exit code was: %s", "msc"), $matches[3][0]) . '</font>';
        }
    } else {
        $out .= '<font color=black face=sans-serif>' . $line . '</font>';
    }
    return $out;
}

function _toDate($a) {
    $never = array(2031, 12, 31, 23, 59, 59);
    $asap = array(1970, 1, 1, 0, 0, 0);

    if (is_array($a) && (count($a) == 6 || count($a) == 9)) {

        if (count(array_diff(array_slice($a, 0, 6), $never)) == 0)
            return _T('Never', 'msc');

        if (count(array_diff(array_slice($a, 0, 6), $asap)) == 0)
            return _T('As soon as possible', 'msc');

        return sprintf(_T('%04d/%02d/%02d %02d:%02d:%02d', 'msc'), $a[0], $a[1], $a[2], $a[3], $a[4], $a[5]);

    } else { # can't guess if we talk about a date or something else :/
        return $a;
    }
}

function _plusIcon($a) {
    $statusTable = getStatusTable();
    return '<img alt="'.$a.'" src="modules/msc/graph/images/status/'.return_icon($a).'"/> ' . $statusTable[$a];
}
