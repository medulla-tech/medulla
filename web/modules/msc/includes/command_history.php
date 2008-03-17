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
class Command {
    function Command($cmd) {
        $this->db_cmd = command_detail($cmd);
        $this->values = array(
            array(_T('Command name', 'msc'),$this->db_cmd['title'], 1),
            array(_T('Creation date', 'msc'),_toDate($this->db_cmd['date_created']), 1),
            array(_T('User command creator', 'msc'),$this->db_cmd['webmin_username'], 0),
            array(_T('Execute file', 'msc'),$this->db_cmd['start_file'], 0),
            array(_T('Execution arguments', 'msc'),$this->db_cmd['parameters'], 0),
            array(_T('Start execute file', 'msc'),$this->db_cmd['start_script'], 0),
            array(_T('Start inventory agent', 'msc'),$this->db_cmd['start_inventory'], 0),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),$this->db_cmd['wake_on_lan'], 0),
            array(_T('Delay between two connections', 'msc'),$this->db_cmd['next_connection_delay'], 0),
            array(_T('Command start date', 'msc'),_toDate($this->db_cmd['start_date']), 0),
            array(_T('Command expiry date', 'msc'),_toDate($this->db_cmd['end_date']), 0),
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
        $values = array(
            array(_T('Command name', 'msc'),$this->db_cmd['title']),
            array(_T('Creation date', 'msc'),_toDate($this->db_cmd['date_created'])),
            array(_T('User command creator', 'msc'),$this->db_cmd['webmin_username']),
            array(_T('Execute file', 'msc'),$this->db_cmd['start_file']),
            array(_T('Execution arguments', 'msc'),$this->db_cmd['parameters']),
            array(_T('Start execute file', 'msc'),$this->db_cmd['start_script']),
            array(_T('Start inventory agent', 'msc'),$this->db_cmd['start_inventory']),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),$this->db_cmd['wake_on_lan']),
            array(_T('Remaining attempts', 'msc'),$this->db_coh['number_attempt_connection_remains']),
            array(_T('Delay between two connections', 'msc'),$this->db_cmd['next_connection_delay']),
            array(_T('Command start date', 'msc'),_toDate($this->db_cmd['start_date'])),
            array(_T('Command expiry date', 'msc'),_toDate($this->db_cmd['end_date'])),
            array(_T('Command next run date', 'msc'),_toDate($this->db_coh['next_launch_date']))
        );

        $name = array_map("_names", $values);
        $value = array_map("_values", $values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($values));
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
        $n->setTableHeaderPadding(1);
        print "<hr/><br/>";
        $n->drawTable(0);

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
            $raw_errors = array_map('_colorise', $hist["stderr"]);
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
    if (preg_match_all("|^(.*) ([ECOX]): (.*)$|", $line, $matches)) {
        if (strlen($matches[3][0]) == 0)
            return;

        $date = date(_T("Y-m-d H:i:s", "msc"), $matches[1][0]);
        if ($matches[2][0] == "E") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=red>';
            $out .= $matches[3][0];
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "C") {
            $split = split('·', $matches[3][0]);
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=blue>';
            $out .= $split[count($split)-1];
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "O") {
            $out .= '<font color=grey>' . $date . '</font>&nbsp;';
            $out .= '<font color=green>';
            $out .= $matches[3][0];
            $out .= '</font><br/>';
        } elseif ($matches[2][0] == "X") {
            $out .= '<font color=black>' . sprintf(_T("Exit code was: %s", "msc"), $matches[3][0]) . '</font>';
        }
    } else $out .=  "<font>$line</font>\n";
    return $out;
}
function _toDate($a) {
    if (is_array($a) && count($a) == 6) {
        return $a[0]."/".$a[1].'/'.$a[2]." ".$a[3].":".$a[4].":".$a[5];
    } elseif (is_array($a) && count($a) == 9) {
        return $a[0]."/".$a[1].'/'.$a[2]." ".$a[3].":".$a[4].":".$a[5];
    } else {
        return $a;
    }
}
function _plusIcon($a) {
    return '<img alt="'.$a.'" src="modules/msc/graph/images/status/'.return_icon($a).'"/> '.$a;
}
